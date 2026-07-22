"""Dashboard principal de WareFlow WMS."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.alerts import alert_warning
from services.product_service import count_active_products, get_products_low_stock
from services.location_service import count_free_locations, get_location_occupation_by_zone
from services.movement_service import get_recent_movements, count_movements_by_type_today
from utils.formatters import format_date

require_auth()
require_permission("dashboard", "leer")

render_sidebar(current_page="dashboard")
render_navbar(titulo="Dashboard", subtitulo="Visión general del sistema", icono="📊")

# KPI Cards con diseño moderno
col1, col2, col3, col4 = st.columns(4, gap="large")

active_products = count_active_products()
free_locations = count_free_locations()
movements_today = count_movements_by_type_today()

with col1:
    st.metric(
        label="📦 Productos Activos",
        value=f"{active_products:,}",
        delta=None
    )

with col2:
    st.metric(
        label="📍 Ubicaciones Libres",
        value=f"{free_locations:,}",
        delta=None
    )

with col3:
    st.metric(
        label="📥 Entradas Hoy",
        value=f"{movements_today['entradas']:,}",
        delta=None
    )

with col4:
    st.metric(
        label="📤 Salidas Hoy",
        value=f"{movements_today['salidas']:,}",
        delta=None
    )

st.markdown("<br>", unsafe_allow_html=True)

# Alertas de stock con diseño moderno
low_stock_products = get_products_low_stock()
if low_stock_products:
    with st.expander("⚠️ Alertas de Stock Mínimo", expanded=True):
        for product in low_stock_products:
            st.warning(
                f"**{product['sku']} - {product['nombre']}**\n\n"
                f"Stock actual: {product['stock_total']} | Mínimo: {product['stock_minimo']}"
            )

st.markdown("<br>", unsafe_allow_html=True)

# Contenido principal en dos columnas
col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    st.markdown("### 📋 Últimos Movimientos")
    recent_movements = get_recent_movements(20)
    if recent_movements:
        df_movements = pd.DataFrame(recent_movements)
        df_movements["fecha_movimiento"] = df_movements["fecha_movimiento"].apply(format_date)
        df_movements_display = df_movements[["fecha_movimiento", "tipo", "sku", "producto_nombre", "cantidad", "usuario_nombre", "estado"]]
        df_movements_display.columns = ["Fecha", "Tipo", "SKU", "Producto", "Cantidad", "Usuario", "Estado"]
        
        # Colores para estados
        def highlight_estado(val):
            if val == "Completado":
                return "background-color: #dcfce7; color: #166534"
            elif val == "Pendiente":
                return "background-color: #fef9c3; color: #854d0e"
            elif val == "Cancelado":
                return "background-color: #fee2e2; color: #991b1b"
            return ""
        
        styled_df = df_movements_display.style.applymap(highlight_estado, subset=["Estado"])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay movimientos registrados.")

with col_right:
    st.markdown("### 📊 Ocupación por Zona")
    occupation_by_zone = get_location_occupation_by_zone()
    if occupation_by_zone:
        df_zone = pd.DataFrame(occupation_by_zone)
        df_zone["libres"] = df_zone["total"] - df_zone["ocupadas"]
        df_zone_melt = df_zone.melt(id_vars=["zona"], value_vars=["ocupadas", "libres"], var_name="Estado", value_name="Cantidad")
        
        # Gráfico más moderno
        fig = px.bar(
            df_zone_melt,
            x="zona",
            y="Cantidad",
            color="Estado",
            barmode="group",
            title="",
            color_discrete_map={"ocupadas": "#3B82F6", "libres": "#E2E8F0"},
            template="plotly_white"
        )
        
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                showgrid=False,
                showline=False,
                tickfont=dict(size=11)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#E2E8F0",
                gridwidth=1,
                showline=False,
                tickfont=dict(size=11)
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=300
        )
        
        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>%{y} ubicaciones<extra></extra>",
            marker_line=dict(width=0),
            marker_line_color="white"
        )
        
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No hay datos de ocupación por zona.")
