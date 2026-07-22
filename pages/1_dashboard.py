"""Dashboard principal de WareFlow WMS."""

import streamlit as st
import pandas as pd
import plotly.express as px

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from services.product_service import count_active_products, get_products_low_stock
from services.location_service import count_free_locations, get_location_occupation_by_zone
from services.movement_service import get_recent_movements, count_movements_by_type_today
from utils.formatters import format_date

require_auth()
require_permission("dashboard", "leer")

render_sidebar(current_page="dashboard")
render_navbar(titulo="Dashboard", subtitulo="Visión general del sistema", icono="dashboard")

# ---------------------------------------------------------------------------
# Iconos SVG (estilo line-icon, monocromático, sin emojis)
# ---------------------------------------------------------------------------
ICONS = {
    "box": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.73Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "arrow-down": '<circle cx="12" cy="12" r="10"/><path d="M12 8v8"/><path d="m8 12 4 4 4-4"/>',
    "arrow-up": '<circle cx="12" cy="12" r="10"/><path d="M12 16V8"/><path d="m8 12 4-4 4 4"/>',
    "list": '<path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/>',
    "bar-chart": '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
}


def svg_icon(name: str, size: int = 18, color: str = "#475569") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'
    )


def section_title(icon: str, text: str) -> None:
    st.markdown(
        f"""
        <div style='display:flex; align-items:center; gap:0.5rem; margin: 0 0 0.9rem 0;'>
            {svg_icon(icon, 16, "#64748B")}
            <span style='font-size:0.75rem; font-weight:600; color:#64748B;
                         text-transform:uppercase; letter-spacing:0.06em;'>{text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(icon: str, label: str, value: str) -> str:
    return f"""
        <div style='background:#FFFFFF; border:1px solid #E2E8F0; border-radius:0.65rem;
                     padding:1.1rem 1.25rem; display:flex; align-items:center; gap:0.9rem;'>
            <div style='width:38px; height:38px; border-radius:0.5rem; background:#F1F5F9;
                         display:flex; align-items:center; justify-content:center; flex-shrink:0;'>
                {svg_icon(icon, 18, "#334155")}
            </div>
            <div style='min-width:0;'>
                <p style='margin:0; font-size:0.7rem; font-weight:600; color:#94A3B8;
                           text-transform:uppercase; letter-spacing:0.05em; white-space:nowrap;'>
                    {label}
                </p>
                <p style='margin:0.15rem 0 0 0; font-size:1.5rem; font-weight:700; color:#0F172A;'>
                    {value}
                </p>
            </div>
        </div>
        """


# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
active_products = count_active_products()
free_locations = count_free_locations()
movements_today = count_movements_by_type_today()

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.markdown(kpi_card("box", "Productos activos", f"{active_products:,}"), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_card("pin", "Ubicaciones libres", f"{free_locations:,}"), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_card("arrow-down", "Entradas hoy", f"{movements_today['entradas']:,}"), unsafe_allow_html=True)
with col4:
    st.markdown(kpi_card("arrow-up", "Salidas hoy", f"{movements_today['salidas']:,}"), unsafe_allow_html=True)

st.markdown("<div style='margin: 1.75rem 0 0 0;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Alertas de stock mínimo
# ---------------------------------------------------------------------------
low_stock_products = get_products_low_stock()
if low_stock_products:
    with st.expander(f"Alertas de stock mínimo ({len(low_stock_products)})", expanded=True, icon=":material/warning:"):
        for product in low_stock_products:
            st.markdown(
                f"""
                <div style='display:flex; align-items:center; gap:0.75rem; background:#FFFBEB;
                             border:1px solid #FDE68A; border-radius:0.5rem; padding:0.65rem 0.9rem;
                             margin-bottom:0.5rem;'>
                    {svg_icon("alert", 16, "#B45309")}
                    <div style='font-size:0.85rem; color:#78350F;'>
                        <strong>{product['sku']} · {product['nombre']}</strong><br>
                        <span style='color:#92400E;'>Stock actual: {product['stock_total']} — Mínimo: {product['stock_minimo']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("<div style='margin: 1.75rem 0 0 0;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Últimos movimientos + Ocupación por zona
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    section_title("list", "Últimos movimientos")
    recent_movements = get_recent_movements(20)
    if recent_movements:
        df_movements = pd.DataFrame(recent_movements)
        df_movements["fecha_movimiento"] = df_movements["fecha_movimiento"].apply(format_date)
        df_movements_display = df_movements[
            ["fecha_movimiento", "tipo", "sku", "producto_nombre", "cantidad", "usuario_nombre", "estado"]
        ]
        df_movements_display.columns = ["Fecha", "Tipo", "SKU", "Producto", "Cantidad", "Usuario", "Estado"]

        def highlight_estado(val):
            if val == "Completado":
                return "background-color: #F0FDF4; color: #15803D; font-weight: 600;"
            elif val == "Pendiente":
                return "background-color: #FFFBEB; color: #B45309; font-weight: 600;"
            elif val == "Cancelado":
                return "background-color: #FEF2F2; color: #B91C1C; font-weight: 600;"
            return ""

        styled_df = df_movements_display.style.applymap(highlight_estado, subset=["Estado"])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay movimientos registrados.")

with col_right:
    section_title("bar-chart", "Ocupación por zona")
    occupation_by_zone = get_location_occupation_by_zone()
    if occupation_by_zone:
        df_zone = pd.DataFrame(occupation_by_zone)
        df_zone["libres"] = df_zone["total"] - df_zone["ocupadas"]
        df_zone_melt = df_zone.melt(
            id_vars=["zona"], value_vars=["ocupadas", "libres"], var_name="Estado", value_name="Cantidad"
        )

        fig = px.bar(
            df_zone_melt,
            x="zona",
            y="Cantidad",
            color="Estado",
            barmode="group",
            title="",
            color_discrete_map={"ocupadas": "#334155", "libres": "#E2E8F0"},
            template="plotly_white",
        )

        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                title=None,
                font=dict(size=11, color="#64748B"),
            ),
            xaxis=dict(showgrid=False, showline=False, tickfont=dict(size=11, color="#64748B")),
            yaxis=dict(
                showgrid=True,
                gridcolor="#F1F5F9",
                gridwidth=1,
                showline=False,
                tickfont=dict(size=11, color="#64748B"),
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="sans-serif"),
        )

        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>%{y} ubicaciones<extra></extra>",
            marker_line=dict(width=0),
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No hay datos de ocupación por zona.")