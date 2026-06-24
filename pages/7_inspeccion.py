"""Página de Inspección de WareFlow WMS."""

import streamlit as st
import pandas as pd

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.alerts import alert_success, alert_error, alert_warning, alert_info
from services.product_service import get_product_by_id
from services.location_service import get_location_by_id
from services.movement_service import (
    get_pending_movements, update_movement_status, update_inventory, get_recent_movements
)

require_auth()
require_permission("recepcion", "leer")

render_sidebar(current_page="inspeccion")

# Título de la página
st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #0f172a; font-weight: 700; margin: 0;">🔍 Inspección de Mercancía</h1>
        <p style="color: #64748b; margin-top: 0.5rem; font-size: 1.1rem;">Valida la calidad y autoriza la entrada de productos</p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["⚠️ Pendientes", "📋 Historial"])

with tab1:
    pending = get_pending_movements()
    if not pending:
        st.markdown('<div style="background: white; padding: 3rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1); text-align: center;">', unsafe_allow_html=True)
        alert_info("🎉 No hay movimientos pendientes de inspección!")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Listado de pendientes
        df_pending = pd.DataFrame([dict(row) for row in pending])
        df_pending = df_pending[['id', 'tipo', 'referencia', 'cantidad', 'fecha_movimiento']]
        df_pending.columns = ['ID', 'Tipo', 'Referencia', 'Cantidad', 'Fecha']
        
        st.markdown('<div style="background: white; padding: 1.5rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1); margin-bottom: 1.5rem;">', unsafe_allow_html=True)
        st.subheader("Movimientos Pendientes")
        st.dataframe(df_pending, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Seleccionar movimiento para inspeccionar
        opciones_movimientos = [f"ID {m['id']} - Ref: {m['referencia']}" for m in pending]
        movimiento_seleccionado = st.selectbox("Selecciona un movimiento para inspeccionar", opciones_movimientos, index=0)
        
        if movimiento_seleccionado:
            mov_id = int(movimiento_seleccionado.split(" - ")[0].split(" ")[1])
            movimiento = next((m for m in pending if m['id'] == mov_id), None)
            
            if movimiento:
                producto = get_product_by_id(movimiento['producto_id'])
                ubicacion_dest = get_location_by_id(movimiento['ubicacion_destino_id'])
                
                st.markdown('<div style="background: white; padding: 2rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1);">', unsafe_allow_html=True)
                
                # Detalles del movimiento
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"### 📦 Producto")
                    st.write(f"**SKU**: {producto['sku']}")
                    st.write(f"**Nombre**: {producto['nombre']}")
                    st.write(f"**Cantidad**: {movimiento['cantidad']}")
                with col_b:
                    st.markdown(f"### 📍 Destino")
                    st.write(f"**Ubicación**: {ubicacion_dest['codigo']}")
                    st.write(f"**Referencia**: {movimiento['referencia']}")
                    st.write(f"**Fecha**: {movimiento['fecha_movimiento']}")
                
                st.markdown("<hr style='border: 1px solid #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
                
                st.markdown("### ✅ Verificación de Calidad")
                calidad_ok = st.checkbox("Calidad verificada y conforme", value=False)
                
                tiene_anomalias = st.checkbox("Presenta anomalías", value=False)
                descripcion_anomalias = ""
                if tiene_anomalias:
                    descripcion_anomalias = st.text_area("Descripción de anomalías")
                
                st.markdown("<hr style='border: 1px solid #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
                
                decision = st.radio("### 📝 Decisión Final", ["✅ Autorizar Entrada", "❌ Rechazar Entrada"], index=0)
                
                observaciones_finales = st.text_area("Observaciones de inspección (opcional)")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                col_izq, col_der = st.columns(2)
                with col_izq:
                    if st.button("Confirmar", type="primary", use_container_width=True):
                        try:
                            if not calidad_ok and decision == "✅ Autorizar Entrada":
                                alert_error("Primero verifica la calidad del producto!")
                            else:
                                lote = None
                                fecha_vencimiento = None
                                if "lotes_temp" in st.session_state and mov_id in st.session_state["lotes_temp"]:
                                    lote = st.session_state["lotes_temp"][mov_id]["lote"]
                                    fecha_vencimiento = st.session_state["lotes_temp"][mov_id]["fecha_vencimiento"]
                                
                                obs_completas = []
                                if observaciones_finales:
                                    obs_completas.append(observaciones_finales)
                                if tiene_anomalias and descripcion_anomalias:
                                    obs_completas.append(f"Anomalías: {descripcion_anomalias}")
                                
                                if decision == "✅ Autorizar Entrada":
                                    update_inventory(
                                        producto_id=producto['id'],
                                        ubicacion_id=ubicacion_dest['id'],
                                        cantidad=movimiento['cantidad'],
                                        lote=lote,
                                        fecha_vencimiento=fecha_vencimiento
                                    )
                                    update_movement_status(
                                        movement_id=mov_id,
                                        nuevo_estado="APROBADO",
                                        observaciones=" | ".join(obs_completas) if obs_completas else ""
                                    )
                                    alert_success("✅ Entrada autorizada! Inventario actualizado.")
                                else:
                                    update_movement_status(
                                        movement_id=mov_id,
                                        nuevo_estado="RECHAZADO",
                                        observaciones=" | ".join(obs_completas) if obs_completas else ""
                                    )
                                    alert_warning("⚠️ Entrada rechazada.")
                                
                                if "lotes_temp" in st.session_state and mov_id in st.session_state["lotes_temp"]:
                                    del st.session_state["lotes_temp"][mov_id]
                                
                                st.rerun()
                        except Exception as e:
                            alert_error(f"Error: {str(e)}")
                
                st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div style="background: white; padding: 2rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    st.subheader("Historial de Inspecciones")
    
    recent = get_recent_movements(20)
    if recent:
        df = pd.DataFrame([dict(row) for row in recent])
        df = df[['id', 'tipo', 'referencia', 'cantidad', 'estado', 'fecha_movimiento']]
        df.columns = ['ID', 'Tipo', 'Referencia', 'Cantidad', 'Estado', 'Fecha']
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        alert_info("No hay movimientos registrados aún.")
    st.markdown('</div>', unsafe_allow_html=True)
