"""Lógica de negocio de productos para WareFlow WMS."""

from database.connection import get_connection
from datetime import datetime


def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE activo = 1")
    return cursor.fetchall()


def get_products_with_inventory():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, COALESCE(SUM(i.cantidad), 0) as stock_total
        FROM productos p
        LEFT JOIN inventario i ON p.id = i.producto_id
        WHERE p.activo = 1
        GROUP BY p.id
    """)
    return cursor.fetchall()


def get_products_low_stock():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, COALESCE(SUM(i.cantidad), 0) as stock_total
        FROM productos p
        LEFT JOIN inventario i ON p.id = i.producto_id
        WHERE p.activo = 1
        GROUP BY p.id
        HAVING stock_total <= p.stock_minimo
    """)
    return cursor.fetchall()


def count_active_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
    return cursor.fetchone()[0]


def search_products(query: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, COALESCE(SUM(i.cantidad), 0) as stock_total
        FROM productos p
        LEFT JOIN inventario i ON p.id = i.producto_id
        WHERE p.activo = 1 AND (p.sku LIKE ? OR p.nombre LIKE ?)
        GROUP BY p.id
    """, (f"%{query}%", f"%{query}%"))
    return cursor.fetchall()
