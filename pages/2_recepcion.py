"""Página de Recepción e Inspección de WareFlow WMS."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.ui_helpers import svg_icon, section_title, kpi_card, alert_card, spacer
from services.product_service import get_all_products, get_product_by_sku, search_products
from services.location_service import get_all_locations, get_available_locations
from services.movement_service import (
    create_recepcion, 
    get_recepciones_recientes,
    get_recepciones_pendientes,
    update_recepcion_with_inspection
)

require_auth()
require_permission("recepcion", "leer")

render_sidebar(current_page="recepcion")
render_navbar(titulo="Recepción e Inspección", subtitulo="Gestión de entrada de mercancía", icono="inbox")

# KPI Cards
recepciones_hoy = len([r for r in get_recepciones_recientes(100) if r['fecha_movimiento'].startswith(datetime.now().strftime('%Y-%m-%d'))])
pendientes = len(get_recepciones_pendientes())
productos_activos = len(get_all_products())
ubicaciones_disponibles = len(get_available_locations())

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.markdown(kpi_card("arrow-down", "Recepciones hoy", f"{recepciones_hoy:,}"), unsafe_allow_html=True)

with col2:
    st.markdown(kpi_card("list", "Pendientes", f"{pendientes:,}"), unsafe_allow_html=True)

with col3:
    st.markdown(kpi_card("box", "Productos", f"{productos_activos:,}"), unsafe_allow_html=True)

with col4:
    st.markdown(kpi_card("pin", "Ubicaciones libres", f"{ubicaciones_disponibles:,}"), unsafe_allow_html=True)

spacer()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Registrar Recepción", 
    "Inspeccionar", 
    "Historial",
    "Estadísticas"
])

# Tab 1: Registrar Recepción
with tab1:
    section_title("inbox", "Registrar recepción")
    
    # Opciones de búsqueda de producto
    section_title("search", "Método de búsqueda")
    col_a, col_b = st.columns(2, gap="medium")
    with col_a:
        busqueda_sku = st.button("Buscar por SKU", use_container_width=True)
    with col_b:
        busqueda_lista = st.button("Seleccionar de lista", use_container_width=True)
    
    # Determinar método seleccionado
    if 'busqueda_tipo' not in st.session_state:
        st.session_state.busqueda_tipo = "sku"
    
    if busqueda_sku:
        st.session_state.busqueda_tipo = "sku"
    elif busqueda_lista:
        st.session_state.busqueda_tipo = "lista"
    
    producto_id = None
    producto_info = None
    
    if st.session_state.busqueda_tipo == "sku":
        sku = st.text_input("Ingrese el SKU del producto", placeholder="Ej: PROD-001").strip().upper()
        if sku:
            producto = get_product_by_sku(sku)
            if producto:
                producto_id = producto['id']
                producto_info = producto
                st.success(f"✅ Producto encontrado: {producto['nombre']} (SKU: {producto['sku']})")
                if producto.get('stock_total', 0) > 0:
                    st.info(f"Stock actual: {producto['stock_total']} unidades")
            elif sku:
                st.warning("Producto no encontrado o inactivo")
    else:
        productos = get_all_products()
        if productos:
            producto_options = {f"{p['sku']} - {p['nombre']}": p["id"] for p in productos}
            selected = st.selectbox("Seleccionar Producto", list(producto_options.keys()))
            producto_id = producto_options[selected]
            producto_info = next((p for p in productos if p['id'] == producto_id), None)
    
    if producto_id and producto_info:
        with st.form("form_recepcion"):
            # Card con información del producto
            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); 
                            border-radius: 0.75rem; 
                            padding: 1.25rem; 
                            margin-bottom: 1.5rem;
                            border: 1px solid #BFDBFE;'>
                    <h4 style='margin: 0 0 0.5rem 0; color: #1E40AF; font-size: 1.1rem; font-weight: 600;'>
                        {producto_info['nombre']}
                    </h4>
                    <p style='margin: 0.25rem 0; color: #3B82F6; font-size: 0.9rem;'>
                        <strong>SKU:</strong> {producto_info['sku']}
                    </p>
                    <p style='margin: 0.25rem 0; color: #64748B; font-size: 0.9rem;'>
                        <strong>Unidad:</strong> {producto_info['unidad_medida']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            col1, col2 = st.columns(2, gap="medium")
            
            with col1:
                section_title("box", "Información de la recepción")
                cantidad = st.number_input(
                    "Cantidad a recibir", 
                    min_value=1, 
                    value=1,
                    step=1
                )
                
                lote = st.text_input("Número de Lote (opcional)", placeholder="Ej: LOTE-2024-001")
                
                fecha_vencimiento = st.date_input(
                    "Fecha de Vencimiento (opcional)",
                    value=None,
                    min_value=datetime.now().date(),
                    max_value=datetime.now().date() + timedelta(days=365*5)
                )
            
            with col2:
                section_title("pin", "Ubicación y referencia")
                ubicacion_opcion = st.selectbox(
                    "Asignación de ubicación",
                    ["Automática", "Manual"]
                )
                
                ubicacion_id = None
                if ubicacion_opcion == "Manual":
                    ubicaciones = get_available_locations()
                    if ubicaciones:
                        ubicacion_options = {f"{u['codigo']} - {u.get('zona_nombre', 'Sin zona')}": u["id"] for u in ubicaciones}
                        selected_ubicacion = st.selectbox("Seleccionar Ubicación", list(ubicacion_options.keys()))
                        ubicacion_id = ubicacion_options[selected_ubicacion]
                    else:
                        st.warning("No hay ubicaciones disponibles. Se usará asignación automática.")
                        ubicacion_opcion = "Automática"
                
                referencia = st.text_input("Referencia (Ej: Orden de Compra)", placeholder="OC-2024-001")
                
                observaciones = st.text_area("Observaciones (opcional)", placeholder="Condiciones de la mercancía, embalaje, etc.")
            
            spacer()
            section_title("alert", "Estado de la mercancía")
            estado_mercancia = st.selectbox(
                "Condición",
                ["Buen estado", "Con detalles menores", "Dañada", "Rechazar"]
            )
            
            if estado_mercancia == "Rechazar":
                motivo_rechazo = st.text_area("Motivo del rechazo", required=True)
            
            spacer()
            submitted = st.form_submit_button("Registrar Recepción", use_container_width=True, type="primary")
            
            if submitted:
                try:
                    usuario_id = st.session_state.get("usuario_id")
                    
                    if estado_mercancia == "Rechazar":
                        movimiento_id = create_recepcion(
                            producto_id=producto_id,
                            cantidad=cantidad,
                            ubicacion_id=None,
                            lote=lote if lote else None,
                            fecha_vencimiento=fecha_vencimiento.strftime('%Y-%m-%d') if fecha_vencimiento else None,
                            referencia=referencia,
                            observaciones=f"{observaciones or ''} - RECHAZADA: {motivo_rechazo}",
                            usuario_id=usuario_id
                        )
                        st.warning(f"⚠️ Recepción registrada pero marcada como RECHAZADA. Motivo: {motivo_rechazo}")
                    else:
                        movimiento_id = create_recepcion(
                            producto_id=producto_id,
                            cantidad=cantidad,
                            ubicacion_id=ubicacion_id,
                            lote=lote if lote else None,
                            fecha_vencimiento=fecha_vencimiento.strftime('%Y-%m-%d') if fecha_vencimiento else None,
                            referencia=referencia,
                            observaciones=f"{observaciones or ''} - Estado: {estado_mercancia}",
                            usuario_id=usuario_id
                        )
                        st.success(f"✅ Recepción registrada exitosamente! ID: {movimiento_id}")
                        
                        if ubicacion_id:
                            st.info(f"Producto almacenado en ubicación: {selected_ubicacion if ubicacion_opcion == 'Manual' else 'Asignación automática'}")
                        else:
                            st.info("El producto está pendiente de asignación de ubicación.")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al registrar la recepción: {str(e)}")

# Tab 2: Inspeccionar
with tab2:
    section_title("search", "Inspección de recepciones pendientes")
    
    pendientes = get_recepciones_pendientes()
    
    if not pendientes:
        st.info("✅ No hay recepciones pendientes de inspección.")
    else:
        st.info(f"Hay {len(pendientes)} recepciones pendientes de inspección.")
        
        # Mostrar lista de pendientes
        df_pendientes = pd.DataFrame(pendientes)
        
        # Seleccionar una recepción para inspeccionar
        opciones = {f"{r['id']} - {r['sku']} - {r['cantidad']} uds ({r['fecha_movimiento'][:10]})": r['id'] for r in pendientes}
        seleccion = st.selectbox("Seleccionar recepción para inspeccionar", list(opciones.keys()))
        
        if seleccion:
            movimiento_id = opciones[seleccion]
            movimiento = next(r for r in pendientes if r['id'] == movimiento_id)
            
            # Card con detalles de la recepción
            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); 
                            border-radius: 0.75rem; 
                            padding: 1.25rem; 
                            margin-bottom: 1.5rem;
                            border: 1px solid #FCD34D;'>
                    <h4 style='margin: 0 0 1rem 0; color: #92400E; font-size: 1.1rem; font-weight: 600;'>
                        Detalles de la recepción
                    </h4>
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;'>
                        <p style='margin: 0; color: #78350F; font-size: 0.9rem;'><strong>ID:</strong> {movimiento['id']}</p>
                        <p style='margin: 0; color: #78350F; font-size: 0.9rem;'><strong>Fecha:</strong> {movimiento['fecha_movimiento']}</p>
                        <p style='margin: 0; color: #78350F; font-size: 0.9rem;'><strong>Producto:</strong> {movimiento['sku']} - {movimiento['producto_nombre']}</p>
                        <p style='margin: 0; color: #78350F; font-size: 0.9rem;'><strong>Cantidad:</strong> {movimiento['cantidad']} unidades</p>
                        <p style='margin: 0; color: #78350F; font-size: 0.9rem;'><strong>Referencia:</strong> {movimiento['referencia'] or 'N/A'}</p>
                        <p style='margin: 0; color: #78350F; font-size: 0.9rem;'><strong>Observaciones:</strong> {movimiento['observaciones'] or 'Ninguna'}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Formulario de inspección
            with st.form("form_inspeccion"):
                section_title("check", "Resultado de inspección")
                
                col1, col2 = st.columns(2, gap="medium")
                with col1:
                    aprobado = st.selectbox(
                        "Decisión",
                        ["Aprobar", "Rechazar"],
                        index=0
                    ) == "Aprobar"
                    
                    if aprobado:
                        ubicaciones = get_available_locations()
                        if ubicaciones:
                            ubicacion_options = {f"{u['codigo']} - {u.get('zona_nombre', 'Sin zona')}": u["id"] for u in ubicaciones}
                            selected_ubicacion = st.selectbox("Asignar Ubicación", list(ubicacion_options.keys()))
                            ubicacion_id = ubicacion_options[selected_ubicacion]
                        else:
                            st.warning("No hay ubicaciones disponibles. El producto quedará sin asignar.")
                            ubicacion_id = None
                    else:
                        ubicacion_id = None
                        st.warning("⚠️ Esta recepción será rechazada.")
                
                with col2:
                    lote_inspeccion = st.text_input("Número de Lote (opcional)", placeholder="Ej: LOTE-2024-001")
                    
                    fecha_vencimiento_inspeccion = st.date_input(
                        "Fecha de Vencimiento (opcional)",
                        value=None,
                        min_value=datetime.now().date(),
                        max_value=datetime.now().date() + timedelta(days=365*5)
                    )
                
                observaciones_inspeccion = st.text_area(
                    "Observaciones de Inspección",
                    placeholder="Detalles de la inspección, condiciones, calidad, etc."
                )
                
                spacer()
                submitted = st.form_submit_button("Guardar Inspección", use_container_width=True, type="primary")
                
                if submitted:
                    try:
                        usuario_id = st.session_state.get("usuario_id")
                        
                        success = update_recepcion_with_inspection(
                            movimiento_id=movimiento_id,
                            ubicacion_id=ubicacion_id,
                            lote=lote_inspeccion if lote_inspeccion else None,
                            fecha_vencimiento=fecha_vencimiento_inspeccion.strftime('%Y-%m-%d') if fecha_vencimiento_inspeccion else None,
                            observaciones=observaciones_inspeccion,
                            usuario_id=usuario_id,
                            aprobado=aprobado
                        )
                        
                        if success:
                            if aprobado:
                                st.success(f"✅ Recepción aprobada y almacenada en {selected_ubicacion if ubicacion_id else 'pendiente de ubicación'}")
                            else:
                                st.warning("⚠️ Recepción rechazada. No se actualizará el inventario.")
                            st.rerun()
                        else:
                            st.error("Error al procesar la inspección")
                            
                    except Exception as e:
                        st.error(f"❌ Error al guardar la inspección: {str(e)}")

# Tab 3: Historial de Recepciones
with tab3:
    section_title("list", "Historial de recepciones")
    
    # Filtros
    section_title("filter", "Filtrar por fecha")
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        fecha_inicio = st.date_input(
            "Fecha inicio",
            value=datetime.now().date() - timedelta(days=30)
        )
    with col2:
        fecha_fin = st.date_input(
            "Fecha fin",
            value=datetime.now().date()
        )
    
    recepciones = get_recepciones_recientes(limit=200)
    
    if recepciones:
        df_recepciones = pd.DataFrame(recepciones)
        
        if 'fecha_movimiento' in df_recepciones.columns:
            df_recepciones['fecha'] = pd.to_datetime(df_recepciones['fecha_movimiento']).dt.date
        else:
            df_recepciones['fecha'] = datetime.now().date()
        
        mask = (df_recepciones['fecha'] >= fecha_inicio) & (df_recepciones['fecha'] <= fecha_fin)
        df_filtrado = df_recepciones[mask]
        
        if not df_filtrado.empty:
            # KPIs del historial
            col1, col2, col3 = st.columns(3, gap="medium")
            with col1:
                st.markdown(kpi_card("box", "Total", f"{len(df_filtrado):,}"), unsafe_allow_html=True)
            with col2:
                completados = len(df_filtrado[df_filtrado['estado'] == 'COMPLETADO'])
                st.markdown(kpi_card("check", "Completadas", f"{completados:,}"), unsafe_allow_html=True)
            with col3:
                pendientes = len(df_filtrado[df_filtrado['estado'] != 'COMPLETADO'])
                st.markdown(kpi_card("list", "Pendientes", f"{pendientes:,}"), unsafe_allow_html=True)
            
            spacer()
            
            # Tabla con estilos
            columns_to_show = ["id", "sku", "producto_nombre", "cantidad", "destino_codigo", "referencia", "estado", "fecha_movimiento"]
            available_columns = [col for col in columns_to_show if col in df_filtrado.columns]
            
            def highlight_estado_row(row):
                if row['estado'] == 'COMPLETADO':
                    return ['background-color: #dcfce7'] * len(row)
                elif row['estado'] == 'PENDIENTE':
                    return ['background-color: #fef9c3'] * len(row)
                elif row['estado'] == 'RECHAZADO':
                    return ['background-color: #fee2e2'] * len(row)
                return [''] * len(row)
            
            styled_df = df_filtrado[available_columns].style.apply(highlight_estado_row, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay recepciones en el rango de fechas seleccionado.")
    else:
        st.info("No hay recepciones registradas.")

# Tab 4: Estadísticas
with tab4:
    section_title("bar-chart", "Estadísticas de recepciones")
    
    recepciones = get_recepciones_recientes(limit=500)
    
    if recepciones:
        df = pd.DataFrame(recepciones)
        df['fecha'] = pd.to_datetime(df['fecha_movimiento']).dt.date
        
        # Agrupar por fecha
        df_agrupado = df.groupby('fecha').agg({
            'id': 'count',
            'cantidad': 'sum'
        }).reset_index()
        df_agrupado.columns = ['Fecha', 'Número de Recepciones', 'Total Unidades']
        
        # Resumen por día
        section_title("list", "Resumen por día")
        st.dataframe(df_agrupado, use_container_width=True, hide_index=True)
        
        # Top productos recibidos
        spacer()
        section_title("box", "Top 10 productos más recibidos")
        top_productos = df.groupby(['sku', 'producto_nombre']).agg({
            'cantidad': 'sum'
        }).reset_index().sort_values('cantidad', ascending=False).head(10)
        
        if not top_productos.empty:
            st.dataframe(top_productos, use_container_width=True, hide_index=True)
        
        # Estadísticas de estado
        spacer()
        section_title("alert", "Estado de recepciones")
        estado_counts = df['estado'].value_counts().reset_index()
        estado_counts.columns = ['Estado', 'Cantidad']
        
        col1, col2 = st.columns([2, 1], gap="medium")
        with col1:
            st.dataframe(estado_counts, use_container_width=True, hide_index=True)
        with col2:
            st.bar_chart(estado_counts.set_index('Estado'))
    else:
        st.info("No hay suficientes datos para mostrar estadísticas.") 
