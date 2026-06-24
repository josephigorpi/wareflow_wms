"""Lógica de negocio de movimientos de inventario para WareFlow WMS."""

from database.connection import get_connection
from datetime import datetime


def get_recent_movements(limit: int = 50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.*, p.sku, p.nombre as producto_nombre, u.username as usuario_nombre
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.fecha_movimiento DESC LIMIT ?
    """, (limit,))
    return cursor.fetchall()


def get_movements_with_details():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.*, p.sku, p.nombre as producto_nombre, u.username as usuario_nombre
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.fecha_movimiento DESC
    """)
    return cursor.fetchall()


def count_movements_by_type_today():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM movimientos 
        WHERE tipo = 'ENTRADA' AND DATE(fecha_movimiento) = ?
    """, (today,))
    entradas = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*) FROM movimientos 
        WHERE tipo = 'SALIDA' AND DATE(fecha_movimiento) = ?
    """, (today,))
    salidas = cursor.fetchone()[0]
    return {"entradas": entradas, "salidas": salidas}


def get_movements_by_date_range(start_date: str, end_date: str, tipo: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.*, p.sku, p.nombre as producto_nombre, u.username as usuario_nombre
        FROM movimientos m
        LEFT JOIN productos p ON m.producto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        WHERE DATE(m.fecha_movimiento) BETWEEN ? AND ?
    """
    params = [start_date, end_date]
    if tipo:
        query += " AND m.tipo = ?"
        params.append(tipo)
    query += " ORDER BY m.fecha_movimiento DESC"
    cursor.execute(query, params)
    return cursor.fetchall()


def get_movements_grouped_by_day(start_date: str, end_date: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            DATE(fecha_movimiento) as fecha,
            tipo,
            COUNT(*) as cantidad
        FROM movimientos
        WHERE DATE(fecha_movimiento) BETWEEN ? AND ?
        GROUP BY DATE(fecha_movimiento), tipo
        ORDER BY fecha
    """, (start_date, end_date))
    return cursor.fetchall()
