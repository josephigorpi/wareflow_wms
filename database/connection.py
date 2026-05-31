"""Gestor de conexión SQLite para WareFlow WMS."""

import sqlite3
from pathlib import Path

from config.settings import DB_PATH


def get_connection():
    """Crea una nueva conexión SQLite sin reutilizar la anterior."""
    db_file = Path(DB_PATH)
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection
