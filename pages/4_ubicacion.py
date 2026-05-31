"""Página de Codificación y Ubicación de WareFlow WMS."""

import streamlit as st

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar

require_auth()
require_permission("ubicacion", "leer")

render_sidebar(current_page="ubicacion")
render_navbar(titulo="Codificación y Ubicación", icono="🗺")

st.write("Contenido del módulo de codificación y ubicación")
