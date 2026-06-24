"""Página de Despacho de WareFlow WMS."""

import streamlit as st
import pandas as pd

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.tables import render_table
from components.alerts import alert_success, alert_error, alert_info
from services.movement_service import get_movements_by_type, create_despacho

require_auth()
require_permission("despacho", "leer")

render_sidebar(current_page="despacho")
render_navbar(titulo="Despacho", icono="🚚")

# Tabs
tab1, tab2, tab3 = st.tabs(["Consolidar Pedidos", "Generar Documentos", "Historial de Despachos"])

# Tab 1: Consolidar Pedidos
with tab1:
    st.header("Consolidar Pedidos para Despacho")
    
    # Get completed picking orders
    picking_orders = get_movements_by_type("PICKING", limit=100)
    completed_picking = [o for o in picking_orders if o["estado"] == "COMPLETADO"]
    
    if not completed_picking:
        alert_info("No hay picking completados para consolidar.")
    else:
        st.subheader("Picking Completados Disponibles")
        
        # Create a DataFrame for selection
        df_picking = pd.DataFrame(completed_picking)
        df_picking["Seleccionar"] = False
        
        # Show editable table for selection
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
            hide_index=True
        )
        
        # Get selected orders
        selected_ids = edited_df[edited_df["Seleccionar"]]["id"].tolist()
        
        if selected_ids:
            st.subheader(f"Pedidos Seleccionados: {len(selected_ids)}")
            
            # Form to create despacho
            with st.form("form_despacho"):
                referencia = st.text_input("Referencia del Despacho")
                observaciones = st.text_area("Observaciones (opcional)")
                
                submitted = st.form_submit_button("Registrar Despacho")
                
                if submitted:
                    try:
                        usuario_id = st.session_state.get("usuario_id")
                        create_despacho(
                            movement_ids=selected_ids,
                            referencia=referencia,
                            observaciones=observaciones,
                            usuario_id=usuario_id
                        )
                        alert_success(f"Despacho registrado exitosamente con {len(selected_ids)} pedidos!")
                        st.rerun()
                    except Exception as e:
                        alert_error(f"Error al registrar el despacho: {str(e)}")

# Tab 2: Generar Documentos
with tab2:
    st.header("Generar Documentos de Envío")
    
    # Get all despachos
    despachos = get_movements_by_type("DESPACHO", limit=50)
    
    if not despachos:
        alert_info("No hay despachos registrados.")
    else:
        # Select despacho
        despacho_options = {f"Despacho #{d['id']} - {d['referencia'] or 'Sin referencia'} ({d['fecha_movimiento'][:10]})": d["id"] for d in despachos}
        selected_despacho_label = st.selectbox("Seleccionar Despacho", list(despacho_options.keys()))
        
        if selected_despacho_label:
            selected_despacho = next(d for d in despachos if d["id"] == despacho_options[selected_despacho_label])
            
            st.subheader("Detalles del Despacho")
            st.write(f"**ID:** {selected_despacho['id']}")
            st.write(f"**Referencia:** {selected_despacho['referencia'] or 'N/A'}")
            st.write(f"**Fecha:** {selected_despacho['fecha_movimiento']}")
            st.write(f"**Observaciones:** {selected_despacho['observaciones'] or 'Ninguna'}")
            
            # Generate document button
            st.subheader("Generar Documento")
            doc_type = st.selectbox("Tipo de Documento", ["Guía de Despacho", "Factura", "Packing List"])
            
            if st.button(f"Generar {doc_type}"):
                # For now, just show a success message
                alert_success(f"{doc_type} generado exitosamente para Despacho #{selected_despacho['id']}!")
                alert_info("En una implementación completa, se generaría un PDF o archivo descargable.")

# Tab 3: Historial de Despachos
with tab3:
    st.header("Historial de Despachos")
    
    despachos = get_movements_by_type("DESPACHO", limit=100)
    
    if despachos:
        df_despachos = pd.DataFrame(despachos)
        columns_to_show = ["id", "referencia", "observaciones", "estado", "fecha_movimiento"]
        available_columns = [col for col in columns_to_show if col in df_despachos.columns]
        render_table(df_despachos[available_columns] if available_columns else df_despachos)
    else:
        alert_info("No hay despachos en el historial.")
