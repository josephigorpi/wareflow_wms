"""Formatos de fechas y moneda para WareFlow WMS."""

from datetime import datetime


def format_date(date_str: str) -> str:
    try:
        return datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
    except Exception:
        return date_str or ""
