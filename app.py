"""Punto de entrada principal del sistema WareFlow WMS."""

import streamlit as st

from components.styles import load_global_styles
from database.db_manager import reset_database, execute_script
from pages import __init__  # noqa: F401

# Reinicializar la base de datos (elimina y recrea con nuevos datos)
try:
    reset_database()
    execute_script("database/seed_data.sql")
except Exception as e:
    st.error(f"Error al inicializar la base de datos: {e}")

st.set_page_config(page_title="WareFlow WMS", layout="wide")
load_global_styles()

st.markdown("# WareFlow WMS")
st.markdown("Bienvenido a WareFlow WMS. Seleccione un módulo desde el menú lateral.")
