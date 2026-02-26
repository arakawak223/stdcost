"""Japanese locale helpers for formatting."""

from datetime import date, datetime
from decimal import Decimal


def format_currency(amount: Decimal | float | int, include_yen: bool = True) -> str:
    """Format amount as Japanese yen (e.g., ¥1,234,567)."""
    formatted = f"{amount:,.0f}" if isinstance(amount, (int, float)) else f"{float(amount):,.0f}"
    return f"¥{formatted}" if include_yen else formatted


def format_jp_date(d: date | datetime) -> str:
    """Format date in Japanese style (e.g., 2026年2月26日)."""
    return f"{d.year}年{d.month}月{d.day}日"


def format_fiscal_period(year: int, month: int) -> str:
    """Format fiscal period (e.g., 2026年2月度)."""
    return f"{year}年{month}月度"


def format_percent(value: Decimal | float, decimal_places: int = 1) -> str:
    """Format as percentage (e.g., 12.3%)."""
    return f"{float(value):.{decimal_places}f}%"
