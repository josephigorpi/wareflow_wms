"""Página de inicio de sesión de WareFlow WMS."""

import time
import streamlit as st

from core.auth import login
from core.session import init_session

init_session()

# Configuración de la página
st.set_page_config(page_title="Login - WareFlow WMS", page_icon="📦", layout="centered")

# Si ya está autenticado, redirigir al dashboard
if st.session_state.get("autenticado"):
    st.success(f"Sesión activa como {st.session_state.get('nombre_completo') or st.session_state.get('username')}.")
    st.info("Redirigiendo al dashboard...")
    time.sleep(1)
    
    try:
        st.switch_page("pages/1_dashboard.py")
    except AttributeError:
        st.markdown(
            """
            <meta http-equiv="refresh" content="1; url=/pages/1_dashboard" />
            <script>
                window.location.href = "/pages/1_dashboard";
            </script>
            """,
            unsafe_allow_html=True
        )
        st.stop()

# CSS personalizado para el login
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #1E3A5F 0%, #2D4A6F 100%);
    }
    [data-testid="stForm"] {
        background: #FFFFFF;
        border-radius: 0.75rem;
        padding: 2.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid #E2E8F0;
    }
    [data-testid="stForm"] > div {
        gap: 1.5rem;
    }
    [data-testid="stTextInput"] > div > div > input {
        background-color: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-radius: 0.5rem;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
    }
    [data-testid="stTextInput"] > div > div > input:focus {
        border-color: #1E3A5F;
        box-shadow: 0 0 0 2px rgba(30, 58, 95, 0.1);
    }
    [data-testid="stFormSubmitButton"] > button {
        background: #1E3A5F;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.875rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        background: #2D4A6F;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Contenedor centrado
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Logo y título
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='margin: 0; font-size: 2.5rem; font-weight: 700; color: #FFFFFF; letter-spacing: -1px;'>
                📦 WareFlow
            </h1>
            <p style='margin: 0.5rem 0 0 0; font-size: 1rem; color: rgba(255,255,255,0.8); font-weight: 400;'>
                Sistema de Gestión de Almacenes
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Formulario de login
    with st.form("login_form"):
        st.markdown("<br>", unsafe_allow_html=True)
        username = st.text_input("Usuario", placeholder="Ingrese su nombre de usuario")
        password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Iniciar Sesión", use_container_width=True)
        
        if submitted:
            if not username or not password:
                st.error("❌ Por favor, complete todos los campos.")
            else:
                if login(username, password):
                    st.success(f"✅ ¡Bienvenido, {st.session_state.get('nombre_completo') or username}!")
                    st.info("🔄 Redirigiendo al dashboard...")
                    
                    time.sleep(1.5)
                    
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
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
    
    # Pie de página
    st.markdown(
        """
        <div style='text-align: center; margin-top: 2rem;'>
            <p style='margin: 0; color: rgba(255,255,255,0.6); font-size: 0.875rem;'>
                © 2024 WareFlow WMS - Todos los derechos reservados
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
