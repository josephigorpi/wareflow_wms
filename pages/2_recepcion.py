"""Página de Recepción e Inspección de WareFlow WMS."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.alerts import alert_success, alert_error, alert_info, alert_warning
from components.forms import input_text, input_number, input_select, form_submit_button
from components.tables import render_table
from components.kpi_card import render_kpi_card
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
render_navbar(titulo="Recepción e Inspección", icono="📦")

# Métricas rápidas
recepciones_hoy = len([r for r in get_recepciones_recientes(100) if r['fecha_movimiento'].startswith(datetime.now().strftime('%Y-%m-%d'))])
pendientes = len(get_recepciones_pendientes())

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("Recepciones Hoy", recepciones_hoy, "📥", "green")
with col2:
    render_kpi_card("Pendientes Inspección", pendientes, "⏳", "orange")
with col3:
    productos_activos = len(get_all_products())
    render_kpi_card("Productos Activos", productos_activos, "📦", "blue")
with col4:
    ubicaciones_disponibles = len(get_available_locations())
    render_kpi_card("Ubicaciones Disponibles", ubicaciones_disponibles, "📍", "purple")

# Tabs para diferentes funcionalidades
tab1, tab2, tab3, tab4 = st.tabs([
    "📥 Registrar Recepción", 
    "🔍 Inspeccionar", 
    "📋 Historial de Recepciones",
    "📊 Estadísticas"
])

# Tab 1: Registrar Recepción
with tab1:
    st.header("Registrar Recepción de Mercancía")
    
    # Opciones de búsqueda de producto
    busqueda_tipo = st.radio(
        "Método de búsqueda",
        ["Buscar por SKU", "Seleccionar de lista"],
        horizontal=True
    )
    
    producto_id = None
    producto_info = None
    
    if busqueda_tipo == "Buscar por SKU":
        sku = st.text_input("Ingrese el SKU del producto").strip().upper()
        if sku:
            producto = get_product_by_sku(sku)
            if producto:
                producto_id = producto['id']
                producto_info = producto
                st.success(f"✅ Producto encontrado: {producto['nombre']} (SKU: {producto['sku']})")
                if producto.get('stock_total', 0) > 0:
                    st.info(f"Stock actual: {producto['stock_total']} unidades")
            elif sku:
                alert_warning("Producto no encontrado o inactivo")
    else:
        productos = get_all_products()
        if productos:
            producto_options = {f"{p['sku']} - {p['nombre']}": p["id"] for p in productos}
            selected = st.selectbox("Seleccionar Producto", list(producto_options.keys()))
            producto_id = producto_options[selected]
            producto_info = next((p for p in productos if p['id'] == producto_id), None)
    
    if producto_id and producto_info:
        with st.form("form_recepcion"):
            st.subheader(f"Producto: {producto_info['nombre']}")
            st.write(f"**SKU:** {producto_info['sku']}")
            st.write(f"**Unidad de medida:** {producto_info['unidad_medida']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
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
                # Opciones de ubicación
                ubicacion_opcion = st.radio(
                    "Asignación de ubicación",
                    ["Automática", "Manual"],
                    horizontal=True
                )
                
                ubicacion_id = None
                if ubicacion_opcion == "Manual":
                    ubicaciones = get_available_locations()
                    if ubicaciones:
                        ubicacion_options = {f"{u['codigo']} - {u.get('zona_nombre', 'Sin zona')}": u["id"] for u in ubicaciones}
                        selected_ubicacion = st.selectbox("Seleccionar Ubicación", list(ubicacion_options.keys()))
                        ubicacion_id = ubicacion_options[selected_ubicacion]
                        st.info(f"Ubicación seleccionada: {selected_ubicacion}")
                    else:
                        st.warning("No hay ubicaciones disponibles. Se usará asignación automática.")
                        ubicacion_opcion = "Automática"
                
                referencia = st.text_input("Referencia (Ej: Orden de Compra)", placeholder="OC-2024-001")
                
                observaciones = st.text_area("Observaciones (opcional)", placeholder="Condiciones de la mercancía, embalaje, etc.")
            
            # Campos adicionales para inspección rápida
            st.subheader("Estado de la Mercancía")
            estado_mercancia = st.selectbox(
                "Condición",
                ["Buen estado", "Con detalles menores", "Dañada", "Rechazar"]
            )
            
            if estado_mercancia == "Rechazar":
                motivo_rechazo = st.text_area("Motivo del rechazo", required=True)
            
            submitted = st.form_submit_button("Registrar Recepción", use_container_width=True)
            
            if submitted:
                try:
                    usuario_id = st.session_state.get("usuario_id")
                    
                    if estado_mercancia == "Rechazar":
                        # Crear recepción pero marcarla como rechazada
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
                        alert_warning(f"Recepción registrada pero marcada como RECHAZADA. Motivo: {motivo_rechazo}")
                    else:
                        # Recepción normal
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
                        alert_success(f"Recepción registrada exitosamente! ID: {movimiento_id}")
                        
                        if ubicacion_id:
                            st.info(f"Producto almacenado en ubicación: {selected_ubicacion if ubicacion_opcion == 'Manual' else 'Asignación automática'}")
                        else:
                            st.info("El producto está pendiente de asignación de ubicación. Pase a la pestaña 'Inspeccionar' para completar.")
                    
                    st.rerun()
                    
                except Exception as e:
                    alert_error(f"Error al registrar la recepción: {str(e)}")

# Tab 2: Inspeccionar
with tab2:
    st.header("Inspección de Recepciones Pendientes")
    
    pendientes = get_recepciones_pendientes()
    
    if not pendientes:
        alert_info("No hay recepciones pendientes de inspección.")
    else:
        st.info(f"Hay {len(pendientes)} recepciones pendientes de inspección.")
        
        # Mostrar lista de pendientes
        df_pendientes = pd.DataFrame(pendientes)
        
        # Seleccionar una recepción para inspeccionar
        opciones = {f"{r['id']} - {r['sku']} - {r['cantidad']} uds ({r['fecha_movimiento'][:10]})": r['id'] for r in pendientes}
        seleccion = st.selectbox("Seleccionar Recepción para Inspeccionar", list(opciones.keys()))
        
        if seleccion:
            movimiento_id = opciones[seleccion]
            movimiento = next(r for r in pendientes if r['id'] == movimiento_id)
            
            st.subheader("Detalles de la Recepción")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**ID:** {movimiento['id']}")
                st.write(f"**Producto:** {movimiento['sku']} - {movimiento['producto_nombre']}")
                st.write(f"**Cantidad:** {movimiento['cantidad']} unidades")
            with col2:
                st.write(f"**Fecha:** {movimiento['fecha_movimiento']}")
                st.write(f"**Referencia:** {movimiento['referencia'] or 'N/A'}")
                st.write(f"**Observaciones:** {movimiento['observaciones'] or 'Ninguna'}")
            
            st.divider()
            
            # Formulario de inspección
            with st.form("form_inspeccion"):
                st.subheader("Resultado de Inspección")
                
                col1, col2 = st.columns(2)
                with col1:
                    aprobado = st.selectbox(
                        "Decisión",
                        ["Aprobar", "Rechazar"],
                        index=0
                    ) == "Aprobar"
                    
                    if aprobado:
                        # Asignar ubicación durante la inspección
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
                
                submitted = st.form_submit_button("Guardar Inspección", use_container_width=True)
                
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
                                alert_success(f"✅ Recepción aprobada y almacenada en {selected_ubicacion if ubicacion_id else 'pendiente de ubicación'}")
                            else:
                                alert_warning("⚠️ Recepción rechazada. No se actualizará el inventario.")
                            st.rerun()
                        else:
                            alert_error("Error al procesar la inspección")
                            
                    except Exception as e:
                        alert_error(f"Error al guardar la inspección: {str(e)}")

# Tab 3: Historial de Recepciones
with tab3:
    st.header("Historial de Recepciones")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input(
            "Fecha Inicio",
            value=datetime.now().date() - timedelta(days=30)
        )
    with col2:
        fecha_fin = st.date_input(
            "Fecha Fin",
            value=datetime.now().date()
        )
    
    # Obtener recepciones
    recepciones = get_recepciones_recientes(limit=200)
    
    if recepciones:
        # Filtrar por fecha
        df_recepciones = pd.DataFrame(recepciones)
        
        # Convertir fechas
        df_recepciones['fecha'] = pd.to_datetime(df_recepciones['fecha_movimiento']).dt.date
        
        # Filtrar por rango de fechas
        mask = (df_recepciones['fecha'] >= fecha_inicio) & (df_recepciones['fecha'] <= fecha_fin)
        df_filtrado = df_recepciones[mask]
        
        if not df_filtrado.empty:
            # Mostrar estadísticas rápidas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Recepciones", len(df_filtrado))
            with col2:
                completados = len(df_filtrado[df_filtrado['estado'] == 'COMPLETADO'])
                st.metric("Completadas", completados)
            with col3:
                pendientes = len(df_filtrado[df_filtrado['estado'] != 'COMPLETADO'])
                st.metric("Pendientes/Rechazadas", pendientes)
            
            # Mostrar tabla
            columns_to_show = ["id", "sku", "producto_nombre", "cantidad", "destino_codigo", "referencia", "estado", "fecha_movimiento"]
            available_columns = [col for col in columns_to_show if col in df_filtrado.columns]
            render_table(df_filtrado[available_columns] if available_columns else df_filtrado)
        else:
            alert_info("No hay recepciones en el rango de fechas seleccionado.")
    else:
        alert_info("No hay recepciones registradas.")

# Tab 4: Estadísticas
with tab4:
    st.header("Estadísticas de Recepciones")
    
    # Gráfico de recepciones por día (simulado con datos reales)
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
        
        # Mostrar datos
        st.subheader("Resumen por Día")
        st.dataframe(df_agrupado, use_container_width=True)
        
        # Top productos recibidos
        st.subheader("Top 10 Productos Más Recibidos")
        top_productos = df.groupby(['sku', 'producto_nombre']).agg({
            'cantidad': 'sum'
        }).reset_index().sort_values('cantidad', ascending=False).head(10)
        
        if not top_productos.empty:
            st.dataframe(top_productos, use_container_width=True)
        
        # Estadísticas de estado
        st.subheader("Estado de Recepciones")
        estado_counts = df['estado'].value_counts().reset_index()
        estado_counts.columns = ['Estado', 'Cantidad']
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(estado_counts, use_container_width=True)
        with col2:
            # Mostrar como gráfico de barras simple
            st.bar_chart(estado_counts.set_index('Estado'))
    else:
        alert_info("No hay suficientes datos para mostrar estadísticas.") 
