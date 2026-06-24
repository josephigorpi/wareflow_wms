"""Menú lateral con navegación para WareFlow WMS."""

import streamlit as st

from core.auth import logout


def render_sidebar(current_page: str = "") -> None:
    st.sidebar.title("WareFlow WMS")
    st.sidebar.markdown(
        f"**Usuario:** {st.session_state.get('nombre_completo') or st.session_state.get('username', 'Invitado')}"
    )
    st.sidebar.markdown(
        f"**Rol:** {st.session_state.get('rol_nombre', 'Sin rol')}"
    )
    st.sidebar.divider()

    if st.sidebar.button("Cerrar sesión"):
        logout()
        st.rerun()

    st.sidebar.markdown("---")
    permisos = st.session_state.get("permisos", {})

    menu_items = [
        ("dashboard", "Dashboard"),
        ("recepcion", "Recepción"),
        ("inspeccion", "Inspección"),
        ("inventario", "Inventario"),
        ("ubicacion", "Ubicación"),
        ("picking", "Picking"),
        ("reportes", "Reportes"),
    ]

    visible_items = [label for key, label in menu_items if "leer" in permisos.get(key, [])]
    label_to_page = {
        "Dashboard": "1_dashboard",
        "Recepción": "2_recepcion",
        "Inspección": "7_inspeccion",
        "Inventario": "3_inventario",
        "Ubicación": "4_ubicacion",
        "Picking": "5_picking",
        "Reportes": "6_reportes",
    }

    if not visible_items:
        st.sidebar.info("No tiene acceso a módulos disponibles.")
        return

    selected_label = visible_items[0]
    for key, label in menu_items:
        if key == current_page and label in visible_items:
            selected_label = label
            break

    try:
        import streamlit_antd_components as sac

        selected = sac.menu(
            items=visible_items,
            default_value=selected_label,
            key="sidebar_menu",
            mode="vertical",
            theme="light",
        )
    except Exception:
        selected = st.sidebar.radio(
            "Navegación",
            visible_items,
            index=visible_items.index(selected_label),
            key="sidebar_menu_fallback",
        )

    selected = selected if selected else selected_label
    page_to_load = label_to_page.get(selected)
    if page_to_load and selected_label != selected:
        try:
            st.switch_page(page_to_load)
        except Exception:
            try:
                st.experimental_set_query_params(page=page_to_load)
                st.experimental_rerun()
            except Exception:
                pass
