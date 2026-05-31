"""Dashboard principal de WareFlow WMS."""

import streamlit as st

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar

require_auth()
require_permission("dashboard", "leer")

render_sidebar(current_page="dashboard")
render_navbar(titulo="Dashboard", subtitulo="Visión general del sistema", icono="📊")

st.markdown(
    """
    <div class="dashboard-welcome">
        <h2>Bienvenido a WareFlow WMS</h2>
        <p>Esta área mostrará métricas clave, accesos rápidos y un resumen de las operaciones del almacén.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
col1.markdown(
    """
    <div class="dashboard-card">
        <h3>Productos activos</h3>
        <p>No hay datos disponibles aún.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
col2.markdown(
    """
    <div class="dashboard-card">
        <h3>Movimientos recientes</h3>
        <p>Aún no se han registrado movimientos.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
col3.markdown(
    """
    <div class="dashboard-card">
        <h3>Ubicaciones libres</h3>
        <p>Revisa el módulo de ubicación para ver el estado actual.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
