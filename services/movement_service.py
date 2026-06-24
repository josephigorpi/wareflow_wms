"""Lógica de negocio de movimientos de inventario para WareFlow WMS."""

import streamlit as st
from datetime import datetime
from database.db_manager import fetch_all, fetch_one, insert, update


def get_recent_movements(limit: int = 50):
    return fetch_all("SELECT * FROM movimientos ORDER BY fecha_movimiento DESC LIMIT ?", (limit,))


def get_movement_by_id(movement_id):
    return fetch_one("SELECT * FROM movimientos WHERE id = ?", (movement_id,))


def get_pending_movements():
    return fetch_all("SELECT * FROM movimientos WHERE estado = 'PENDIENTE' ORDER BY fecha_movimiento DESC")


def create_movement(tipo, producto_id, ubicacion_origen_id, ubicacion_destino_id, cantidad, referencia="", observaciones="", proveedor_id=None, orden_compra_id=None, fecha_movimiento=None):
    if fecha_movimiento is None:
        fecha_movimiento = datetime.now().isoformat()
    user_id = st.session_state.get("user_id")
    
    query = """
        INSERT INTO movimientos 
        (tipo, producto_id, ubicacion_origen_id, ubicacion_destino_id, cantidad, referencia, observaciones, estado, usuario_id, fecha_movimiento, proveedor_id, orden_compra_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (tipo, producto_id, ubicacion_origen_id, ubicacion_destino_id, cantidad, referencia, observaciones, "PENDIENTE", user_id, fecha_movimiento, proveedor_id, orden_compra_id)
    return insert(query, params)


def update_movement_status(movement_id, nuevo_estado, observaciones=""):
    data = {"estado": nuevo_estado}
    if observaciones:
        current = fetch_one("SELECT observaciones FROM movimientos WHERE id = ?", (movement_id,))
        if current and current["observaciones"]:
            data["observaciones"] = f"{current['observaciones']} | {observaciones}"
        else:
            data["observaciones"] = observaciones
    return update("movimientos", data, "id = ?", (movement_id,))


def get_inventory_by_product(product_id):
    return fetch_all("SELECT i.*, u.codigo as ubicacion_codigo FROM inventario i JOIN ubicaciones u ON i.ubicacion_id = u.id WHERE i.producto_id = ?", (product_id,))


def update_inventory(product_id, ubicacion_id, cantidad, lote=None, fecha_vencimiento=None):
    now = datetime.now().isoformat()
    user_id = st.session_state.get("user_id")
    
    existing = fetch_one(
        "SELECT * FROM inventario WHERE producto_id = ? AND ubicacion_id = ? AND (lote = ? OR lote IS NULL)",
        (product_id, ubicacion_id, lote if lote else None)
    )
    
    if existing:
        new_qty = existing["cantidad"] + cantidad
        update(
            "inventario",
            {
                "cantidad": new_qty,
                "actualizado_en": now,
                "actualizado_por": user_id
            },
            "id = ?",
            (existing["id"],)
        )
    else:
        insert(
            "inventario",
            {
                "producto_id": product_id,
                "ubicacion_id": ubicacion_id,
                "cantidad": cantidad,
                "lote": lote,
                "fecha_vencimiento": fecha_vencimiento,
                "actualizado_en": now,
                "actualizado_por": user_id
            }
        )
