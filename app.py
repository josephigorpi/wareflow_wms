"""Punto de entrada principal del sistema WareFlow WMS."""

import streamlit as st

from components.styles import load_global_styles
from core.auth import is_authenticated
from core.session import init_session
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

# Inicializar sesión y verificar autenticación
init_session()

if not is_authenticated():
    try:
        st.switch_page("pages/0_login.py")
    except AttributeError:
        st.markdown(
            """
            <meta http-equiv="refresh" content="0; url=/pages/0_login" />
            <script>
                window.location.href = "/pages/0_login";
            </script>
            """,
            unsafe_allow_html=True
        )
        st.stop()
else:
    # Si está autenticado, redirigir al dashboard
    try:
        st.switch_page("pages/1_dashboard.py")
    except AttributeError:
        st.markdown(
            """
            <meta http-equiv="refresh" content="0; url=/pages/1_dashboard" />
            <script>
                window.location.href = "/pages/1_dashboard";
            </script>
            """,
            unsafe_allow_html=True
        )
        st.stop()
