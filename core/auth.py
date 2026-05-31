"""Módulo de autenticación para WareFlow WMS."""

import datetime

import streamlit as st

from core.permissions import load_permissions
from core.session import init_session, reset_session
from database.connection import get_connection
from services.user_service import get_user_by_username
from utils.passwords import verify_password


def login(username: str, password: str) -> bool:
    init_session()

    user = get_user_by_username(username)
    if not user:
        return False

    password_hash = user["password_hash"]
    if not verify_password(password, password_hash):
        return False

    if user.get("activo") != 1:
        return False

    st.session_state["autenticado"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["username"] = user["username"]
    st.session_state["nombre_completo"] = user.get("nombre_completo")
    st.session_state["rol_id"] = user.get("rol_id")
    st.session_state["rol_nombre"] = user.get("rol_nombre") or ""
    st.session_state["permisos"] = load_permissions(st.session_state["rol_nombre"])

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET ultimo_acceso = ? WHERE id = ?",
            (datetime.datetime.utcnow().isoformat(), user["id"]),
        )
        conn.commit()
    except Exception:
        pass

    return True


def logout() -> None:
    reset_session()


def is_authenticated() -> bool:
    init_session()
    return st.session_state.get("autenticado", False)


def require_auth() -> None:
    init_session()
    if not is_authenticated():
        st.warning("Por favor, inicie sesión para acceder al sistema.")
        st.stop()


def get_current_user() -> dict:
    return {
        "user_id": st.session_state.get("user_id"),
        "username": st.session_state.get("username"),
        "rol_id": st.session_state.get("rol_id"),
        "rol_nombre": st.session_state.get("rol_nombre"),
    }
