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

# Título de la página
st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #0f172a; font-weight: 700; margin: 0;">📦 Recepción de Mercancía</h1>
        <p style="color: #64748b; margin-top: 0.5rem; font-size: 1.1rem;">Registra y valida la entrada de productos al almacén contra órdenes de compra</p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["➕ Nueva Entrada", "📋 Historial"])

# --- Tab 1: Nueva Entrada ---
with tab1:
    st.markdown('<div style="background: white; padding: 2rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    
    # Sección 1: Datos de Proveedor y OC
    st.markdown("### 🏢 Información del Proveedor y Orden de Compra")
    
    col1, col2 = st.columns(2)
    with col1:
        # Seleccionar proveedor
        proveedores = get_all_providers()
        if proveedores:
            opciones_proveedores = [f"{p['id']}|{p['nombre']}" for p in proveedores]
            proveedor_seleccionado = st.selectbox("Proveedor", opciones_proveedores, index=0)
            proveedor_id = int(proveedor_seleccionado.split("|")[0])
            proveedor_nombre = proveedor_seleccionado.split("|")[1]
        else:
            alert_warning("⚠️ No hay proveedores registrados. Contacta al administrador.")
            proveedor_id = None
            proveedor_nombre = None
    
    with col2:
        # Seleccionar orden de compra
        if proveedor_id:
            ocs_pendientes = get_pending_purchase_orders()
            ocs_proveedor = [oc for oc in ocs_pendientes if oc['proveedor_id'] == proveedor_id]
            
            if ocs_proveedor:
                opciones_oc = [f"{oc['id']}|{oc['numero_oc']}" for oc in ocs_proveedor]
                oc_seleccionada = st.selectbox("Orden de Compra", opciones_oc, index=0)
                oc_id = int(oc_seleccionada.split("|")[0])
                oc_numero = oc_seleccionada.split("|")[1]
                orden_compra = next((oc for oc in ocs_proveedor if oc['id'] == oc_id), None)
            else:
                alert_info("ℹ️ No hay órdenes de compra pendientes de este proveedor")
                oc_id = None
                oc_numero = None
                orden_compra = None
        else:
            oc_id = None
            oc_numero = None
            orden_compra = None
    
    st.markdown("<hr style='border: 1px solid #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    # Sección 2: Datos del Documento
    st.markdown("### 📄 Datos de Recepción")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        referencia = st.text_input("Número de Referencia / Remito", placeholder="Ej: REM-2024-0001")
    with col4:
        fecha_doc = st.date_input("Fecha de Recepción")
    with col5:
        hora_doc = st.time_input("Hora de Recepción")
    
    doc_validado = st.checkbox("✅ Documentos validados contra OC", value=False)
    
    st.markdown("<hr style='border: 1px solid #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    # Sección 3: Producto
    st.markdown("### 📦 Producto")
    
    productos = get_all_products()
    if not productos:
        alert_warning("No hay productos registrados en el sistema.")
    else:
        opciones_productos = [f"{p['sku']} - {p['nombre']}" for p in productos]
        producto_seleccionado = st.selectbox("Producto", opciones_productos, index=0)
        
        if producto_seleccionado:
            sku = producto_seleccionado.split(" - ")[0]
            producto = get_product_by_sku(sku)
            
            col6, col7 = st.columns(2)
            with col6:
                cantidad = st.number_input("Cantidad Recibida", min_value=1, value=1)
                lote = st.text_input("Número de Lote", placeholder="Ej: LOTE-123")
            with col7:
                fecha_vencimiento = st.date_input("Fecha de Vencimiento (opcional)")
            
            # Validar contra OC si está disponible
            if orden_compra and oc_id:
                items_oc = get_purchase_order_items(oc_id)
                item_producto = next((item for item in items_oc if item['producto_id'] == producto['id']), None)
                
                if item_producto:
                    st.success(f"✅ Producto encontrado en OC: Se esperaban {item_producto['cantidad_ordenada']} unidades")
                    if cantidad > item_producto['cantidad_ordenada']:
                        alert_warning(f"⚠️ Cantidad recibida ({cantidad}) supera la ordenada ({item_producto['cantidad_ordenada']})")
                else:
                    alert_warning("⚠️ Este producto NO está en la OC seleccionada")
            
            st.markdown("<hr style='border: 1px solid #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
            
            # Sección 4: Ubicación
            st.markdown("### 📍 Asignación de Ubicación")
            
            zonas = get_all_zones()
            opciones_zonas = [f"{z['codigo']} - {z['nombre']}" for z in zonas]
            zona_seleccionada = st.selectbox("Zona de Asignación", opciones_zonas, index=0)
            
            if zona_seleccionada:
                zona_codigo = zona_seleccionada.split(" - ")[0]
                zona = next((z for z in zonas if z['codigo'] == zona_codigo), None)
                
                if zona:
                    ubicaciones_zona = get_locations_by_zone(zona['id'])
                    if not ubicaciones_zona:
                        alert_warning(f"No hay ubicaciones disponibles en la zona {zona['nombre']}")
                    else:
                        opciones_ubicaciones = [f"{u['codigo']} - Pasillo {u['pasillo']} / Estante {u['estante']} / Nivel {u['nivel']}" for u in ubicaciones_zona]
                        ubicacion_seleccionada = st.selectbox("Ubicación Específica", opciones_ubicaciones, index=0)
                        
                        st.markdown("<hr style='border: 1px solid #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
                        
                        observaciones = st.text_area("Observaciones (opcional)", placeholder="Agrega notas importantes sobre la recepción...")
                        
                        if st.button("📝 Registrar Entrada", type="primary", use_container_width=True):
                            if not referencia:
                                alert_error("Ingresa un número de referencia!")
                            elif not proveedor_id:
                                alert_error("Selecciona un proveedor!")
                            elif not doc_validado:
                                alert_error("Primero valida los documentos antes de continuar!")
                            elif not ubicacion_seleccionada:
                                alert_error("Selecciona una ubicación!")
                            else:
                                ubicacion_codigo = ubicacion_seleccionada.split(" - ")[0]
                                ubicacion = next((u for u in ubicaciones_zona if u['codigo'] == ubicacion_codigo), None)
                                
                                if ubicacion:
                                    try:
                                        fecha_venc_str = fecha_vencimiento.isoformat() if fecha_vencimiento else None
                                        fecha_movimiento = f"{fecha_doc.isoformat()}T{hora_doc.isoformat()}"
                                        
                                        # Crear movimiento con información completa
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
                                        
                                        alert_success(f"✅ Entrada registrada exitosamente! ID: {movement_id}. Ve a Inspección para validar.")
                                        st.rerun()
                                    except Exception as e:
                                        alert_error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab 2: Historial ---
with tab2:
    st.markdown('<div style="background: white; padding: 2rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    st.subheader("Movimientos Recientes")
    
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
            alert_info("No hay entradas registradas.")
    else:
        alert_info("No hay movimientos registrados aún.")
    st.markdown('</div>', unsafe_allow_html=True)
