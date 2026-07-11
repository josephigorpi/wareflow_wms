"""Lógica de negocio de inventario para WareFlow WMS."""

from database.connection import get_connection
from datetime import datetime


def get_all_inventory():
    """Obtiene todo el inventario con detalles de producto, ubicación y zona."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.producto_id, i.ubicacion_id, i.cantidad, i.lote, 
               i.fecha_vencimiento, i.actualizado_en, i.actualizado_por,
               p.sku, p.nombre as producto_nombre, 
               u.codigo as ubicacion_codigo, 
               z.nombre as zona_nombre
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE p.activo = 1 AND u.activo = 1
        ORDER BY p.nombre, u.codigo
    """)
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_inventory_by_product(product_id: int):
    """Obtiene inventario filtrado por producto."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.producto_id, i.ubicacion_id, i.cantidad, i.lote, 
               i.fecha_vencimiento, i.actualizado_en, i.actualizado_por,
               p.sku, p.nombre as producto_nombre, 
               u.codigo as ubicacion_codigo, 
               z.nombre as zona_nombre
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE i.producto_id = ? AND p.activo = 1 AND u.activo = 1
        ORDER BY u.codigo
    """, (product_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_inventory_by_location(location_id: int):
    """Obtiene inventario filtrado por ubicación."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.producto_id, i.ubicacion_id, i.cantidad, i.lote, 
               i.fecha_vencimiento, i.actualizado_en, i.actualizado_por,
               p.sku, p.nombre as producto_nombre, 
               u.codigo as ubicacion_codigo, 
               z.nombre as zona_nombre
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE i.ubicacion_id = ? AND p.activo = 1 AND u.activo = 1
        ORDER BY p.nombre
    """, (location_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def update_inventory(inventory_id: int, cantidad: int, usuario_id: int):
    """Actualiza la cantidad de un registro de inventario."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE inventario 
        SET cantidad = ?, actualizado_en = ?, actualizado_por = ?
        WHERE id = ?
    """, (cantidad, now, usuario_id, inventory_id))
    conn.commit()
    conn.close()
    return True


def get_inventory_by_id(inventory_id: int):
    """Obtiene un registro de inventario por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.producto_id, i.ubicacion_id, i.cantidad, i.lote, 
               i.fecha_vencimiento, i.actualizado_en, i.actualizado_por,
               p.sku, p.nombre as producto_nombre, 
               u.codigo as ubicacion_codigo, 
               z.nombre as zona_nombre
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        LEFT JOIN zonas z ON u.zona_id = z.id
        WHERE i.id = ?
    """, (inventory_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def get_inventory_summary():
    """Obtiene un resumen del inventario con totales por producto."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            p.id as producto_id,
            p.sku,
            p.nombre as producto_nombre,
            COALESCE(SUM(i.cantidad), 0) as stock_total,
            COUNT(DISTINCT i.ubicacion_id) as ubicaciones_ocupadas
        FROM productos p
        LEFT JOIN inventario i ON p.id = i.producto_id
        WHERE p.activo = 1
        GROUP BY p.id, p.sku, p.nombre
        ORDER BY p.nombre
    """)
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_inventory_by_zone(zona_id: int):
    """Obtiene inventario filtrado por zona."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.producto_id, i.ubicacion_id, i.cantidad, i.lote, 
               i.fecha_vencimiento, i.actualizado_en, i.actualizado_por,
               p.sku, p.nombre as producto_nombre, 
               u.codigo as ubicacion_codigo, 
               z.nombre as zona_nombre
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        JOIN zonas z ON u.zona_id = z.id
        WHERE z.id = ? AND p.activo = 1 AND u.activo = 1
        ORDER BY p.nombre, u.codigo
    """, (zona_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results] if results else []


def get_total_inventory_value():
    """Calcula el valor total del inventario (requiere campo precio en productos)."""
    # Esta función es un placeholder - requeriría un campo de precio en productos
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COALESCE(SUM(i.cantidad), 0) as total_unidades,
            COUNT(DISTINCT i.producto_id) as productos_con_stock
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        WHERE p.activo = 1
    """)
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else {"total_unidades": 0, "productos_con_stock": 0}
