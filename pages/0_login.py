"""Página de inicio de sesión de WareFlow WMS."""

import time
import streamlit as st

from components.alerts import alert_error, alert_success
from core.auth import login
from core.session import init_session

init_session()

# Si ya está autenticado, redirigir al dashboard
if st.session_state.get("autenticado"):
    st.success(f"Sesión activa como {st.session_state.get('nombre_completo') or st.session_state.get('username')}.")
    st.info("Redirigiendo al dashboard...")
    time.sleep(1)
    
    try:
        st.switch_page("pages/1_dashboard.py")
    except AttributeError:
        # Fallback para versiones anteriores de Streamlit
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

st.title("📦 WareFlow WMS - Inicio de Sesión")

# Mostrar mensaje de bienvenida
st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <p style='color: #666;'>Sistema de Gestión de Almacenes</p>
    </div>
""", unsafe_allow_html=True)

# Formulario de login
with st.form("login_form"):
    username = st.text_input("👤 Usuario", placeholder="Ingrese su nombre de usuario")
    password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingrese su contraseña")
    
    submitted = st.form_submit_button("🚀 Ingresar", use_container_width=True)
    
    if submitted:
        if not username or not password:
            alert_error("Por favor, complete todos los campos.")
        else:
            if login(username, password):
                alert_success(f"✅ ¡Bienvenido, {st.session_state.get('nombre_completo') or username}!")
                st.info("🔄 Redirigiendo al dashboard...")
                
                # Pequeña pausa para que el usuario vea el mensaje de éxito
                time.sleep(1.5)
                
                # Redirigir al dashboard
                try:
                    st.switch_page("pages/1_dashboard.py")
                except AttributeError:
                    # Fallback para versiones anteriores
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
                alert_error("❌ Usuario o contraseña incorrectos.")

# Pie de página
st.divider()
st.caption("© 2024 WareFlow WMS - Todos los derechos reservados")
