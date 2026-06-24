"""Página de Recepción de WareFlow WMS."""

import streamlit as st
import pandas as pd
from datetime import datetime

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.alerts import alert_success, alert_error, alert_warning, alert_info
from services.product_service import get_all_products, get_product_by_sku
from services.location_service import get_all_zones, get_locations_by_zone
from services.movement_service import create_movement, get_recent_movements
from services.provider_service import (
    get_all_providers, get_pending_purchase_orders, 
    get_purchase_order_by_number, get_purchase_order_items
)

require_auth()
require_permission("recepcion", "leer")

render_sidebar(current_page="recepcion")

# Navbar superior
st.markdown("""
    <div class="top-navbar">
        <h1>📦 Recepción de Mercancía</h1>
        <p>Registra y valida la entrada de productos al almacén contra órdenes de compra</p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["➕ Nueva Entrada", "📋 Historial"])

# --- Tab 1: Nueva Entrada ---
with tab1:
    # Layout de dos columnas
    col_main, col_sidebar = st.columns([2, 0.95])
    
    with col_main:
        # Sección 1: Proveedor y OC
        st.markdown("""
            <div class="section-card">
                <div class="section-title">🏢 Proveedor y Orden de Compra</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            proveedores = get_all_providers()
            if proveedores:
                opciones_proveedores = [f"{p['id']}|{p['nombre']}" for p in proveedores]
                proveedor_seleccionado = st.selectbox("🏢 Proveedor", opciones_proveedores, index=0, label_visibility="collapsed")
                proveedor_id = int(proveedor_seleccionado.split("|")[0])
                proveedor_nombre = proveedor_seleccionado.split("|")[1]
            else:
                st.markdown('<div class="alert-box alert-warning">⚠️ No hay proveedores registrados</div>', unsafe_allow_html=True)
                proveedor_id = None
        
        with col2:
            if proveedor_id:
                ocs_pendientes = get_pending_purchase_orders()
                ocs_proveedor = [oc for oc in ocs_pendientes if oc['proveedor_id'] == proveedor_id]
                
                if ocs_proveedor:
                    opciones_oc = [f"{oc['id']}|{oc['numero_oc']}" for oc in ocs_proveedor]
                    oc_seleccionada = st.selectbox("📋 Orden de Compra", opciones_oc, index=0, label_visibility="collapsed")
                    oc_id = int(oc_seleccionada.split("|")[0])
                    oc_numero = oc_seleccionada.split("|")[1]
                    orden_compra = next((oc for oc in ocs_proveedor if oc['id'] == oc_id), None)
                else:
                    st.markdown('<div class="alert-box alert-info">ℹ️ No hay OC pendientes</div>', unsafe_allow_html=True)
                    oc_id = None
                    orden_compra = None
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Sección 2: Datos de Recepción
        st.markdown("""
            <div class="section-card">
                <div class="section-title">📄 Datos de Recepción</div>
            </div>
        """, unsafe_allow_html=True)
        
        col3, col4, col5 = st.columns(3)
        with col3:
            referencia = st.text_input("Referencia/Remito", placeholder="REM-2024-0001", label_visibility="collapsed")
        with col4:
            fecha_doc = st.date_input("Fecha", label_visibility="collapsed")
        with col5:
            hora_doc = st.time_input("Hora", label_visibility="collapsed")
        
        doc_validado = st.checkbox("✅ Documentos validados contra OC")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Sección 3: Producto
        st.markdown("""
            <div class="section-card">
                <div class="section-title">📦 Producto</div>
            </div>
        """, unsafe_allow_html=True)
        
        productos = get_all_products()
        if productos:
            opciones_productos = [f"{p['sku']} - {p['nombre']}" for p in productos]
            producto_seleccionado = st.selectbox("Selecciona Producto", opciones_productos, label_visibility="collapsed")
            
            if producto_seleccionado:
                sku = producto_seleccionado.split(" - ")[0]
                producto = get_product_by_sku(sku)
                
                col6, col7 = st.columns(2)
                with col6:
                    cantidad = st.number_input("Cantidad Recibida", min_value=1, value=1, label_visibility="collapsed")
                    lote = st.text_input("Número de Lote", placeholder="LOTE-123", label_visibility="collapsed")
                with col7:
                    fecha_vencimiento = st.date_input("Fecha de Vencimiento", label_visibility="collapsed")
                
                # Validar contra OC
                if orden_compra and oc_id:
                    items_oc = get_purchase_order_items(oc_id)
                    item_producto = next((item for item in items_oc if item['producto_id'] == producto['id']), None)
                    
                    if item_producto:
                        st.markdown(f'<div class="alert-box alert-success">✅ Producto en OC: {item_producto["cantidad_ordenada"]} unidades esperadas</div>', unsafe_allow_html=True)
                        if cantidad > item_producto['cantidad_ordenada']:
                            st.markdown(f'<div class="alert-box alert-warning">⚠️ Cantidad supera lo ordenado</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="alert-box alert-warning">⚠️ Producto NO está en la OC</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                
                # Sección 4: Ubicación
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">📍 Asignación de Ubicación</div>
                    </div>
                """, unsafe_allow_html=True)
                
                zonas = get_all_zones()
                if zonas:
                    opciones_zonas = [f"{z['codigo']} - {z['nombre']}" for z in zonas]
                    zona_seleccionada = st.selectbox("Zona", opciones_zonas, label_visibility="collapsed")
                    
                    zona_codigo = zona_seleccionada.split(" - ")[0]
                    zona = next((z for z in zonas if z['codigo'] == zona_codigo), None)
                    
                    if zona:
                        ubicaciones_zona = get_locations_by_zone(zona['id'])
                        if ubicaciones_zona:
                            opciones_ubicaciones = [f"{u['codigo']} - P{u['pasillo']} E{u['estante']} N{u['nivel']}" for u in ubicaciones_zona]
                            ubicacion_seleccionada = st.selectbox("Ubicación Específica", opciones_ubicaciones, label_visibility="collapsed")
                            
                            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                            
                            observaciones = st.text_area("Observaciones", placeholder="Notas importantes...", height=100, label_visibility="collapsed")
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            if st.button("📝 Registrar Entrada", use_container_width=True):
                                if not referencia:
                                    alert_error("Ingresa un número de referencia")
                                elif not proveedor_id:
                                    alert_error("Selecciona un proveedor")
                                elif not doc_validado:
                                    alert_error("Valida los documentos primero")
                                elif not ubicacion_seleccionada:
                                    alert_error("Selecciona una ubicación")
                                else:
                                    ubicacion_codigo = ubicacion_seleccionada.split(" - ")[0]
                                    ubicacion = next((u for u in ubicaciones_zona if u['codigo'] == ubicacion_codigo), None)
                                    
                                    if ubicacion:
                                        try:
                                            fecha_venc_str = fecha_vencimiento.isoformat() if fecha_vencimiento else None
                                            fecha_movimiento = f"{fecha_doc.isoformat()}T{hora_doc.isoformat()}"
                                            
                                            movement_id = create_movement(
                                                tipo="ENTRADA",
                                                producto_id=producto['id'],
                                                ubicacion_origen_id=None,
                                                ubicacion_destino_id=ubicacion['id'],
                                                cantidad=cantidad,
                                                referencia=referencia,
                                                observaciones=observaciones,
                                                proveedor_id=proveedor_id,
                                                orden_compra_id=oc_id,
                                                fecha_movimiento=fecha_movimiento
                                            )
                                            
                                            if "lotes_temp" not in st.session_state:
                                                st.session_state["lotes_temp"] = {}
                                            st.session_state["lotes_temp"][movement_id] = {
                                                "lote": lote,
                                                "fecha_vencimiento": fecha_venc_str
                                            }
                                            
                                            alert_success(f"✅ Entrada registrada! ID: {movement_id}")
                                            st.rerun()
                                        except Exception as e:
                                            alert_error(f"Error: {str(e)}")
    
    # Sidebar de información
    with col_sidebar:
        # Resumen de Proveedor
        if proveedor_id and proveedor_nombre:
            st.markdown("""
                <div class="sidebar-card info">
                    <h4>📦 Proveedor Actual</h4>
                    <p>{}</p>
                </div>
            """.format(proveedor_nombre), unsafe_allow_html=True)
        
        # Resumen de OC
        if orden_compra:
            st.markdown("""
                <div class="sidebar-card info">
                    <h4>📋 Orden Activa</h4>
                    <p>{}</p>
                    <div class="value">{}</div>
                </div>
            """.format(oc_numero, orden_compra.get('cantidad', 0)), unsafe_allow_html=True)
        
        # Validación de Documentos
        if doc_validado:
            st.markdown("""
                <div class="sidebar-card success">
                    <h4>✅ Documentos</h4>
                    <p>Validados contra OC</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="sidebar-card warning">
                    <h4>⚠️ Documentos</h4>
                    <p>Pendiente de validar</p>
                </div>
            """, unsafe_allow_html=True)

# --- Tab 2: Historial ---
with tab2:
    st.markdown("""
        <div class="section-card">
            <div class="section-title">📋 Historial de Entradas</div>
        </div>
    """, unsafe_allow_html=True)
    
    recent = get_recent_movements(30)
    if recent:
        entradas = [m for m in recent if m['tipo'] == 'ENTRADA']
        if entradas:
            for entrada in entradas:
                estado_class = ""
                if entrada['estado'] == 'APROBADO':
                    estado_class = "success"
                elif entrada['estado'] == 'RECHAZADO':
                    estado_class = "danger"
                else:
                    estado_class = "warning"
                
                st.markdown(f"""
                    <div class="sidebar-card {estado_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0;">Ref: {entrada['referencia']}</h4>
                            <span class="badge badge-{estado_class}">{entrada['estado']}</span>
                        </div>
                        <p style="margin: 0.5rem 0 0 0;">ID: {entrada['id']} | Cantidad: {entrada['cantidad']}</p>
                        <p style="margin: 0.25rem 0; color: #9ca3af; font-size: 0.85rem;">{entrada['fecha_movimiento']}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-info">ℹ️ No hay entradas registradas</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-box alert-info">ℹ️ No hay movimientos aún</div>', unsafe_allow_html=True)
