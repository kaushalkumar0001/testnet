"""Order placement and result formatting."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from .client import BinanceClient, BinanceClientError
from .logging_config import logger
from .validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)


class OrderResult:
    """Parsed, human-friendly representation of a Binance order response."""

    def __init__(self, raw: dict[str, Any]):
        self.raw = raw
        self.order_id: int = raw.get("orderId", 0)
        self.symbol: str = raw.get("symbol", "")
        self.side: str = raw.get("side", "")
        self.order_type: str = raw.get("type", "")
        self.status: str = raw.get("status", "")
        self.orig_qty: str = raw.get("origQty", "0")
        self.executed_qty: str = raw.get("executedQty", "0")
        self.avg_price: str = raw.get("avgPrice", "0") or raw.get("price", "0")
        self.price: str = raw.get("price", "0")
        self.stop_price: str = raw.get("stopPrice", "0")
        self.time_in_force: str = raw.get("timeInForce", "")
        self.update_time: int = raw.get("updateTime", 0)

    def __str__(self) -> str:
        lines = [
            "",
            "┌─────────────────────────────────────────────",
            f"│  Order ID      : {self.order_id}",
            f"│  Symbol        : {self.symbol}",
            f"│  Side          : {self.side}",
            f"│  Type          : {self.order_type}",
            f"│  Status        : {self.status}",
            f"│  Orig Qty      : {self.orig_qty}",
            f"│  Executed Qty  : {self.executed_qty}",
        ]
        if self.avg_price and self.avg_price != "0":
            lines.append(f"│  Avg Price     : {self.avg_price}")
        if self.order_type == "LIMIT" and self.price and self.price != "0":
            lines.append(f"│  Limit Price   : {self.price}")
        if self.stop_price and self.stop_price != "0":
            lines.append(f"│  Stop Price    : {self.stop_price}")
        if self.time_in_force:
            lines.append(f"│  Time In Force : {self.time_in_force}")
        lines.append("└─────────────────────────────────────────────")
        return "\n".join(lines)


class OrderManager:
    """High-level order management layer; validates inputs then calls the client."""

    def __init__(self, client: BinanceClient):
        self.client = client

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str | float,
        price: str | float | None = None,
        stop_price: str | float | None = None,
        time_in_force: str = "GTC",
    ) -> OrderResult:
        """Validate inputs and place an order, returning an OrderResult.

        Raises:
            ValueError: on invalid user input.
            BinanceClientError: on API-level errors.
            ConnectionError / TimeoutError: on network failures.
        """
        # --- Validate ---
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        order_type = validate_order_type(order_type)
        qty_dec: Decimal = validate_quantity(quantity)
        price_dec: Decimal | None = validate_price(price, order_type)
        stop_price_dec: Decimal | None = validate_stop_price(stop_price, order_type)

        logger.debug(
            "Validated inputs: symbol=%s side=%s type=%s qty=%s price=%s stopPrice=%s",
            symbol, side, order_type, qty_dec, price_dec, stop_price_dec,
        )

        # --- Place ---
        raw = self.client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=str(qty_dec),
            price=str(price_dec) if price_dec else None,
            stop_price=str(stop_price_dec) if stop_price_dec else None,
            time_in_force=time_in_force,
        )

        return OrderResult(raw)
