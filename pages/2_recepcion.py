"""Página de Recepción de WareFlow WMS."""

import streamlit as st
import pandas as pd

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.alerts import alert_success, alert_error, alert_warning, alert_info
from services.product_service import get_all_products, get_product_by_sku
from services.location_service import get_all_zones, get_locations_by_zone
from services.movement_service import create_movement, get_recent_movements

require_auth()
require_permission("recepcion", "leer")

render_sidebar(current_page="recepcion")

# Título de la página
st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #0f172a; font-weight: 700; margin: 0;">📦 Recepción de Mercancía</h1>
        <p style="color: #64748b; margin-top: 0.5rem; font-size: 1.1rem;">Registra y valida la entrada de productos al almacén</p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["➕ Nueva Entrada", "📋 Historial"])

# --- Tab 1: Nueva Entrada ---
with tab1:
    st.markdown('<div style="background: white; padding: 2rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        referencia = st.text_input("Número de Referencia / Remito", placeholder="Ej: REM-2024-0001")
        doc_validado = st.checkbox("✅ Documentos validados", value=False)
    with col2:
        fecha_doc = st.date_input("Fecha de Documento")
    
    st.markdown("<hr style='border: 1px solid #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    productos = get_all_products()
    if not productos:
        alert_warning("No hay productos registrados en el sistema.")
    else:
        opciones_productos = [f"{p['sku']} - {p['nombre']}" for p in productos]
        producto_seleccionado = st.selectbox("Producto", opciones_productos, index=0)
        
        if producto_seleccionado:
            sku = producto_seleccionado.split(" - ")[0]
            producto = get_product_by_sku(sku)
            
            col3, col4 = st.columns(2)
            with col3:
                cantidad = st.number_input("Cantidad", min_value=1, value=1)
                lote = st.text_input("Número de Lote (opcional)", placeholder="Ej: LOTE-123")
            with col4:
                fecha_vencimiento = st.date_input("Fecha de Vencimiento (opcional)")
            
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
                        opciones_ubicaciones = [f"{u['codigo']} - Pasillo {u['pasillo']} / Estante {u['estante']}" for u in ubicaciones_zona]
                        ubicacion_seleccionada = st.selectbox("Ubicación Específica", opciones_ubicaciones, index=0)
                        
                        observaciones = st.text_area("Observaciones (opcional)", placeholder="Agrega notas importantes sobre la recepción...")
                        
                        if st.button("📝 Registrar Entrada", type="primary", use_container_width=True):
                            if not doc_validado:
                                alert_error("Primero valida los documentos antes de continuar!")
                            elif not ubicacion_seleccionada:
                                alert_error("Selecciona una ubicación!")
                            else:
                                ubicacion_codigo = ubicacion_seleccionada.split(" - ")[0]
                                ubicacion = next((u for u in ubicaciones_zona if u['codigo'] == ubicacion_codigo), None)
                                
                                if ubicacion:
                                    try:
                                        fecha_venc_str = fecha_vencimiento.isoformat() if fecha_vencimiento else None
                                        
                                        movement_id = create_movement(
                                            tipo="ENTRADA",
                                            producto_id=producto['id'],
                                            ubicacion_origen_id=None,
                                            ubicacion_destino_id=ubicacion['id'],
                                            cantidad=cantidad,
                                            referencia=referencia,
                                            observaciones=observaciones
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
    
    recent = get_recent_movements(20)
    if recent:
        df = pd.DataFrame([dict(row) for row in recent])
        df = df[['id', 'tipo', 'referencia', 'cantidad', 'estado', 'fecha_movimiento']]
        df.columns = ['ID', 'Tipo', 'Referencia', 'Cantidad', 'Estado', 'Fecha']
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        alert_info("No hay movimientos registrados aún.")
    st.markdown('</div>', unsafe_allow_html=True)
