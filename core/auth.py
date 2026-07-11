"""Módulo de autenticación para WareFlow WMS."""

import datetime

import streamlit as st

from core.permissions import load_permissions
from core.session import init_session, reset_session
from database.connection import get_connection
from services.user_service import get_user_by_username
from utils.passwords import verify_password


def login(username: str, password: str) -> bool:
    """
    Autentica a un usuario en el sistema.
    
    Args:
        username (str): Nombre de usuario
        password (str): Contraseña del usuario
        
    Returns:
        bool: True si la autenticación fue exitosa, False en caso contrario
    """
    init_session()

    # Validar que los campos no estén vacíos
    if not username or not password:
        return False

    user = get_user_by_username(username)
    if not user:
        return False

    password_hash = user.get("password_hash")
    if not password_hash or not verify_password(password, password_hash):
        return False

    if user.get("activo") != 1:
        return False

    # Establecer sesión
    st.session_state["autenticado"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["username"] = user["username"]
    st.session_state["nombre_completo"] = user.get("nombre_completo", username)
    st.session_state["rol_id"] = user.get("rol_id")
    st.session_state["rol_nombre"] = user.get("rol_nombre") or ""
    st.session_state["permisos"] = load_permissions(st.session_state["rol_nombre"])

    # Registrar último acceso
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET ultimo_acceso = ? WHERE id = ?",
            (datetime.datetime.utcnow().isoformat(), user["id"]),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        # Log del error pero no interrumpir el flujo
        print(f"Error al actualizar último acceso: {e}")

    return True


def logout() -> None:
    """
    Cierra la sesión del usuario actual y redirecciona al login.
    """
    # Limpiar el estado de sesión
    reset_session()
    
    # Mostrar mensaje de éxito
    st.success("✅ Sesión cerrada exitosamente")
    
    # Redireccionar a la página de login usando query parameters
    # Opción 1: Usar st.switch_page (Streamlit 1.36.0+)
    try:
        #st.switch_page("app.py")
        st.switch_page("pages/0_login.py")
    except AttributeError:
        # Opción 2: Fallback para versiones anteriores
        st.markdown(
            """
            <meta http-equiv="refresh" content="1; url=/" />
            <script>
                window.location.href = "/";
            </script>
            """,
            unsafe_allow_html=True
        )
        st.info("Redirigiendo al login...")
        st.stop()


def logout_simple() -> None:
    """
    Versión simple de logout sin redirección automática.
    Útil cuando se quiere controlar la redirección desde la UI.
    """
    reset_session()
    st.success("✅ Sesión cerrada exitosamente")


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
