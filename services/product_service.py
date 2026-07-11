"""Lógica de negocio de productos para WareFlow WMS."""

from database.connection import get_connection
from datetime import datetime, timedelta


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


def get_products_high_stock():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, COALESCE(SUM(i.cantidad), 0) as stock_total
        FROM productos p
        LEFT JOIN inventario i ON p.id = i.producto_id
        WHERE p.activo = 1 AND p.stock_maximo IS NOT NULL
        GROUP BY p.id
        HAVING stock_total >= p.stock_maximo
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


def count_low_stock_products():
    return len(get_products_low_stock())


def count_high_stock_products():
    return len(get_products_high_stock())


def get_expiring_products(days: int = 30):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    future_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT DISTINCT p.*, i.lote, i.fecha_vencimiento, i.cantidad, u.codigo as ubicacion_codigo
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        WHERE i.fecha_vencimiento IS NOT NULL 
        AND i.fecha_vencimiento BETWEEN ? AND ?
        AND p.activo = 1
        ORDER BY i.fecha_vencimiento
    """, (today, future_date))
    return cursor.fetchall()


def count_expiring_products(days: int = 30):
    return len(get_expiring_products(days))


def get_product_by_sku(sku: str):
    """
    Obtiene un producto por su SKU.
    
    Args:
        sku (str): El SKU del producto a buscar
        
    Returns:
        dict or None: El producto encontrado o None si no existe
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, 
               c.nombre as categoria_nombre,
               COALESCE(SUM(i.cantidad), 0) as stock_total
        FROM productos p
        LEFT JOIN categorias_producto c ON p.categoria_id = c.id
        LEFT JOIN inventario i ON p.id = i.producto_id
        WHERE p.sku = ? AND p.activo = 1
        GROUP BY p.id
    """, (sku,))
    
    result = cursor.fetchone()
    conn.close()
    return result
