"""
Display formatting utilities for cfo-copilot.

This module contains functions for formatting numbers, currency, percentages,
and other display values in both English and Polish formats.
"""

from typing import Optional


def scale_for_display(x: Optional[float], unit_mode: str) -> Optional[float]:
    """
    Scale a value for display based on unit mode.

    Args:
        x: Value in PLN
        unit_mode: Display unit ("m PLN", "k PLN", or "PLN")

    Returns:
        Scaled value or None if input is None
    """
    if x is None:
        return None

    if unit_mode == "m PLN":
        return x / 1_000_000
    elif unit_mode == "k PLN":
        return x / 1_000
    else:
        return x


def unit_suffix(unit_mode: str) -> str:
    """
    Get the display suffix for a unit mode.

    Args:
        unit_mode: Unit mode string

    Returns:
        Display suffix (e.g., "m PLN", "k PLN", "PLN")
    """
    if unit_mode == "m PLN":
        return "m PLN"
    elif unit_mode == "k PLN":
        return "k PLN"
    else:
        return "PLN"


def pl_number_str(x: Optional[float], unit_mode: str) -> str:
    """
    Format number in Polish style with space as thousands separator.

    Polish format: 1 234 567,8 (space for thousands, comma for decimal)

    Args:
        x: Number to format
        unit_mode: Unit mode (unused, kept for API compatibility)

    Returns:
        Formatted string or "—" if None
    """
    if x is None:
        return "—"

    # Python's format with comma as thousands separator: 1,234.5
    # Then swap: comma -> X, dot -> comma, X -> space
    return f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", " ")


def money_fmt(x: Optional[float], unit_mode: str) -> str:
    """
    Format a monetary value with appropriate unit suffix.

    Args:
        x: Value in PLN
        unit_mode: Display unit ("m PLN", "k PLN", or "PLN")

    Returns:
        Formatted string like "1 234,5 m PLN" or "—" if None
    """
    if x is None:
        return "—"

    scaled = scale_for_display(x, unit_mode)
    return f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}"


def pct_fmt(x: Optional[float]) -> str:
    """
    Format a decimal ratio as percentage.

    Args:
        x: Decimal ratio (e.g., 0.15 for 15%)

    Returns:
        Formatted string like "15.0%" or "—" if None
    """
    if x is None:
        return "—"

    return f"{x * 100:.1f}%"


def pp_fmt(x: Optional[float]) -> str:
    """
    Format a value in percentage points (pp).

    Args:
        x: Value in percentage points

    Returns:
        Formatted string like "2.5 pp" or "—" if None
    """
    if x is None:
        return "—"

    return f"{x:.1f} pp"


def neg_red(val) -> str:
    """
    Return CSS style string for negative numbers (red and bold).

    Used with pandas DataFrame.style.applymap() to highlight negative values.

    Args:
        val: Cell value

    Returns:
        CSS style string or empty string
    """
    try:
        if val is not None and float(val) < 0:
            return "color: #C62828; font-weight: 700;"
    except (ValueError, TypeError):
        pass

    return ""
