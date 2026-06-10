"""Página de Codificación y Ubicación de WareFlow WMS."""

import pandas as pd
import streamlit as st

from components.alerts import alert_error, alert_success, alert_warning
from components.forms import form_submit_button, input_number, input_select, input_text
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.tables import render_table
from core.auth import require_auth
from core.permissions import require_permission
from services.location_service import (
    create_location,
    delete_location,
    get_all_locations,
    get_all_zones,
    get_location_by_id,
    update_location,
)

# ── Autenticación y permisos ──────────────────────────────────────────────────

require_auth()
require_permission("ubicacion", "leer")

can_write = "escribir" in st.session_state.get("permisos", {}).get("ubicacion", [])

# ── Navegación ────────────────────────────────────────────────────────────────

render_sidebar(current_page="ubicacion")
render_navbar(titulo="Codificación y Ubicación", icono="🗺")

# ── Estado de sesión ──────────────────────────────────────────────────────────

for key, default in {
    "ub_edit_id": None,
    "ub_delete_id": None,
    "ub_show_form": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Datos de referencia ───────────────────────────────────────────────────────

zones = get_all_zones()
zone_options = {z["nombre"]: z["id"] for z in zones}
zone_labels = ["Todas las zonas"] + list(zone_options.keys())

# ── Filtros ───────────────────────────────────────────────────────────────────

col_f1, col_f2, col_f3 = st.columns([2, 3, 1])

with col_f1:
    selected_zone_label = st.selectbox(
        "Zona",
        options=zone_labels,
        key="ub_filter_zona",
    )

with col_f2:
    search_term = st.text_input(
        "Buscar por código",
        placeholder="Ej: Z-ALM-A01-01",
        key="ub_filter_search",
    )

with col_f3:
    st.markdown("<br>", unsafe_allow_html=True)
    if can_write:
        if st.button("➕ Nueva ubicación", use_container_width=True):
            st.session_state["ub_show_form"] = True
            st.session_state["ub_edit_id"] = None
            st.session_state["ub_delete_id"] = None

# ── Formulario de alta / edición ──────────────────────────────────────────────

show_form = st.session_state["ub_show_form"] or st.session_state["ub_edit_id"] is not None

if can_write and show_form:
    edit_id = st.session_state["ub_edit_id"]
    is_edit = edit_id is not None

    form_title = f"✏️ Editar ubicación" if is_edit else "➕ Nueva ubicación"

    with st.expander(form_title, expanded=True):

        # Prellenar valores si es edición
        prefill = {}
        if is_edit:
            prefill = get_location_by_id(edit_id) or {}

        def _zone_index_for_prefill():
            if not is_edit or not prefill:
                return 0
            for i, z in enumerate(zones):
                if z["id"] == prefill.get("zona_id"):
                    return i
            return 0

        with st.form(key="ub_form"):
            fc1, fc2 = st.columns(2)

            with fc1:
                zona_label = st.selectbox(
                    "Zona *",
                    options=list(zone_options.keys()),
                    index=_zone_index_for_prefill(),
                )
                pasillo = input_text(
                    "Pasillo *",
                    key="ub_form_pasillo",
                )
                nivel = input_text(
                    "Nivel *",
                    key="ub_form_nivel",
                )
                capacidad_kg = st.number_input(
                    "Capacidad (kg)",
                    min_value=0.0,
                    step=0.1,
                    value=float(prefill.get("capacidad_kg") or 0.0),
                    key="ub_form_cap_kg",
                )

            with fc2:
                codigo = input_text(
                    "Código *",
                    key="ub_form_codigo",
                )
                estante = input_text(
                    "Estante *",
                    key="ub_form_estante",
                )
                posicion = input_text(
                    "Posición *",
                    key="ub_form_posicion",
                )
                capacidad_m3 = st.number_input(
                    "Capacidad (m³)",
                    min_value=0.0,
                    step=0.01,
                    value=float(prefill.get("capacidad_m3") or 0.0),
                    key="ub_form_cap_m3",
                )

            fb1, fb2 = st.columns([1, 5])
            with fb1:
                submitted = form_submit_button(
                    label="Guardar" if is_edit else "Crear",
                    key="ub_form_submit",
                )
            with fb2:
                cancelled = st.form_submit_button("Cancelar")

        # Nota: los valores de st.text_input dentro de st.form solo están
        # disponibles tras el submit; recuperamos por session_state de Streamlit.
        if submitted:
            zona_id = zone_options.get(zona_label)
            cap_kg = capacidad_kg if capacidad_kg > 0 else None
            cap_m3 = capacidad_m3 if capacidad_m3 > 0 else None

            try:
                if is_edit:
                    update_location(
                        location_id=edit_id,
                        zona_id=zona_id,
                        codigo=codigo,
                        pasillo=pasillo,
                        estante=estante,
                        nivel=nivel,
                        posicion=posicion,
                        capacidad_kg=cap_kg,
                        capacidad_m3=cap_m3,
                    )
                    alert_success(f"Ubicación **{codigo}** actualizada correctamente.")
                else:
                    new_id = create_location(
                        zona_id=zona_id,
                        codigo=codigo,
                        pasillo=pasillo,
                        estante=estante,
                        nivel=nivel,
                        posicion=posicion,
                        capacidad_kg=cap_kg,
                        capacidad_m3=cap_m3,
                    )
                    alert_success(f"Ubicación **{codigo}** creada con ID {new_id}.")

                st.session_state["ub_show_form"] = False
                st.session_state["ub_edit_id"] = None
                st.rerun()

            except ValueError as exc:
                alert_error(str(exc))

        if cancelled:
            st.session_state["ub_show_form"] = False
            st.session_state["ub_edit_id"] = None
            st.rerun()

# ── Confirmación de eliminación ───────────────────────────────────────────────

delete_id = st.session_state.get("ub_delete_id")
if delete_id is not None:
    loc = get_location_by_id(delete_id)
    if loc:
        alert_warning(
            f"¿Eliminar la ubicación **{loc['codigo']}** ({loc['zona_nombre']})? "
            "Esta acción no se puede deshacer."
        )
        cd1, cd2, _ = st.columns([1, 1, 6])
        with cd1:
            if st.button("✅ Confirmar", key="ub_confirm_delete"):
                try:
                    delete_location(delete_id)
                    alert_success(f"Ubicación **{loc['codigo']}** eliminada.")
                    st.session_state["ub_delete_id"] = None
                    st.rerun()
                except ValueError as exc:
                    alert_error(str(exc))
                    st.session_state["ub_delete_id"] = None
        with cd2:
            if st.button("❌ Cancelar", key="ub_cancel_delete"):
                st.session_state["ub_delete_id"] = None
                st.rerun()

st.markdown("---")

# ── Tabla de ubicaciones ──────────────────────────────────────────────────────

filter_zona_id = zone_options.get(selected_zone_label) if selected_zone_label != "Todas las zonas" else None
locations = get_all_locations(zona_id=filter_zona_id, search_term=search_term)

if not locations:
    alert_info_msg = "No se encontraron ubicaciones"
    if selected_zone_label != "Todas las zonas" or search_term:
        alert_info_msg += " con los filtros aplicados"
    alert_warning(alert_info_msg + ".")
else:
    # Construir DataFrame para visualización
    rows = []
    for loc in locations:
        rows.append({
            "ID": loc["id"],
            "Código": loc["codigo"],
            "Zona": loc["zona_nombre"],
            "Pasillo": loc["pasillo"],
            "Estante": loc["estante"],
            "Nivel": loc["nivel"],
            "Posición": loc["posicion"],
            "Cap. Kg": loc["capacidad_kg"] if loc["capacidad_kg"] else "—",
            "Cap. m³": loc["capacidad_m3"] if loc["capacidad_m3"] else "—",
            "Estado": "🔴 Ocupada" if loc["ocupada"] else "🟢 Libre",
        })

    df = pd.DataFrame(rows)

    st.caption(f"{len(locations)} ubicación(es) encontrada(s)")
    render_table(df)

    # ── Acciones por fila (solo con permiso de escritura) ─────────────────────

    if can_write:
        st.markdown("**Acciones**")
        ac1, ac2, ac3 = st.columns([2, 1, 1])

        with ac1:
            location_labels = [f"{loc['codigo']} — {loc['zona_nombre']}" for loc in locations]
            selected_label = st.selectbox(
                "Seleccionar ubicación",
                options=location_labels,
                key="ub_action_select",
                label_visibility="collapsed",
            )

        selected_index = location_labels.index(selected_label) if selected_label else 0
        selected_loc = locations[selected_index]

        with ac2:
            if st.button("✏️ Editar", key="ub_btn_edit", use_container_width=True):
                st.session_state["ub_edit_id"] = selected_loc["id"]
                st.session_state["ub_show_form"] = False
                st.session_state["ub_delete_id"] = None
                st.rerun()

        with ac3:
            if st.button("🗑️ Eliminar", key="ub_btn_delete", use_container_width=True):
                st.session_state["ub_delete_id"] = selected_loc["id"]
                st.session_state["ub_edit_id"] = None
                st.session_state["ub_show_form"] = False
                st.rerun()
