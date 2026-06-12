#!/usr/bin/env python3
"""CLI entry point for the Binance Futures Testnet Trading Bot."""
from __future__ import annotations

import argparse
import os
import sys
import textwrap

from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import logger
from bot.orders import OrderManager

load_dotenv()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _print_request_summary(args: argparse.Namespace) -> None:
    print("\n╔══════════════════════════════════════════════════")
    print("║  ORDER REQUEST SUMMARY")
    print("╠══════════════════════════════════════════════════")
    print(f"║  Symbol     : {args.symbol.upper()}")
    print(f"║  Side       : {args.side.upper()}")
    print(f"║  Type       : {args.order_type.upper()}")
    print(f"║  Quantity   : {args.quantity}")
    if args.price:
        print(f"║  Price      : {args.price}")
    if getattr(args, "stop_price", None):
        print(f"║  Stop Price : {args.stop_price}")
    print("╚══════════════════════════════════════════════════\n")


def _get_credentials() -> tuple[str, str]:
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print(
            "\n[ERROR] API credentials not found.\n"
            "Set BINANCE_API_KEY and BINANCE_API_SECRET in a .env file or as environment variables.\n"
            "See README.md for setup instructions.\n"
        )
        logger.error("Missing API credentials. Exiting.")
        sys.exit(1)

    return api_key, api_secret


# ──────────────────────────────────────────────────────────────────────────────
# Argument parser
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            Binance Futures Testnet Trading Bot
            ────────────────────────────────────
            Place MARKET, LIMIT, or STOP_MARKET orders on the USDT-M testnet.
            """
        ),
        epilog=textwrap.dedent(
            """\
            Examples:
              # Market BUY
              python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

              # Limit SELL
              python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3500

              # Stop-Market BUY (bonus order type)
              python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 65000
            """
        ),
    )

    parser.add_argument(
        "--symbol",
        required=True,
        metavar="SYMBOL",
        help="Trading pair symbol (e.g. BTCUSDT, ETHUSDT)",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        metavar="SIDE",
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET", "market", "limit", "stop_market"],
        metavar="TYPE",
        help="Order type: MARKET | LIMIT | STOP_MARKET",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        type=float,
        metavar="QTY",
        help="Order quantity (e.g. 0.001 for BTC)",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        metavar="PRICE",
        help="Limit price (required for LIMIT orders)",
    )
    parser.add_argument(
        "--stop-price",
        dest="stop_price",
        type=float,
        default=None,
        metavar="STOP_PRICE",
        help="Stop trigger price (required for STOP_MARKET orders)",
    )
    parser.add_argument(
        "--tif",
        dest="time_in_force",
        default="GTC",
        choices=["GTC", "IOC", "FOK"],
        metavar="TIF",
        help="Time-in-force for LIMIT orders: GTC (default) | IOC | FOK",
    )
    parser.add_argument(
        "--testnet-url",
        default="https://testnet.binancefuture.com",
        metavar="URL",
        help="Override the testnet base URL (default: https://testnet.binancefuture.com)",
    )

    return parser


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    _print_request_summary(args)

    api_key, api_secret = _get_credentials()

    client = BinanceClient(api_key=api_key, api_secret=api_secret, base_url=args.testnet_url)
    manager = OrderManager(client=client)

    try:
        result = manager.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
            time_in_force=args.time_in_force,
        )
        print(result)
        print("\n✅  Order placed successfully!\n")
        logger.info("CLI completed successfully. orderId=%s", result.order_id)

    except ValueError as exc:
        print(f"\n❌  Validation error: {exc}\n")
        logger.error("Validation error: %s", exc)
        sys.exit(2)

    except BinanceClientError as exc:
        print(f"\n❌  Binance API error [{exc.code}]: {exc.msg}\n")
        logger.error("BinanceClientError code=%s msg=%s", exc.code, exc.msg)
        sys.exit(3)

    except (ConnectionError, TimeoutError) as exc:
        print(f"\n❌  Network error: {exc}\n")
        logger.error("Network error: %s", exc)
        sys.exit(4)

    except Exception as exc:
        print(f"\n❌  Unexpected error: {exc}\n")
        logger.exception("Unexpected error: %s", exc)
        sys.exit(5)


if __name__ == "__main__":
    main()
