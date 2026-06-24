"""Página de Control de Inventario de WareFlow WMS."""

import streamlit as st

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar

require_auth()
require_permission("inventario", "leer")

render_sidebar(current_page="inventario")
render_navbar(titulo="Control de Inventario", icono="📋")

st.write("Contenido del módulo de control de inventario")

moreno
