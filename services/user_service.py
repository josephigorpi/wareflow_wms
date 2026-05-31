"""Lógica de negocio de usuarios para WareFlow WMS."""

from database.connection import get_connection


def get_user_by_username(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT u.*, r.nombre AS rol_nombre FROM usuarios u LEFT JOIN roles r ON u.rol_id = r.id WHERE u.username = ?",
        (username,),
    )
    return cursor.fetchone()
