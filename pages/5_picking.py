"""Página de Picking de WareFlow WMS."""

import streamlit as st
import pandas as pd

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.ui_helpers import svg_icon, section_title, kpi_card, spacer
from services.product_service import get_all_products, get_product_by_sku
from services.location_service import get_all_locations
from services.movement_service import (
    get_movements_by_type, create_picking_order, process_picking
)

require_auth()
require_permission("picking", "leer")

render_sidebar(current_page="picking")
render_navbar(titulo="Picking", subtitulo="Preparación y recolección de pedidos", icono="cart")

# KPI Cards
picking_orders = get_movements_by_type("PICKING", limit=100)
pending_orders = [o for o in picking_orders if o["estado"] == "PENDIENTE"]
completed_today = [o for o in picking_orders if o["estado"] == "COMPLETADO"]

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown(kpi_card("list", "Pendientes", f"{len(pending_orders):,}"), unsafe_allow_html=True)

with col2:
    st.markdown(kpi_card("check", "Completadas hoy", f"{len(completed_today):,}"), unsafe_allow_html=True)

with col3:
    st.markdown(kpi_card("box", "Total órdenes", f"{len(picking_orders):,}"), unsafe_allow_html=True)

spacer()

# Tabs
tab1, tab2, tab3 = st.tabs(["Crear Orden", "Guiar Picking", "Validar"])

# Tab 1: Crear Orden de Picking
with tab1:
    section_title("plus", "Crear orden de picking")
    
    productos = get_all_products()
    ubicaciones = get_all_locations()
    
    if not productos:
        st.info("ℹ️ No hay productos disponibles.")
    elif not ubicaciones:
        st.info("ℹ️ No hay ubicaciones disponibles.")
    else:
        with st.form("form_picking"):
            col1, col2 = st.columns(2, gap="medium")
            
            with col1:
                section_title("box", "Producto")
                producto_options = {f"{p['sku']} - {p['nombre']}": p["id"] for p in productos}
                selected_product = st.selectbox("Seleccionar producto", list(producto_options.keys()))
                producto_id = producto_options[selected_product] if selected_product else None
                
                section_title("arrow-down", "Cantidad")
                cantidad = st.number_input("Cantidad a recoger", min_value=1, value=1)
            
            with col2:
                section_title("pin", "Ubicación de origen")
                ubicacion_options = {f"{u['codigo']} - {u['zona_nombre']}": u["id"] for u in ubicaciones}
                selected_ubicacion = st.selectbox("Ubicación", list(ubicacion_options.keys()))
                ubicacion_id = ubicacion_options[selected_ubicacion] if selected_ubicacion else None
                
                section_title("file", "Referencia")
                referencia = st.text_input("Referencia (opcional)", placeholder="Ej: PED-2024-001")
            
            section_title("edit", "Observaciones")
            observaciones = st.text_area("Observaciones (opcional)", placeholder="Detalles adicionales...")
            
            spacer()
            submitted = st.form_submit_button("Crear Orden", use_container_width=True, type="primary")
            
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
                    st.success("✅ Orden de picking creada exitosamente!")
                except Exception as e:
                    st.error(f"❌ Error al crear la orden: {str(e)}")

# Tab 2: Guiar Picking
with tab2:
    section_title("search", "Órdenes de picking pendientes")
    
    picking_orders = get_movements_by_type("PICKING", limit=100)
    pending_orders = [o for o in picking_orders if o["estado"] == "PENDIENTE"]
    
    if not pending_orders:
        st.info("ℹ️ No hay órdenes de picking pendientes.")
    else:
        df_pending = pd.DataFrame(pending_orders)
        columns_to_show = ["id", "sku", "producto_nombre", "origen_codigo", "cantidad", "referencia", "estado", "fecha_movimiento"]
        available_columns = [col for col in columns_to_show if col in df_pending.columns]
        st.dataframe(df_pending[available_columns] if available_columns else df_pending, use_container_width=True, hide_index=True)

# Tab 3: Validar y Completar
with tab3:
    section_title("check", "Validar y completar picking")
    
    picking_orders = get_movements_by_type("PICKING", limit=100)
    pending_orders = [o for o in picking_orders if o["estado"] == "PENDIENTE"]
    
    if not pending_orders:
        st.info("ℹ️ No hay órdenes de picking pendientes para validar.")
    else:
        order_options = {f"Orden #{o['id']} - {o['sku']} ({o['cantidad']} uds)": o["id"] for o in pending_orders}
        selected_order_label = st.selectbox("Seleccionar orden de picking", list(order_options.keys()))
        selected_order_id = order_options[selected_order_label]
        
        selected_order = next(o for o in pending_orders if o["id"] == selected_order_id)
        
        # Card con detalles de la orden
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #E0E7FF 0%, #C7D2FE 100%); 
                        border-radius: 0.75rem; 
                        padding: 1.25rem; 
                        margin-bottom: 1.5rem;
                        border: 1px solid #A5B4FC;'>
                <h4 style='margin: 0 0 1rem 0; color: #3730A3; font-size: 1.1rem; font-weight: 600;'>
                    Detalles de la orden
                </h4>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;'>
                    <p style='margin: 0; color: #4338CA; font-size: 0.9rem;'><strong>ID:</strong> {selected_order['id']}</p>
                    <p style='margin: 0; color: #4338CA; font-size: 0.9rem;'><strong>Estado:</strong> {selected_order['estado']}</p>
                    <p style='margin: 0; color: #4338CA; font-size: 0.9rem;'><strong>Producto:</strong> {selected_order['sku']} - {selected_order['producto_nombre']}</p>
                    <p style='margin: 0; color: #4338CA; font-size: 0.9rem;'><strong>Ubicación:</strong> {selected_order['origen_codigo']}</p>
                    <p style='margin: 0; color: #4338CA; font-size: 0.9rem;'><strong>Cantidad:</strong> {selected_order['cantidad']}</p>
                    <p style='margin: 0; color: #4338CA; font-size: 0.9rem;'><strong>Referencia:</strong> {selected_order['referencia'] or 'N/A'}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        section_title("search", "Validar código")
        sku_input = st.text_input("Escanear o ingresar SKU del producto", placeholder="Ej: PROD-001")
        
        if sku_input:
            product = get_product_by_sku(sku_input)
            if product and product["id"] == selected_order["producto_id"]:
                st.success("✅ SKU validado correctamente!")
                
                if st.button("Completar Picking", use_container_width=True, type="primary"):
                    try:
                        usuario_id = st.session_state.get("usuario_id")
                        success, message = process_picking(selected_order_id, usuario_id)
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    except Exception as e:
                        st.error(f"❌ Error al procesar: {str(e)}")
            else:
                st.error("❌ SKU no coincide con el producto de la orden.")

spacer()
st.markdown("---")
spacer()

# Historial de Picking
section_title("list", "Historial de picking")
all_picking = get_movements_by_type("PICKING", limit=50)
if all_picking:
    df_all = pd.DataFrame(all_picking)
    columns_to_show = ["id", "sku", "producto_nombre", "origen_codigo", "cantidad", "estado", "fecha_movimiento"]
    available_columns = [col for col in columns_to_show if col in df_all.columns]
    
    def highlight_estado_row(row):
        if row["estado"] == "COMPLETADO":
            return ['background-color: #dcfce7'] * len(row)
        elif row["estado"] == "PENDIENTE":
            return ['background-color: #fef9c3'] * len(row)
        return [''] * len(row)
    
    styled_df = df_all[available_columns].style.apply(highlight_estado_row, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
else:
    st.info("ℹ️ No hay órdenes de picking en el historial.")
