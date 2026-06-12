"""Low-level Binance Futures Testnet REST client."""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests

from .logging_config import logger

BASE_URL = "https://testnet.binancefuture.com"
TIMEOUT = 10  # seconds


class BinanceClientError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"Binance API error {code}: {msg}")


class BinanceClient:
    """Thin wrapper around the Binance Futures Testnet REST API."""

    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.debug("BinanceClient initialised. base_url=%s", self.base_url)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, endpoint: str, signed: bool = False, **kwargs) -> Any:
        url = f"{self.base_url}{endpoint}"
        params = kwargs.pop("params", {})
        data = kwargs.pop("data", {})

        if signed:
            payload = {**params, **data}
            payload = self._sign(payload)
            if method.upper() == "GET":
                params = payload
            else:
                data = payload

        logger.debug(
            "API REQUEST  method=%s url=%s params=%s data=%s",
            method.upper(),
            url,
            params,
            {k: v for k, v in data.items() if k != "signature"},
        )

        try:
            resp = self._session.request(
                method, url, params=params, data=data, timeout=TIMEOUT, **kwargs
            )
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error reaching %s: %s", url, exc)
            raise ConnectionError(f"Could not connect to Binance API: {exc}") from exc
        except requests.exceptions.Timeout:
            logger.error("Request to %s timed out after %ss", url, TIMEOUT)
            raise TimeoutError(f"Request to {url} timed out.") from None

        logger.debug(
            "API RESPONSE status=%s body=%s", resp.status_code, resp.text[:500]
        )

        try:
            body = resp.json()
        except ValueError:
            logger.error("Non-JSON response from %s: %s", url, resp.text[:200])
            raise BinanceClientError(-1, f"Unexpected non-JSON response: {resp.text[:200]}")

        if isinstance(body, dict) and "code" in body and body["code"] != 200:
            err_code = body.get("code", -1)
            err_msg = body.get("msg", "Unknown error")
            logger.error("Binance error code=%s msg=%s", err_code, err_msg)
            raise BinanceClientError(err_code, err_msg)

        return body

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_exchange_info(self) -> dict:
        """Fetch exchange info (rate limits, symbols, etc.)."""
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def get_account(self) -> dict:
        """Fetch account balances and positions."""
        return self._request("GET", "/fapi/v2/account", signed=True)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None = None,
        stop_price: str | None = None,
        time_in_force: str = "GTC",
    ) -> dict:
        """Place a new order on Binance Futures Testnet.

        Args:
            symbol:        Trading pair, e.g. 'BTCUSDT'
            side:          'BUY' or 'SELL'
            order_type:    'MARKET', 'LIMIT', or 'STOP_MARKET'
            quantity:      Order quantity as a string
            price:         Limit price (required for LIMIT orders)
            stop_price:    Stop trigger price (required for STOP_MARKET)
            time_in_force: 'GTC' | 'IOC' | 'FOK' (ignored for MARKET)

        Returns:
            Raw Binance order response dict.
        """
        payload: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            payload["price"] = price
            payload["timeInForce"] = time_in_force
        elif order_type == "STOP_MARKET":
            payload["stopPrice"] = stop_price

        logger.info(
            "Placing order: symbol=%s side=%s type=%s qty=%s price=%s stopPrice=%s",
            symbol,
            side,
            order_type,
            quantity,
            price,
            stop_price,
        )

        response = self._request("POST", "/fapi/v1/order", signed=True, data=payload)
        logger.info("Order placed successfully: %s", response)
        return response
