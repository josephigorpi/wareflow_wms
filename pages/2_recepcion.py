"""Página de Recepción e Inspección de WareFlow WMS."""

import streamlit as st

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar

require_auth()
require_permission("recepcion", "leer")

render_sidebar(current_page="recepcion")
render_navbar(titulo="Recepción e Inspección", icono="📦")

st.write("Contenido del módulo de recepción e inspección")
