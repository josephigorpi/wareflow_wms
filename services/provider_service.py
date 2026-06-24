"""Servicio de gestión de proveedores y órdenes de compra."""

from database.db_manager import fetch_all, fetch_one, insert, update, delete


# ===== PROVEEDORES =====

def get_all_providers():
    """Obtiene todos los proveedores activos."""
    query = "SELECT * FROM proveedores WHERE activo = 1 ORDER BY nombre"
    return fetch_all(query)


def get_provider_by_id(provider_id: int):
    """Obtiene un proveedor por ID."""
    query = "SELECT * FROM proveedores WHERE id = ?"
    return fetch_one(query, (provider_id,))


def create_provider(nombre: str, contacto: str = "", telefono: str = "", 
                   email: str = "", ciudad: str = "", direccion: str = ""):
    """Crea un nuevo proveedor."""
    from datetime import datetime
    created_at = datetime.now().isoformat()
    
    query = """
        INSERT INTO proveedores (nombre, contacto, telefono, email, ciudad, direccion, creado_en)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = (nombre, contacto, telefono, email, ciudad, direccion, created_at)
    return insert(query, params)


def update_provider(provider_id: int, **kwargs):
    """Actualiza un proveedor."""
    allowed_fields = {'nombre', 'contacto', 'telefono', 'email', 'ciudad', 'direccion', 'activo'}
    fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not fields:
        return False
    
    set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
    values = list(fields.values()) + [provider_id]
    
    query = f"UPDATE proveedores SET {set_clause} WHERE id = ?"
    return update(query, values)


def delete_provider(provider_id: int):
    """Desactiva un proveedor (soft delete)."""
    query = "UPDATE proveedores SET activo = 0 WHERE id = ?"
    return update(query, (provider_id,))


# ===== ÓRDENES DE COMPRA =====

def get_all_purchase_orders():
    """Obtiene todas las órdenes de compra."""
    query = """
        SELECT oc.*, p.nombre as proveedor_nombre 
        FROM ordenes_compra oc
        LEFT JOIN proveedores p ON oc.proveedor_id = p.id
        ORDER BY oc.fecha_emision DESC
    """
    return fetch_all(query)


def get_purchase_order_by_id(order_id: int):
    """Obtiene una orden de compra por ID."""
    query = """
        SELECT oc.*, p.nombre as proveedor_nombre 
        FROM ordenes_compra oc
        LEFT JOIN proveedores p ON oc.proveedor_id = p.id
        WHERE oc.id = ?
    """
    return fetch_one(query, (order_id,))


def get_purchase_order_by_number(numero_oc: str):
    """Obtiene una orden de compra por número."""
    query = """
        SELECT oc.*, p.nombre as proveedor_nombre 
        FROM ordenes_compra oc
        LEFT JOIN proveedores p ON oc.proveedor_id = p.id
        WHERE oc.numero_oc = ?
    """
    return fetch_one(query, (numero_oc,))


def get_purchase_orders_by_provider(provider_id: int):
    """Obtiene todas las órdenes de compra de un proveedor."""
    query = """
        SELECT oc.*, p.nombre as proveedor_nombre 
        FROM ordenes_compra oc
        LEFT JOIN proveedores p ON oc.proveedor_id = p.id
        WHERE oc.proveedor_id = ?
        ORDER BY oc.fecha_emision DESC
    """
    return fetch_all(query, (provider_id,))


def get_pending_purchase_orders():
    """Obtiene órdenes de compra pendientes."""
    query = """
        SELECT oc.*, p.nombre as proveedor_nombre 
        FROM ordenes_compra oc
        LEFT JOIN proveedores p ON oc.proveedor_id = p.id
        WHERE oc.estado = 'PENDIENTE'
        ORDER BY oc.fecha_entrega_esperada
    """
    return fetch_all(query)


def create_purchase_order(numero_oc: str, proveedor_id: int, fecha_emision: str, 
                         fecha_entrega_esperada: str, items: list = None):
    """Crea una nueva orden de compra con sus items.
    
    Args:
        numero_oc: Número único de la OC
        proveedor_id: ID del proveedor
        fecha_emision: Fecha de emisión
        fecha_entrega_esperada: Fecha esperada de entrega
        items: Lista de items [{producto_id, cantidad_ordenada, precio_unitario}, ...]
    """
    from datetime import datetime
    created_at = datetime.now().isoformat()
    total_items = len(items) if items else 0
    
    # Crear la orden de compra
    query = """
        INSERT INTO ordenes_compra (numero_oc, proveedor_id, fecha_emision, 
                                    fecha_entrega_esperada, total_items, creado_en)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (numero_oc, proveedor_id, fecha_emision, fecha_entrega_esperada, total_items, created_at)
    order_id = insert(query, params)
    
    # Crear los items de la orden
    if items and order_id:
        for item in items:
            create_purchase_order_item(
                order_id,
                item.get('producto_id'),
                item.get('cantidad_ordenada'),
                item.get('precio_unitario', 0)
            )
    
    return order_id


def update_purchase_order_status(order_id: int, nuevo_estado: str):
    """Actualiza el estado de una orden de compra."""
    query = "UPDATE ordenes_compra SET estado = ? WHERE id = ?"
    return update(query, (nuevo_estado, order_id))


def create_purchase_order_item(orden_id: int, producto_id: int, 
                              cantidad_ordenada: int, precio_unitario: float = 0):
    """Crea un item en una orden de compra."""
    query = """
        INSERT INTO ordenes_compra_items (orden_compra_id, producto_id, cantidad_ordenada, precio_unitario)
        VALUES (?, ?, ?, ?)
    """
    params = (orden_id, producto_id, cantidad_ordenada, precio_unitario)
    return insert(query, params)


def get_purchase_order_items(orden_id: int):
    """Obtiene los items de una orden de compra."""
    query = """
        SELECT oci.*, p.sku, p.nombre 
        FROM ordenes_compra_items oci
        LEFT JOIN productos p ON oci.producto_id = p.id
        WHERE oci.orden_compra_id = ?
    """
    return fetch_all(query, (orden_id,))


def update_purchase_order_item_received(item_id: int, cantidad_recibida: int):
    """Actualiza la cantidad recibida de un item de OC."""
    query = "UPDATE ordenes_compra_items SET cantidad_recibida = ? WHERE id = ?"
    return update(query, (cantidad_recibida, item_id))
