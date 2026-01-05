from __future__ import annotations


def format_number(value, decimals: int = 1) -> str:
    """
    Format:
      - space as thousands separator
      - dot as decimal separator
    """
    try:
        fmt = f"{{:,.{decimals}f}}"
        s = fmt.format(float(value))
        return s.replace(",", " ")
    except Exception:
        return ""
