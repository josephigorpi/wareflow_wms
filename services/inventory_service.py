"""Lógica de negocio de inventario para WareFlow WMS."""

from database.connection import get_connection
from datetime import datetime


def get_all_inventory():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.sku, p.nombre as producto_nombre, u.codigo as ubicacion_codigo, z.nombre as zona_nombre
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE p.activo = 1 AND u.activo = 1
        ORDER BY p.nombre, u.codigo
    """)
    return cursor.fetchall()


def get_inventory_by_product(product_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.sku, p.nombre as producto_nombre, u.codigo as ubicacion_codigo, z.nombre as zona_nombre
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE i.producto_id = ? AND p.activo = 1 AND u.activo = 1
        ORDER BY u.codigo
    """, (product_id,))
    return cursor.fetchall()


def get_inventory_by_location(location_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.sku, p.nombre as producto_nombre, u.codigo as ubicacion_codigo, z.nombre as zona_nombre
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE i.ubicacion_id = ? AND p.activo = 1 AND u.activo = 1
        ORDER BY p.nombre
    """, (location_id,))
    return cursor.fetchall()


def update_inventory(inventory_id: int, cantidad: int, usuario_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE inventario 
        SET cantidad = ?, actualizado_en = ?, actualizado_por = ?
        WHERE id = ?
    """, (cantidad, now, usuario_id, inventory_id))
    conn.commit()
    return True


def get_inventory_by_id(inventory_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.sku, p.nombre as producto_nombre, u.codigo as ubicacion_codigo
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        WHERE i.id = ?
    """, (inventory_id,))
    return cursor.fetchone()
