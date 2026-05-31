"""Lógica de negocio de ubicaciones para WareFlow WMS."""

from database.connection import get_connection


def get_all_locations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ubicaciones WHERE activo = 1")
    return cursor.fetchall()
