"""Página de Picking de WareFlow WMS."""

import streamlit as st
import pandas as pd

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.forms import input_text, input_number, input_select, form_submit_button
from components.tables import render_table
from components.alerts import alert_success, alert_error, alert_info
from services.product_service import get_all_products, get_inventory, get_product_by_sku
from services.location_service import get_all_locations
from services.movement_service import (
    get_movements_by_type, create_picking_order, process_picking
)

require_auth()
require_permission("picking", "leer")

render_sidebar(current_page="picking")
render_navbar(titulo="Picking", icono="📦")

# Tabs for different functions
tab1, tab2, tab3 = st.tabs(["Crear Orden de Picking", "Guiar Picking", "Validar y Completar"])

# Tab 1: Crear Orden de Picking
with tab1:
    st.header("Crear Orden de Picking")
    
    productos = get_all_products()
    ubicaciones = get_all_locations()
    
    if not productos:
        alert_info("No hay productos disponibles.")
    elif not ubicaciones:
        alert_info("No hay ubicaciones disponibles.")
    else:
        with st.form("form_picking"):
            # Product selector
            producto_options = {f"{p['sku']} - {p['nombre']}": p["id"] for p in productos}
            selected_product = st.selectbox("Seleccionar Producto", list(producto_options.keys()))
            producto_id = producto_options[selected_product] if selected_product else None
            
            # Location selector
            ubicacion_options = {f"{u['codigo']} - {u['zona_nombre']}": u["id"] for u in ubicaciones}
            selected_ubicacion = st.selectbox("Ubicación de Origen", list(ubicacion_options.keys()))
            ubicacion_id = ubicacion_options[selected_ubicacion] if selected_ubicacion else None
            
            # Quantity
            cantidad = st.number_input("Cantidad a Recoger", min_value=1, value=1)
            
            # Reference and observations
            referencia = st.text_input("Referencia (opcional)")
            observaciones = st.text_area("Observaciones (opcional)")
            
            submitted = st.form_submit_button("Crear Orden")
            
            if submitted and producto_id and ubicacion_id:
                try:
                    usuario_id = st.session_state.get("usuario_id")
                    create_picking_order(
                        producto_id=producto_id,
                        cantidad=cantidad,
                        ubicacion_origen_id=ubicacion_id,
                        referencia=referencia,
                        observaciones=observaciones,
                        usuario_id=usuario_id
                    )
                    alert_success("Orden de picking creada exitosamente!")
                except Exception as e:
                    alert_error(f"Error al crear la orden: {str(e)}")

# Tab 2: Guiar Picking
with tab2:
    st.header("Ordenes de Picking Pendientes")
    
    picking_orders = get_movements_by_type("PICKING", limit=100)
    pending_orders = [o for o in picking_orders if o["estado"] == "PENDIENTE"]
    
    if not pending_orders:
        alert_info("No hay órdenes de picking pendientes.")
    else:
        df_pending = pd.DataFrame(pending_orders)
        # Show relevant columns
        columns_to_show = ["id", "sku", "producto_nombre", "origen_codigo", "cantidad", "referencia", "estado", "fecha_movimiento"]
        available_columns = [col for col in columns_to_show if col in df_pending.columns]
        render_table(df_pending[available_columns] if available_columns else df_pending)

# Tab 3: Validar y Completar
with tab3:
    st.header("Validar y Completar Picking")
    
    picking_orders = get_movements_by_type("PICKING", limit=100)
    pending_orders = [o for o in picking_orders if o["estado"] == "PENDIENTE"]
    
    if not pending_orders:
        alert_info("No hay órdenes de picking pendientes para validar.")
    else:
        # Order selector
        order_options = {f"Orden #{o['id']} - {o['sku']} ({o['cantidad']} uds)": o["id"] for o in pending_orders}
        selected_order_label = st.selectbox("Seleccionar Orden de Picking", list(order_options.keys()))
        selected_order_id = order_options[selected_order_label]
        
        # Show order details
        selected_order = next(o for o in pending_orders if o["id"] == selected_order_id)
        st.subheader("Detalles de la Orden")
        st.write(f"**Producto:** {selected_order['sku']} - {selected_order['producto_nombre']}")
        st.write(f"**Ubicación:** {selected_order['origen_codigo']}")
        st.write(f"**Cantidad:** {selected_order['cantidad']}")
        st.write(f"**Estado:** {selected_order['estado']}")
        
        # Validate SKU/Code
        st.subheader("Validar Código")
        sku_input = st.text_input("Escanear o ingresar SKU del producto")
        if sku_input:
            product = get_product_by_sku(sku_input)
            if product and product["id"] == selected_order["producto_id"]:
                alert_success("SKU validado correctamente!")
                
                # Complete button
                if st.button("Completar Picking"):
                    try:
                        usuario_id = st.session_state.get("usuario_id")
                        success, message = process_picking(selected_order_id, usuario_id)
                        if success:
                            alert_success(message)
                            st.rerun()
                        else:
                            alert_error(message)
                    except Exception as e:
                        alert_error(f"Error al procesar: {str(e)}")
            else:
                alert_error("SKU no coincide con el producto de la orden.")

# Show all picking orders
st.divider()
st.header("Historial de Picking")
all_picking = get_movements_by_type("PICKING", limit=50)
if all_picking:
    df_all = pd.DataFrame(all_picking)
    columns_to_show = ["id", "sku", "producto_nombre", "origen_codigo", "cantidad", "estado", "fecha_movimiento"]
    available_columns = [col for col in columns_to_show if col in df_all.columns]
    render_table(df_all[available_columns] if available_columns else df_all)
else:
    alert_info("No hay órdenes de picking en el historial.")
