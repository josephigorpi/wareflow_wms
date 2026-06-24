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
    <div class="top-navbar">
        <h1>🔍 Inspección de Mercancía</h1>
        <p>Valida la calidad y autoriza la entrada de productos</p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["⚠️ Pendientes", "📋 Historial", "📊 Anomalías"])

with tab1:
    pending = get_pending_movements()
    # Filtrar solo entradas
    pending = [m for m in pending if m['tipo'] == 'ENTRADA']
    
    if not pending:
        st.markdown("""
            <div class="sidebar-card success" style="text-align: center; padding: 3rem 2rem;">
                <h4 style="margin: 0; font-size: 1.5rem; color: #065f46;">🎉 ¡Excelente!</h4>
                <p style="color: #065f46; margin: 1rem 0 0 0;">No hay movimientos pendientes de inspección</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Layout con columnas
        col_main, col_info = st.columns([2, 0.95])
        
        with col_main:
            # Resumen de pendientes
            st.markdown(f"""
                <div class="section-card">
                    <div class="section-title">⚠️ Pendientes de Inspección</div>
                    <p style="color: #6b7280; margin: 0.5rem 0;">Total: <strong style="font-size: 1.3rem; color: #ef4444;">{len(pending)} movimiento{'s' if len(pending) > 1 else ''}</strong></p>
                </div>
            """, unsafe_allow_html=True)
            
            # Seleccionar movimiento
            opciones_movimientos = [f"ID {m['id']} - Ref: {m['referencia']} ({m['cantidad']} unidades)" for m in pending]
            movimiento_idx = st.selectbox("Selecciona movimiento a inspeccionar", range(len(opciones_movimientos)), 
                                         format_func=lambda x: opciones_movimientos[x], label_visibility="collapsed")
            
            movimiento = pending[movimiento_idx]
            mov_id = movimiento['id']
            
            if movimiento:
                producto = get_product_by_id(movimiento['producto_id'])
                ubicacion_dest = get_location_by_id(movimiento['ubicacion_destino_id'])
                
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                
                # Detalles del Producto
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">📦 Detalles del Producto</div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**SKU:** {producto['sku']}")
                    st.write(f"**Nombre:** {producto['nombre']}")
                with col_b:
                    st.write(f"**Cantidad a Inspeccionar:** {movimiento['cantidad']}")
                    st.write(f"**Ubicación Destino:** {ubicacion_dest['codigo']}")
                
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                
                # Verificación de Calidad
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">✅ Verificación de Calidad</div>
                    </div>
                """, unsafe_allow_html=True)
                
                calidad_ok = st.checkbox("✓ Calidad verificada y conforme")
                
                if not calidad_ok:
                    st.markdown('<div class="alert-box alert-warning">⚠️ Debes verificar la calidad antes de autorizar</div>', unsafe_allow_html=True)
                
                cantidad_conforme = st.number_input(
                    "Cantidad conforme", 
                    min_value=0, 
                    max_value=movimiento['cantidad'],
                    value=movimiento['cantidad'],
                    label_visibility="collapsed"
                )
                
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                
                # Anomalías
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">⚠️ Registro de Anomalías</div>
                    </div>
                """, unsafe_allow_html=True)
                
                tiene_anomalias = st.checkbox("Presenta anomalías")
                
                anomalias_registradas = []
                
                if tiene_anomalias:
                    col_anom1, col_anom2 = st.columns(2)
                    
                    with col_anom1:
                        tipo_anomalia = st.selectbox(
                            "Tipo de Anomalía",
                            ["Daño Físico", "Oxidación", "Vencido", "Falta de Cantidad", "Otro"],
                            label_visibility="collapsed"
                        )
                        cantidad_danada = st.number_input(
                            "Cantidad de productos dañados",
                            min_value=0,
                            max_value=movimiento['cantidad'],
                            value=0,
                            label_visibility="collapsed"
                        )
                    
                    with col_anom2:
                        severidad = st.select_slider(
                            "Severidad",
                            ["Leve", "Moderado", "Grave"],
                            value="Moderado"
                        )
                    
                    descripcion_anomalias = st.text_area(
                        "Descripción de la anomalía",
                        placeholder="Describe qué pasó...",
                        height=80,
                        label_visibility="collapsed"
                    )
                    
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
                    
                    if st.button("➕ Registrar Anomalía", use_container_width=True):
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
                
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                
                # Decisión Final
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">📝 Decisión Final</div>
                    </div>
                """, unsafe_allow_html=True)
                
                decision = st.radio(
                    "Acción:",
                    ["✅ Autorizar Entrada", "❌ Rechazar Entrada"],
                    index=0,
                    horizontal=True,
                    label_visibility="collapsed"
                )
                
                observaciones_finales = st.text_area(
                    "Observaciones finales",
                    placeholder="Notas adicionales...",
                    height=80,
                    label_visibility="collapsed"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("✅ Confirmar Inspección", use_container_width=True):
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
                                anomalias_previas = get_anomalies_by_movement(mov_id)
                                
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
        
        # Sidebar con información
        with col_info:
            st.markdown(f"""
                <div class="sidebar-card info">
                    <h4>📌 Referencia</h4>
                    <p>{movimiento['referencia']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="sidebar-card info">
                    <h4>📊 Cantidad</h4>
                    <div class="value">{movimiento['cantidad']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if calidad_ok:
                st.markdown("""
                    <div class="sidebar-card success">
                        <h4>✅ Calidad</h4>
                        <p>Verificada</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="sidebar-card warning">
                        <h4>⚠️ Calidad</h4>
                        <p>Por verificar</p>
                    </div>
                """, unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Historial de Inspecciones</div>', unsafe_allow_html=True)
    
    recent = get_recent_movements(30)
    if recent:
        # Filtrar solo entradas
        entradas = [m for m in recent if m['tipo'] == 'ENTRADA']
        if entradas:
            for entrada in entradas:
                estado_class = ""
                estado_icon = ""
                
                if entrada['estado'] == 'APROBADO':
                    estado_class = "status-approved"
                    estado_icon = "✅"
                elif entrada['estado'] == 'RECHAZADO':
                    estado_class = "status-rejected"
                    estado_icon = "❌"
                elif entrada['estado'] == 'PENDIENTE':
                    estado_class = "status-pending"
                    estado_icon = "⏳"
                
                st.markdown(f"""
                    <div class="movement-card approved">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <div>
                                <h4 style="margin: 0; color: #1f2937;">Ref: {entrada['referencia']}</h4>
                                <p style="margin: 0.25rem 0 0 0; color: #6b7280; font-size: 0.9rem;">ID: {entrada['id']}</p>
                            </div>
                            <span class="status-badge {estado_class}">{estado_icon} {entrada['estado']}</span>
                        </div>
                        <div class="info-row">
                            <div class="info-item">
                                <div class="info-item-label">Cantidad Inspeccionada</div>
                                <div class="info-item-value">{entrada['cantidad']}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-item-label">Fecha de Inspección</div>
                                <div class="info-item-value" style="font-size: 1rem;">{entrada['fecha_movimiento']}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-item-label">Estado</div>
                                <div class="info-item-value" style="font-size: 1rem;">{entrada['estado']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-info">ℹ️ No hay inspecciones registradas.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-info">ℹ️ No hay movimientos registrados aún.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Anomalías Registradas</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); padding: 1.5rem; border-radius: 0.75rem; border: 1px solid #3b82f6; margin-bottom: 1.5rem;">
            <p style="margin: 0; color: #1e40af; font-weight: 600;">
                📊 Este tab mostrará un resumen de todas las anomalías detectadas durante las inspecciones
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); padding: 2rem; border-radius: 1rem; border: 2px solid #10b981; text-align: center;">
            <h3 style="color: #166534; margin: 0;">✅ Sistema en desarrollo</h3>
            <p style="color: #166534; margin: 1rem 0 0 0; font-size: 1.1rem;">
                Los datos se poblarán automáticamente cuando se registren anomalías en las inspecciones
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
