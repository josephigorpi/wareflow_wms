"""Helpers para inicializar y gestionar st.session_state."""

import streamlit as st

SESSION_DEFAULTS = {
    "autenticado": False,
    "user_id": None,
    "username": None,
    "nombre_completo": None,
    "rol_id": None,
    "rol_nombre": None,
    "permisos": {},
}


def init_session() -> None:
    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session()
