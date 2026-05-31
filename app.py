"""Punto de entrada principal del sistema WareFlow WMS."""

import streamlit as st

from components.styles import load_global_styles
from database.db_manager import initialize_database
from pages import __init__  # noqa: F401

# Inicializar la base de datos si no existe
try:
    initialize_database()
except Exception:
    pass  # Si ya existe, no hacer nada

st.set_page_config(page_title="WareFlow WMS", layout="wide")
load_global_styles()

st.markdown("# WareFlow WMS")
st.markdown("Bienvenido a WareFlow WMS. Seleccione un módulo desde el menú lateral.")
