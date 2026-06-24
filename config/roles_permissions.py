"""Mapeo de roles y permisos para el sistema WareFlow WMS."""

ROLES_PERMISSIONS = {
    "Administrador": {
        "dashboard": ["leer", "escribir"],
        "recepcion": ["leer", "escribir"],
        "inventario": ["leer", "escribir"],
        "ubicacion": ["leer", "escribir"],
        "picking": ["leer", "escribir"],
        "despacho": ["leer", "escribir"],
        "reportes": ["leer", "escribir"],
        "admin": ["leer", "escribir"],
    },
    "Supervisor": {
        "dashboard": ["leer"],
        "recepcion": ["leer", "escribir"],
        "inventario": ["leer", "escribir"],
        "ubicacion": ["leer", "escribir"],
        "picking": ["leer", "escribir"],
        "despacho": ["leer", "escribir"],
        "reportes": ["leer"],
    },
    "Operador Almacén": {
        "dashboard": ["leer"],
        "recepcion": ["leer", "escribir"],
        "inventario": ["leer", "escribir"],
        "ubicacion": ["leer", "escribir"],
        "picking": ["leer", "escribir"],
        "despacho": ["leer", "escribir"],
    },
    "Auditor": {
        "dashboard": ["leer"],
        "inventario": ["leer"],
        "reportes": ["leer"],
    },
}
