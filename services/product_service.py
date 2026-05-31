"""Lógica de negocio de productos para WareFlow WMS."""

from database.connection import get_connection


def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE activo = 1")
    return cursor.fetchall()
