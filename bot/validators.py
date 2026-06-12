"""Validation helpers for CLI inputs."""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}

# Symbols must be uppercase letters only, 2-20 chars
_SYMBOL_RE = re.compile(r"^[A-Z]{2,20}$")


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not _SYMBOL_RE.match(s):
        raise ValueError(
            f"Invalid symbol '{symbol}'. Must be uppercase letters only (e.g. BTCUSDT)."
        )
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}.")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    return t


def validate_quantity(quantity: str | float) -> Decimal:
    try:
        q = Decimal(str(quantity))
    except InvalidOperation:
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if q <= 0:
        raise ValueError(f"Quantity must be greater than 0, got {quantity}.")
    return q


def validate_price(price: str | float | None, order_type: str) -> Decimal | None:
    if order_type in ("LIMIT", "STOP_MARKET") and price is None:
        raise ValueError(f"Price is required for {order_type} orders.")
    if price is None:
        return None
    try:
        p = Decimal(str(price))
    except InvalidOperation:
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValueError(f"Price must be greater than 0, got {price}.")
    return p


def validate_stop_price(stop_price: str | float | None, order_type: str) -> Decimal | None:
    if order_type == "STOP_MARKET" and stop_price is None:
        raise ValueError("Stop price is required for STOP_MARKET orders.")
    if stop_price is None:
        return None
    try:
        sp = Decimal(str(stop_price))
    except InvalidOperation:
        raise ValueError(f"Invalid stop price '{stop_price}'. Must be a positive number.")
    if sp <= 0:
        raise ValueError(f"Stop price must be greater than 0, got {stop_price}.")
    return sp
