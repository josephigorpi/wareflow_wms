"""Verificación de permisos basados en roles para WareFlow WMS."""

import streamlit as st

from config.roles_permissions import ROLES_PERMISSIONS


def load_permissions(rol_nombre: str) -> dict:
    return ROLES_PERMISSIONS.get(rol_nombre, {})


def require_permission(modulo: str, accion: str) -> None:
    permisos = st.session_state.get("permisos", {})
    modulo_permisos = permisos.get(modulo, [])
    if accion not in modulo_permisos:
        st.warning("No tiene permisos suficientes para acceder a este módulo.")
        st.stop()
