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
from services.inspection_service import create_anomaly, get_anomalies_by_movement
from services.provider_service import get_provider_by_id
import os
from datetime import datetime

require_auth()
require_permission("recepcion", "leer")

render_sidebar(current_page="inspeccion")

# Crear carpeta para almacenar fotos de anomalías
ANOMALIAS_FOLDER = "anomalias_evidencia"
os.makedirs(ANOMALIAS_FOLDER, exist_ok=True)

# Título de la página
st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #0f172a; font-weight: 700; margin: 0;">🔍 Inspección de Mercancía</h1>
        <p style="color: #64748b; margin-top: 0.5rem; font-size: 1.1rem;">Valida la calidad y autoriza la entrada de productos</p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["⚠️ Pendientes", "📋 Historial", "📊 Anomalías"])

with tab1:
    pending = get_pending_movements()
    # Filtrar solo entradas
    pending = [m for m in pending if m['tipo'] == 'ENTRADA']
    
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
                
                cantidad_conforme = st.number_input(
                    "Cantidad conforme (Cumple especificaciones)", 
                    min_value=0, 
                    max_value=movimiento['cantidad'],
                    value=movimiento['cantidad']
                )
                
                st.markdown("<hr style='border: 1px solid #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
                
                st.markdown("### ⚠️ Registro de Anomalías")
                tiene_anomalias = st.checkbox("Presenta anomalías", value=False)
                
                anomalias_registradas = []
                
                if tiene_anomalias:
                    # Formulario de anomalías
                    col_anom1, col_anom2 = st.columns(2)
                    
                    with col_anom1:
                        tipo_anomalia = st.selectbox(
                            "Tipo de Anomalía",
                            ["Daño Físico", "Oxidación", "Vencido", "Falta de Cantidad", "Otro"]
                        )
                        cantidad_danada = st.number_input(
                            "Cantidad de productos dañados",
                            min_value=0,
                            max_value=movimiento['cantidad'],
                            value=0
                        )
                    
                    with col_anom2:
                        severidad = st.select_slider(
                            "Severidad de la anomalía",
                            ["Leve", "Moderado", "Grave"],
                            value="Moderado"
                        )
                    
                    descripcion_anomalias = st.text_area(
                        "Descripción detallada de la anomalía",
                        placeholder="Describe qué pasó, cómo, dónde..."
                    )
                    
                    # Upload de foto
                    foto_uploaded = st.file_uploader(
                        "📸 Subir foto de evidencia",
                        type=["jpg", "jpeg", "png"],
                        key=f"foto_anomalia_{mov_id}"
                    )
                    
                    foto_path = None
                    if foto_uploaded:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"anomalia_{mov_id}_{timestamp}_{foto_uploaded.name}"
                        filepath = os.path.join(ANOMALIAS_FOLDER, filename)
                        
                        with open(filepath, "wb") as f:
                            f.write(foto_uploaded.getbuffer())
                        
                        foto_path = filepath
                        st.success(f"✅ Foto guardada: {filename}")
                    
                    if st.button("➕ Registrar esta anomalía", use_container_width=True):
                        if cantidad_danada > 0 or descripcion_anomalias:
                            anomalias_registradas.append({
                                "tipo": tipo_anomalia,
                                "cantidad": cantidad_danada,
                                "severidad": severidad,
                                "descripcion": descripcion_anomalias,
                                "foto": foto_path
                            })
                            alert_success("✅ Anomalía registrada!")
                        else:
                            alert_warning("⚠️ Ingresa una cantidad o descripción")
                
                st.markdown("<hr style='border: 1px solid #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
                
                decision = st.radio(
                    "### 📝 Decisión Final", 
                    ["✅ Autorizar Entrada", "❌ Rechazar Entrada"],
                    index=0
                )
                
                observaciones_finales = st.text_area("Observaciones de inspección (opcional)")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                col_izq, col_der = st.columns(2)
                with col_izq:
                    if st.button("✅ Confirmar Inspección", type="primary", use_container_width=True):
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
                                
                                # Registrar anomalías en BD
                                if tiene_anomalias:
                                    # Obtener anomalías previas del movimiento
                                    anomalias_previas = get_anomalies_by_movement(mov_id)
                                    
                                    # Agregar nuevas anomalías
                                    for anom in anomalias_registradas:
                                        create_anomaly(
                                            movimiento_id=mov_id,
                                            tipo_anomalia=anom['tipo'],
                                            cantidad_danada=anom['cantidad'],
                                            severidad=anom['severidad'],
                                            descripcion=anom['descripcion'],
                                            foto_path=anom['foto'] or ""
                                        )
                                        obs_completas.append(f"Anomalía: {anom['tipo']} (Severidad: {anom['severidad']}, Cantidad: {anom['cantidad']})")
                                
                                if decision == "✅ Autorizar Entrada":
                                    # Actualizar inventario con cantidad conforme
                                    if cantidad_conforme > 0:
                                        update_inventory(
                                            product_id=producto['id'],
                                            ubicacion_id=ubicacion_dest['id'],
                                            cantidad=cantidad_conforme,
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
    
    recent = get_recent_movements(30)
    if recent:
        # Filtrar solo entradas
        entradas = [m for m in recent if m['tipo'] == 'ENTRADA']
        if entradas:
            df = pd.DataFrame([dict(row) for row in entradas])
            df = df[['id', 'tipo', 'referencia', 'cantidad', 'estado', 'fecha_movimiento']]
            df.columns = ['ID', 'Tipo', 'Referencia', 'Cantidad', 'Estado', 'Fecha']
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            alert_info("No hay inspecciones registradas.")
    else:
        alert_info("No hay movimientos registrados aún.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div style="background: white; padding: 2rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1);"></div>', unsafe_allow_html=True)
    st.subheader("📊 Anomalías Registradas")
    
    st.info("Este tab mostrará un resumen de todas las anomalías detectadas durante las inspecciones")
    
    st.markdown('</div>', unsafe_allow_html=True)
