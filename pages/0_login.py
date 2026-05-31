"""Página de inicio de sesión de WareFlow WMS."""

import streamlit as st

from components.alerts import alert_error, alert_success
from core.auth import login
from core.session import init_session

init_session()

if st.session_state.get("autenticado"):
    st.success(f"Sesión activa como {st.session_state.get('nombre_completo') or st.session_state.get('username')}.")
    st.info("Use el menú lateral para continuar.")
    st.stop()

st.title("Login")
username = st.text_input("Usuario")
password = st.text_input("Contraseña", type="password")

if st.button("Ingresar"):
    if login(username, password):
        alert_success(f"Bienvenido, {st.session_state.get('nombre_completo') or username}.")
        st.info("Use el menú lateral para continuar.")
    else:
        alert_error("Usuario o contraseña incorrectos.")
