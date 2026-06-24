"""Lógica de negocio de productos para WareFlow WMS."""

from database.db_manager import fetch_all, fetch_one, insert, update


def get_all_products():
    """Obtiene todos los productos activos."""
    query = "SELECT * FROM productos WHERE activo = 1 ORDER BY nombre"
    results = fetch_all(query)
    return [dict(row) for row in results] if results else []


def get_product_by_id(product_id):
    """Obtiene un producto por su ID."""
    query = "SELECT * FROM productos WHERE id = ?"
    result = fetch_one(query, (product_id,))
    return dict(result) if result else None


def get_product_by_sku(sku):
    """Obtiene un producto por su SKU."""
    query = "SELECT * FROM productos WHERE sku = ? AND activo = 1"
    result = fetch_one(query, (sku,))
    return dict(result) if result else None


def get_inventory(product_id=None, location_id=None):
    """Obtiene inventario, opcionalmente filtrado por producto y/o ubicación."""
    query = """
        SELECT 
            i.id, i.producto_id, i.ubicacion_id, i.cantidad, i.lote, i.fecha_vencimiento,
            p.sku, p.nombre as producto_nombre,
            u.codigo as ubicacion_codigo, z.nombre as zona_nombre
        FROM inventario i
        JOIN productos p ON i.producto_id = p.id
        JOIN ubicaciones u ON i.ubicacion_id = u.id
        JOIN zonas z ON u.zona_id = z.id
        WHERE i.cantidad > 0
    """
    params = []
    
    if product_id:
        query += " AND i.producto_id = ?"
        params.append(product_id)
    
    if location_id:
        query += " AND i.ubicacion_id = ?"
        params.append(location_id)
    
    query += " ORDER BY p.nombre"
    results = fetch_all(query, tuple(params))
    return [dict(row) for row in results] if results else []
