"""Página de Despacho de WareFlow WMS."""

import streamlit as st
import pandas as pd

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from services.movement_service import get_movements_by_type, create_despacho

require_auth()
require_permission("despacho", "leer")

render_sidebar(current_page="despacho")
render_navbar(titulo="Despacho", subtitulo="Consolidación y envío de pedidos", icono="🚚")

# KPI Cards
picking_orders = get_movements_by_type("PICKING", limit=100)
completed_picking = [o for o in picking_orders if o["estado"] == "COMPLETADO"]
despachos = get_movements_by_type("DESPACHO", limit=100)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.metric("📦 Picking Listos", f"{len(completed_picking):,}")

with col2:
    st.metric("🚚 Despachos Hoy", f"{len(despachos):,}")

with col3:
    st.metric("📋 Total Despachos", f"{len(despachos):,}")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs modernos
tab1, tab2, tab3 = st.tabs(["📦 Consolidar Pedidos", "📄 Documentos", "📊 Historial"])

# Tab 1: Consolidar Pedidos
with tab1:
    st.markdown("### 📦 Consolidar Pedidos para Despacho")
    
    if not completed_picking:
        st.info("ℹ️ No hay picking completados para consolidar.")
    else:
        st.markdown("**Picking Completados Disponibles**")
        
        df_picking = pd.DataFrame(completed_picking)
        df_picking["Seleccionar"] = False
        
        edited_df = st.data_editor(
            df_picking[["Seleccionar", "id", "sku", "producto_nombre", "cantidad", "origen_codigo", "fecha_movimiento"]],
            column_config={
                "Seleccionar": st.column_config.CheckboxColumn("Seleccionar", default=False),
                "id": "ID Orden",
                "sku": "SKU",
                "producto_nombre": "Producto",
                "cantidad": "Cantidad",
                "origen_codigo": "Ubicación",
                "fecha_movimiento": "Fecha"
            },
            disabled=["id", "sku", "producto_nombre", "cantidad", "origen_codigo", "fecha_movimiento"],
            hide_index=True,
            use_container_width=True
        )
        
        selected_ids = edited_df[edited_df["Seleccionar"]]["id"].tolist()
        
        if selected_ids:
            st.markdown(f"**Pedidos Seleccionados:** {len(selected_ids)}")
            
            with st.form("form_despacho"):
                col1, col2 = st.columns(2, gap="large")
                
                with col1:
                    referencia = st.text_input("Referencia del Despacho", placeholder="Ej: DESP-2024-001")
                
                with col2:
                    observaciones = st.text_area("Observaciones (opcional)", placeholder="Detalles adicionales...")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("🚚 Registrar Despacho", use_container_width=True, type="primary")
                
                if submitted:
                    try:
                        usuario_id = st.session_state.get("usuario_id")
                        create_despacho(
                            movement_ids=selected_ids,
                            referencia=referencia,
                            observaciones=observaciones,
                            usuario_id=usuario_id
                        )
                        st.success(f"✅ Despacho registrado exitosamente con {len(selected_ids)} pedidos!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al registrar el despacho: {str(e)}")

# Tab 2: Generar Documentos
with tab2:
    st.markdown("### 📄 Generar Documentos de Envío")
    
    despachos = get_movements_by_type("DESPACHO", limit=50)
    
    if not despachos:
        st.info("ℹ️ No hay despachos registrados.")
    else:
        despacho_options = {f"Despacho #{d['id']} - {d['referencia'] or 'Sin referencia'} ({d['fecha_movimiento'][:10]})": d["id"] for d in despachos}
        selected_despacho_label = st.selectbox("Seleccionar Despacho", list(despacho_options.keys()))
        
        if selected_despacho_label:
            selected_despacho = next(d for d in despachos if d["id"] == despacho_options[selected_despacho_label])
            
            # Card con detalles del despacho
            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%); 
                            border-radius: 0.75rem; 
                            padding: 1.25rem; 
                            margin-bottom: 1.5rem;
                            border: 1px solid #6EE7B7;'>
                    <h4 style='margin: 0 0 1rem 0; color: #065F46; font-size: 1.1rem; font-weight: 600;'>
                        📋 Detalles del Despacho
                    </h4>
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;'>
                        <p style='margin: 0; color: #047857; font-size: 0.9rem;'><strong>ID:</strong> {selected_despacho['id']}</p>
                        <p style='margin: 0; color: #047857; font-size: 0.9rem;'><strong>Estado:</strong> {selected_despacho['estado']}</p>
                        <p style='margin: 0; color: #047857; font-size: 0.9rem;'><strong>Referencia:</strong> {selected_despacho['referencia'] or 'N/A'}</p>
                        <p style='margin: 0; color: #047857; font-size: 0.9rem;'><strong>Fecha:</strong> {selected_despacho['fecha_movimiento']}</p>
                        <p style='margin: 0; color: #047857; font-size: 0.9rem;'><strong>Observaciones:</strong> {selected_despacho['observaciones'] or 'Ninguna'}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("**Generar Documento**")
            doc_type = st.selectbox("Tipo de Documento", ["Guía de Despacho", "Factura", "Packing List"])
            
            if st.button(f"📄 Generar {doc_type}", use_container_width=True):
                st.success(f"✅ {doc_type} generado exitosamente para Despacho #{selected_despacho['id']}!")
                st.info("ℹ️ En una implementación completa, se generaría un PDF o archivo descargable.")

# Tab 3: Historial de Despachos
with tab3:
    st.markdown("### 📊 Historial de Despachos")
    
    despachos = get_movements_by_type("DESPACHO", limit=100)
    
    if despachos:
        df_despachos = pd.DataFrame(despachos)
        columns_to_show = ["id", "referencia", "observaciones", "estado", "fecha_movimiento"]
        available_columns = [col for col in columns_to_show if col in df_despachos.columns]
        
        def highlight_estado_row(row):
            if row["estado"] == "COMPLETADO":
                return ['background-color: #dcfce7'] * len(row)
            elif row["estado"] == "PENDIENTE":
                return ['background-color: #fef9c3'] * len(row)
            return [''] * len(row)
        
        styled_df = df_despachos[available_columns].style.apply(highlight_estado_row, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No hay despachos en el historial.")
