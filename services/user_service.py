"""Lógica de negocio de usuarios para WareFlow WMS."""

from database.connection import get_connection


def get_user_by_username(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT u.*, r.nombre AS rol_nombre FROM usuarios u LEFT JOIN roles r ON u.rol_id = r.id WHERE u.username = ?",
        (username,),
    )
    row = cursor.fetchone()
    # Convertir sqlite3.Row a diccionario
    if row:
        return dict(row)
    return None
