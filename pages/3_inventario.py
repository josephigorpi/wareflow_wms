"""Página de Control de Inventario de WareFlow WMS."""

import streamlit as st
import pandas as pd

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.ui_helpers import svg_icon, section_title, kpi_card, alert_card, spacer
from services.product_service import (
    count_active_products,
    count_low_stock_products, count_expiring_products,
    get_products_low_stock, get_products_high_stock, get_expiring_products, get_all_products
)
from services.location_service import get_all_locations, get_locations_with_zones
from services.inventory_service import (
    get_all_inventory, get_inventory_by_product, get_inventory_by_location,
    update_inventory, get_inventory_by_id
)
from utils.formatters import format_date

require_auth()
require_permission("inventario", "leer")

render_sidebar(current_page="inventario")
render_navbar(titulo="Control de Inventario", subtitulo="Gestión de stock, lotes y fechas de vencimiento", icono="box")

# KPI Cards
active_products = count_active_products()
low_stock = count_low_stock_products()
expiring_products = count_expiring_products()

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown(kpi_card("box", "Total productos", f"{active_products:,}"), unsafe_allow_html=True)

with col2:
    st.markdown(kpi_card("alert", "Stock bajo", f"{low_stock:,}"), unsafe_allow_html=True)

with col3:
    st.markdown(kpi_card("arrow-down", "Próximos a vencer", f"{expiring_products:,}"), unsafe_allow_html=True)

spacer()

# Alertas
low_stock_products = get_products_low_stock()
high_stock_products = get_products_high_stock()
expiring_products_list = get_expiring_products()

if low_stock_products or high_stock_products or expiring_products_list:
    with st.expander("Alertas de inventario", expanded=False):
        if low_stock_products:
            st.markdown("**Stock mínimo**")
            for product in low_stock_products:
                st.markdown(alert_card("alert", product['sku'], f"{product['nombre']}: {product['stock_total']} (mín: {product['stock_minimo']})"), unsafe_allow_html=True)
        
        if high_stock_products:
            st.markdown("**Stock máximo**")
            for product in high_stock_products:
                st.markdown(alert_card("alert", product['sku'], f"{product['nombre']}: {product['stock_total']} (máx: {product['stock_maximo']})"), unsafe_allow_html=True)
        
        if expiring_products_list:
            st.markdown("**Próximos a vencer**")
            for product in expiring_products_list:
                st.markdown(alert_card("arrow-down", product['sku'], f"{product['nombre']} (Lote: {product['lote']} - Vence: {format_date(product['fecha_vencimiento'])})"), unsafe_allow_html=True)

spacer()

# Filtros
section_title("filter", "Filtros de inventario")
col_filtro1, col_filtro2 = st.columns(2, gap="medium")

products = get_all_products()
product_options = ["Todos"] + [f"{p['sku']} - {p['nombre']}" for p in products]
product_dict = {f"{p['sku']} - {p['nombre']}": p['id'] for p in products}

locations = get_all_locations()
location_options = ["Todos"] + [u['codigo'] for u in locations]
location_dict = {u['codigo']: u['id'] for u in locations}

with col_filtro1:
    selected_product_label = st.selectbox("Filtrar por producto", product_options, key="filtro_producto")

with col_filtro2:
    selected_location_code = st.selectbox("Filtrar por ubicación", location_options, key="filtro_ubicacion")

# Obtener inventario según filtros
if selected_product_label != "Todos" and selected_location_code != "Todos":
    inventory = get_all_inventory()
    inventory = [i for i in inventory if i['producto_id'] == product_dict[selected_product_label] and i['ubicacion_id'] == location_dict[selected_location_code]]
elif selected_product_label != "Todos":
    inventory = get_inventory_by_product(product_dict[selected_product_label])
elif selected_location_code != "Todos":
    inventory = get_inventory_by_location(location_dict[selected_location_code])
else:
    inventory = get_all_inventory()

# Mostrar tabla
spacer()
section_title("list", "Inventario actual")
if inventory:
    df_inventory = pd.DataFrame(inventory)
    if 'fecha_vencimiento' in df_inventory.columns:
        df_inventory['fecha_vencimiento'] = df_inventory['fecha_vencimiento'].apply(lambda x: format_date(x) if x else "")
    df_display = df_inventory[['sku', 'producto_nombre', 'ubicacion_codigo', 'zona_nombre', 'lote', 'fecha_vencimiento', 'cantidad']]
    df_display.columns = ['SKU', 'Producto', 'Ubicación', 'Zona', 'Lote', 'Fecha Vencimiento', 'Cantidad']
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("No hay registros de inventario.")

spacer()

# Ajuste de inventario
section_title("edit", "Ajuste de inventario")

col_ajuste1, col_ajuste2 = st.columns([2, 1], gap="medium")

with col_ajuste1:
    inventory_options = [f"{i['sku']} - {i['producto_nombre']} en {i['ubicacion_codigo']} (Lote: {i['lote'] or 'Sin lote'})" for i in get_all_inventory()]
    inventory_dict = {f"{i['sku']} - {i['producto_nombre']} en {i['ubicacion_codigo']} (Lote: {i['lote'] or 'Sin lote'})": i['id'] for i in get_all_inventory()}
    selected_inventory_label = st.selectbox("Seleccionar item a ajustar", ["-- Seleccionar --"] + inventory_options, key="ajuste_inventario")

if selected_inventory_label != "-- Seleccionar --":
    selected_inventory_id = inventory_dict[selected_inventory_label]
    inventory_item = get_inventory_by_id(selected_inventory_id)
    if inventory_item:
        with st.form("form_ajuste_inventario"):
            col_a, col_b = st.columns(2, gap="medium")
            
            with col_a:
                section_title("box", "Información actual")
                st.info(f"Cantidad actual: {inventory_item['cantidad']}")
                st.info(f"Ubicación: {inventory_item['ubicacion_codigo']}")
                st.info(f"Lote: {inventory_item['lote'] or 'Sin lote'}")
            
            with col_b:
                section_title("edit", "Ajuste")
                new_cantidad = st.number_input("Nueva cantidad", min_value=0, value=inventory_item['cantidad'], key="nueva_cantidad")
            
            spacer()
            submitted = st.form_submit_button("Actualizar Inventario", use_container_width=True, type="primary")
            
            if submitted:
                usuario_id = st.session_state.get('usuario_id')
                update_inventory(selected_inventory_id, new_cantidad, usuario_id)
                st.success(f"✅ Inventario actualizado exitosamente!")
                st.rerun()
