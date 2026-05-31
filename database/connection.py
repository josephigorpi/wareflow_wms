"""Gestor de conexión SQLite para WareFlow WMS."""

import sqlite3
from pathlib import Path

from config.settings import DB_PATH

"""_CONNECTION = None"""


def get_connection():
    """global _CONNECTION
    if _CONNECTION is None:
        db_file = Path(DB_PATH)
        _CONNECTION = sqlite3.connect(db_file)
        _CONNECTION.row_factory = sqlite3.Row"""

    """Crea una nueva conexión SQLite sin reutilizar la anterior."""
    db_file = Path(DB_PATH)
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return _CONNECTION
