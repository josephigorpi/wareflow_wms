"""Validaciones genéricas para WareFlow WMS."""


def validate_not_empty(value) -> bool:
    return value is not None and str(value).strip() != ""
