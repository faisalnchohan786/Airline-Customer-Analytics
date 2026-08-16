"""Formatting helpers for dashboard presentation."""

def compact_number(value: float | int) -> str:
    value = float(value)
    magnitude = abs(value)
    if magnitude >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if magnitude >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if magnitude >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def money(value: float | int, compact: bool = False) -> str:
    if compact:
        return f"{compact_number(value)}"
    return f"{float(value):,.0f}"


def percent(value: float | int) -> str:
    return f"{float(value):.1f}%"
