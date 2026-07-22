"""Menú lateral con navegación para WareFlow WMS."""

import streamlit as st

from core.auth import logout


# key interno -> (icono material, etiqueta visible, página destino)
MENU_ITEMS = [
    ("dashboard", "dashboard", "Dashboard", "1_dashboard"),
    ("recepcion", "move_to_inbox", "Recepción", "2_recepcion"),
    ("inventario", "inventory_2", "Inventario", "3_inventario"),
    ("ubicacion", "pin_drop", "Ubicación", "4_ubicacion"),
    ("picking", "shopping_cart", "Picking", "5_picking"),
    ("despacho", "local_shipping", "Despacho", "8_despacho"),
    ("reportes", "bar_chart", "Reportes", "6_reportes"),
]


def _inject_sidebar_styles() -> None:
    st.sidebar.markdown(
        """
        <style>
        /* --- Reduce el espacio vacío superior del sidebar --- */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 1.25rem !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            gap: 0.35rem !important;
        }

        /* --- Navegación: botones tipo "nav link" --- */
        .st-key-sidebar_nav div[data-testid="stButton"] button {
            width: 100% !important;
            justify-content: flex-start !important;
            text-align: left !important;
            border-radius: 0.5rem !important;
            padding: 0.55rem 0.85rem !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            margin-bottom: 0.15rem !important;
            transition: background-color 0.15s ease, color 0.15s ease !important;
        }

        /* Item inactivo: transparente, texto tenue */
        .st-key-sidebar_nav div[data-testid="stButton"] button[kind="secondary"] {
            background-color: transparent !important;
            border: 1px solid transparent !important;
            color: rgba(255,255,255,0.65) !important;
        }
        .st-key-sidebar_nav div[data-testid="stButton"] button[kind="secondary"]:hover {
            background-color: rgba(255,255,255,0.07) !important;
            color: #FFFFFF !important;
            border: 1px solid transparent !important;
        }
        .st-key-sidebar_nav div[data-testid="stButton"] button[kind="secondary"] p {
            color: inherit !important;
            font-weight: 500 !important;
        }

        /* Item activo: fondo acento sutil + borde izquierdo */
        .st-key-sidebar_nav div[data-testid="stButton"] button[kind="primary"] {
            background-color: rgba(59, 130, 246, 0.16) !important;
            border: 1px solid rgba(59, 130, 246, 0.25) !important;
            border-left: 3px solid #60A5FA !important;
            color: #FFFFFF !important;
            box-shadow: none !important;
        }
        .st-key-sidebar_nav div[data-testid="stButton"] button[kind="primary"]:hover {
            background-color: rgba(59, 130, 246, 0.22) !important;
        }
        .st-key-sidebar_nav div[data-testid="stButton"] button[kind="primary"] p {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }

        /* Iconos Material dentro de los botones de nav */
        .st-key-sidebar_nav div[data-testid="stButton"] button span[data-testid="stIconMaterial"] {
            font-size: 1.05rem !important;
            opacity: 0.9;
        }

        /* --- Botón de cerrar sesión: aislado del estilo de nav --- */
        .st-key-sidebar_logout div[data-testid="stButton"] button {
            width: 100% !important;
            background-color: rgba(239, 68, 68, 0.15) !important;
            border: 1px solid rgba(239, 68, 68, 0.25) !important;
            border-radius: 0.5rem !important;
            padding: 0.55rem 1rem !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            transition: all 0.15s ease !important;
        }
        .st-key-sidebar_logout div[data-testid="stButton"] button:hover {
            background-color: rgba(239, 68, 68, 0.25) !important;
            border: 1px solid rgba(239, 68, 68, 0.4) !important;
        }
        .st-key-sidebar_logout div[data-testid="stButton"] button p,
        .st-key-sidebar_logout div[data-testid="stButton"] button span[data-testid="stIconMaterial"] {
            color: #FCA5A5 !important;
        }
        .st-key-sidebar_logout div[data-testid="stButton"] button:hover p,
        .st-key-sidebar_logout div[data-testid="stButton"] button:hover span[data-testid="stIconMaterial"] {
            color: #FFFFFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(current_page: str = "") -> None:
    _inject_sidebar_styles()

    # Logo y título
    st.sidebar.markdown(
        """
        <div style='text-align: center; padding: 0.25rem 0 0.75rem 0;'>
            <h1 style='margin: 0; font-size: 1.5rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.5px;'>
                WareFlow
            </h1>
            <p style='margin: 0.5rem 0 0 0; font-size: 0.75rem; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 1px;'>
                WMS System
            </p>
        </div>
        """,
        unsafe_allow_html=True,
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
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # --- Menú de navegación ---
    permisos = st.session_state.get("permisos", {})
    visible_items = [
        (key, icon, label, page)
        for key, icon, label, page in MENU_ITEMS
        if "leer" in permisos.get(key, [])
    ]

    if not visible_items:
        st.sidebar.info("No tiene acceso a módulos disponibles.")
        return

    with st.sidebar.container(key="sidebar_nav"):
        for key, icon, label, page in visible_items:
            is_active = key == current_page
            clicked = st.button(
                label,
                icon=f":material/{icon}:",
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            )
            if clicked and not is_active:
                st.session_state["current_page"] = label
                try:
                    st.switch_page(f"pages/{page}.py")
                except Exception:
                    try:
                        st.experimental_set_query_params(page=page)
                        st.experimental_rerun()
                    except Exception:
                        pass

    # --- Botón de cerrar sesión ---
    st.sidebar.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    with st.sidebar.container(key="sidebar_logout"):
        if st.button(
            "Cerrar Sesión",
            icon=":material/logout:",
            use_container_width=True,
            key="btn_logout",
        ):
            logout()
            st.rerun()