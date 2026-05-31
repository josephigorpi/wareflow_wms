"""Página de Picking y Despacho de WareFlow WMS."""

import streamlit as st

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar

require_auth()
require_permission("picking", "leer")

render_sidebar(current_page="picking")
render_navbar(titulo="Picking y Despacho", icono="🚚")

st.write("Contenido del módulo de picking y despacho")
