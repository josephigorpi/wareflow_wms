"""Menú lateral con navegación para WareFlow WMS."""

import streamlit as st

from core.auth import logout


def render_sidebar(current_page: str = "") -> None:
    # Logo y título
    st.sidebar.markdown(
        """
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='margin: 0; font-size: 1.5rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.5px;'>
                📦 WareFlow
            </h1>
            <p style='margin: 0.5rem 0 0 0; font-size: 0.75rem; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 1px;'>
                WMS System
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Información del usuario
    st.sidebar.markdown(
        f"""
        <div style='background: rgba(255,255,255,0.1); border-radius: 0.5rem; padding: 1rem; margin: 1rem 0;'>
            <p style='margin: 0 0 0.25rem 0; font-size: 0.75rem; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.5px;'>
                Usuario
            </p>
            <p style='margin: 0 0 0.5rem 0; font-size: 0.95rem; font-weight: 600; color: #FFFFFF;'>
                {st.session_state.get('nombre_completo') or st.session_state.get('username', 'Invitado')}
            </p>
            <p style='margin: 0; font-size: 0.75rem; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.5px;'>
                Rol
            </p>
            <p style='margin: 0.25rem 0 0 0; font-size: 0.875rem; color: rgba(255,255,255,0.9);'>
                {st.session_state.get('rol_nombre', 'Sin rol')}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    # Menú de navegación
    permisos = st.session_state.get("permisos", {})

    menu_items = [
        ("dashboard", "📊", "Dashboard"),
        ("recepcion", "📥", "Recepción"),
        ("inventario", "📦", "Inventario"),
        ("ubicacion", "📍", "Ubicación"),
        ("picking", "🛒", "Picking"),
        ("despacho", "📤", "Despacho"),
        ("reportes", "📈", "Reportes"),
    ]

    visible_items = [(icon, label) for key, icon, label in menu_items if "leer" in permisos.get(key, [])]
    label_to_page = {
        "Dashboard": "1_dashboard",
        "Recepción": "2_recepcion",
        "Inventario": "3_inventario",
        "Ubicación": "4_ubicacion",
        "Picking": "5_picking",
        "Despacho": "8_despacho",
        "Reportes": "6_reportes",
    }

    if not visible_items:
        st.sidebar.info("No tiene acceso a módulos disponibles.")
        return

    # Determinar el label y el icono seleccionado basado en current_page
    selected_label = visible_items[0][1]
    selected_icon = visible_items[0][0]
    for key, icon, label in menu_items:
        if key == current_page and (icon, label) in visible_items:
            selected_label = label
            selected_icon = icon
            break

    # Crear opciones para el radio con iconos
    menu_options = [f"{icon} {label}" for icon, label in visible_items]
    
    # Encontrar el índice correcto del item seleccionado
    selected_option = f"{selected_icon} {selected_label}"
    try:
        default_index = menu_options.index(selected_option)
    except ValueError:
        default_index = 0
    
    selected = st.sidebar.radio(
        "Navegación",
        menu_options,
        index=default_index,
        key="sidebar_menu",
        label_visibility="collapsed",
    )

    # Extraer solo el label (sin icono) para la navegación
    selected_clean = selected.split(" ", 1)[1] if " " in selected else selected
    
    page_to_load = label_to_page.get(selected_clean)
    if page_to_load and selected_label != selected_clean:
        st.session_state["current_page"] = selected_clean
        try:
            st.switch_page(f"pages/{page_to_load}.py")
        except Exception:
            try:
                st.experimental_set_query_params(page=page_to_load)
                st.experimental_rerun()
            except Exception:
                pass

    # Botón de cerrar sesión al final
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    st.sidebar.markdown(
        """
        <style>
        div[data-testid="stSidebar"] > div > div > button[kind="secondary"] {
            background-color: rgba(239, 68, 68, 0.2) !important;
            color: #FCA5A5 !important;
            border: none !important;
            border-radius: 0.5rem !important;
            padding: 0.5rem 1rem !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stSidebar"] > div > div > button[kind="secondary"]:hover {
            background-color: rgba(239, 68, 68, 0.3) !important;
            color: #FFFFFF !important;
            border: none !important;
        }
        div[data-testid="stSidebar"] > div > div > button[kind="secondary"]:focus {
            background-color: rgba(239, 68, 68, 0.3) !important;
            color: #FFFFFF !important;
            border: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        logout()
        st.rerun()
