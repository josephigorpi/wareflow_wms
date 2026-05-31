"""Lógica de negocio de movimientos de inventario para WareFlow WMS."""

from database.connection import get_connection


def get_recent_movements(limit: int = 50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movimientos ORDER BY fecha_movimiento DESC LIMIT ?", (limit,))
    return cursor.fetchall()
