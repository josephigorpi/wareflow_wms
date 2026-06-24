"""Dashboard principal de WareFlow WMS."""

import streamlit as st
import pandas as pd
import plotly.express as px

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.kpi_card import render_kpi_card
from components.alerts import alert_warning
from components.tables import render_table
from services.product_service import count_active_products, get_products_low_stock
from services.location_service import count_free_locations, get_location_occupation_by_zone
from services.movement_service import get_recent_movements, count_movements_by_type_today
from utils.formatters import format_date

require_auth()
require_permission("dashboard", "leer")

render_sidebar(current_page="dashboard")
render_navbar(titulo="Dashboard", subtitulo="Visión general del sistema", icono="📊")

col1, col2, col3, col4 = st.columns(4)

active_products = count_active_products()
free_locations = count_free_locations()
movements_today = count_movements_by_type_today()

with col1:
    render_kpi_card("Productos activos", active_products, icono="📦")

with col2:
    render_kpi_card("Ubicaciones libres", free_locations, icono="📍")

with col3:
    render_kpi_card("Entradas del día", movements_today["entradas"], icono="📥", color="green")

with col4:
    render_kpi_card("Salidas del día", movements_today["salidas"], icono="📤", color="red")

low_stock_products = get_products_low_stock()
if low_stock_products:
    st.markdown("### ⚠️ Alertas de stock mínimo")
    for product in low_stock_products:
        alert_warning(f"Producto {product['sku']} - {product['nombre']}: Stock actual {product['stock_total']} (mínimo {product['stock_minimo']})")

st.markdown("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### Últimos 20 movimientos")
    recent_movements = get_recent_movements(20)
    if recent_movements:
        df_movements = pd.DataFrame(recent_movements)
        df_movements["fecha_movimiento"] = df_movements["fecha_movimiento"].apply(format_date)
        df_movements_display = df_movements[["fecha_movimiento", "tipo", "sku", "producto_nombre", "cantidad", "usuario_nombre", "estado"]]
        df_movements_display.columns = ["Fecha", "Tipo", "SKU", "Producto", "Cantidad", "Usuario", "Estado"]
        render_table(df_movements_display)
    else:
        st.info("No hay movimientos registrados.")

with col_right:
    st.markdown("### Ocupación por zona")
    occupation_by_zone = get_location_occupation_by_zone()
    if occupation_by_zone:
        df_zone = pd.DataFrame(occupation_by_zone)
        df_zone["libres"] = df_zone["total"] - df_zone["ocupadas"]
        df_zone_melt = df_zone.melt(id_vars=["zona"], value_vars=["ocupadas", "libres"], var_name="Estado", value_name="Cantidad")
        fig = px.bar(df_zone_melt, x="zona", y="Cantidad", color="Estado", barmode="group",
                    title="Ocupación de ubicaciones por zona")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de ocupación por zona.")
