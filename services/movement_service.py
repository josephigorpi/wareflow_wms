"""Lógica de negocio de movimientos de inventario para WareFlow WMS."""

from datetime import datetime
from database.db_manager import fetch_all, fetch_one, insert, update
from services.product_service import get_inventory


def get_recent_movements(limit: int = 50):
    """Obtiene los movimientos más recientes."""
    query = """
        SELECT 
            m.id, m.tipo, m.producto_id, m.ubicacion_origen_id, m.ubicacion_destino_id,
            m.cantidad, m.referencia, m.observaciones, m.estado, m.usuario_id, m.fecha_movimiento,
            p.sku, p.nombre as producto_nombre,
            u1.codigo as origen_codigo, z1.nombre as origen_zona,
            u2.codigo as destino_codigo, z2.nombre as destino_zona
        FROM movimientos m
        JOIN productos p ON m.producto_id = p.id
        LEFT JOIN ubicaciones u1 ON m.ubicacion_origen_id = u1.id
        LEFT JOIN zonas z1 ON u1.zona_id = z1.id
        LEFT JOIN ubicaciones u2 ON m.ubicacion_destino_id = u2.id
        LEFT JOIN zonas z2 ON u2.zona_id = z2.id
        ORDER BY m.fecha_movimiento DESC
        LIMIT ?
    """
    results = fetch_all(query, (limit,))
    return [dict(row) for row in results] if results else []


def get_movements_by_type(tipo, limit: int = 100):
    """Obtiene movimientos filtrados por tipo."""
    query = """
        SELECT 
            m.id, m.tipo, m.producto_id, m.ubicacion_origen_id, m.ubicacion_destino_id,
            m.cantidad, m.referencia, m.observaciones, m.estado, m.usuario_id, m.fecha_movimiento,
            p.sku, p.nombre as producto_nombre,
            u1.codigo as origen_codigo,
            u2.codigo as destino_codigo
        FROM movimientos m
        JOIN productos p ON m.producto_id = p.id
        LEFT JOIN ubicaciones u1 ON m.ubicacion_origen_id = u1.id
        LEFT JOIN ubicaciones u2 ON m.ubicacion_destino_id = u2.id
        WHERE m.tipo = ?
        ORDER BY m.fecha_movimiento DESC
        LIMIT ?
    """
    results = fetch_all(query, (tipo, limit))
    return [dict(row) for row in results] if results else []


def get_movement_by_id(movement_id):
    """Obtiene un movimiento por su ID."""
    query = "SELECT * FROM movimientos WHERE id = ?"
    result = fetch_one(query, (movement_id,))
    return dict(result) if result else None


def create_movement(tipo, producto_id, cantidad, referencia=None, observaciones=None,
                    ubicacion_origen_id=None, ubicacion_destino_id=None, usuario_id=None, estado="PENDIENTE"):
    """Crea un nuevo movimiento de inventario."""
    data = {
        "tipo": tipo,
        "producto_id": producto_id,
        "ubicacion_origen_id": ubicacion_origen_id,
        "ubicacion_destino_id": ubicacion_destino_id,
        "cantidad": cantidad,
        "referencia": referencia,
        "observaciones": observaciones,
        "estado": estado,
        "usuario_id": usuario_id,
        "fecha_movimiento": datetime.now().isoformat()
    }
    return insert("movimientos", data)


def update_movement_status(movement_id, estado):
    """Actualiza el estado de un movimiento."""
    data = {"estado": estado}
    return update("movimientos", data, "id = ?", (movement_id,))


def process_picking(movement_id, usuario_id=None):
    """Procesa un picking: valida y actualiza inventario."""
    movement = get_movement_by_id(movement_id)
    if not movement or movement["estado"] != "PENDIENTE":
        return False, "Movimiento no encontrado o no pendiente"
    
    if movement["tipo"] != "PICKING":
        return False, "El movimiento no es de tipo PICKING"
    
    # Validar que haya suficiente inventario
    inventory = get_inventory(
        product_id=movement["producto_id"],
        location_id=movement["ubicacion_origen_id"]
    )
    
    if not inventory:
        return False, "No hay inventario disponible en la ubicación de origen"
    
    total_available = sum(item["cantidad"] for item in inventory)
    if total_available < movement["cantidad"]:
        return False, f"Stock insuficiente. Disponible: {total_available}, Requerido: {movement['cantidad']}"
    
    # Actualizar inventario (descontar de origen)
    # For simplicity, we'll take from the first available location
    item = inventory[0]
    from database.db_manager import execute
    execute(
        "UPDATE inventario SET cantidad = cantidad - ? WHERE id = ?",
        (movement["cantidad"], item["id"])
    )
    
    # Actualizar movimiento
    update_movement_status(movement_id, "COMPLETADO")
    
    return True, "Picking completado exitosamente"


def create_picking_order(producto_id, cantidad, ubicacion_origen_id, referencia=None, observaciones=None, usuario_id=None):
    """Crea una orden de picking."""
    return create_movement(
        tipo="PICKING",
        producto_id=producto_id,
        cantidad=cantidad,
        ubicacion_origen_id=ubicacion_origen_id,
        referencia=referencia,
        observaciones=observaciones,
        usuario_id=usuario_id,
        estado="PENDIENTE"
    )


def create_despacho(movement_ids, referencia=None, observaciones=None, usuario_id=None):
    """Crea un despacho a partir de picking completados."""
    despacho_id = insert("movimientos", {
        "tipo": "DESPACHO",
        "producto_id": None,
        "ubicacion_origen_id": None,
        "ubicacion_destino_id": None,
        "cantidad": 0,
        "referencia": referencia,
        "observaciones": observaciones,
        "estado": "COMPLETADO",
        "usuario_id": usuario_id,
        "fecha_movimiento": datetime.now().isoformat()
    })
    
    # Update picking movements to link to despacho
    # For now, just mark them as part of despacho
    return despacho_id
