"""Página de Reportes y KPIs de WareFlow WMS."""

import streamlit as st

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar

require_auth()
require_permission("reportes", "leer")

render_sidebar(current_page="reportes")
render_navbar(titulo="Reportes y KPIs", icono="📈")

st.write("Contenido del módulo de reportes y KPIs")
