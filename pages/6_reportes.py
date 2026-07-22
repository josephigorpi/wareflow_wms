"""Página de Reportes y KPIs de WareFlow WMS."""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from core.auth import require_auth
from core.permissions import require_permission
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from services.product_service import get_products_with_inventory, search_products
from services.location_service import get_locations_with_zones, count_locations_by_status
from services.movement_service import get_movements_by_date_range, get_movements_grouped_by_day
from utils.formatters import format_date

require_auth()
require_permission("reportes", "leer")

render_sidebar(current_page="reportes")
render_navbar(titulo="Reportes y KPIs", subtitulo="Análisis y métricas del sistema", icono="📈")

# KPI Cards globales
status_counts = count_locations_by_status()
products = get_products_with_inventory()
total_products = len(products) if products else 0

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.metric("📦 Total Productos", f"{total_products:,}")

with col2:
    st.metric("📍 Ubicaciones", f"{status_counts['total']:,}")

with col3:
    st.metric("🟢 Ocupación", f"{status_counts['ocupadas']:,}")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs modernos
tab1, tab2, tab3 = st.tabs(["📦 Productos", "📊 Movimientos", "🗺️ Ubicaciones"])

with tab1:
    st.markdown("### 📦 Reportes de Productos")
    
    query = st.text_input("Buscar por SKU o nombre", placeholder="Ej: PROD-001", key="search_products")
    
    if query:
        products = search_products(query)
    else:
        products = get_products_with_inventory()
    
    if products:
        df_products = pd.DataFrame(products)
        
        st.markdown("**Análisis ABC (Stock)**")
        df_products["valor_stock"] = df_products["stock_total"]
        
        df_abc = df_products.sort_values("stock_total", ascending=False)
        total_stock_total = df_abc["stock_total"].sum()
        df_abc["acumulado"] = df_abc["stock_total"].cumsum()
        df_abc["porcentaje_acumulado"] = (df_abc["acumulado"] / total_stock_total) * 100
        
        def categorizar_abc(porcentaje):
            if porcentaje <= 80:
                return "A"
            elif porcentaje <= 95:
                return "B"
            else:
                return "C"
        
        df_abc["categoria_abc"] = df_abc["porcentaje_acumulado"].apply(categorizar_abc)
        
        col_abc = px.bar(df_abc, x="categoria_abc", y="stock_total", 
                           title="Distribución ABC por Stock", color="categoria_abc",
                           color_discrete_map={"A": "#10B981", "B": "#F59E0B", "C": "#EF4444"})
        st.plotly_chart(col_abc, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Lista de productos**")
        df_display = df_abc[["sku", "nombre", "stock_total", "stock_minimo", "categoria_abc"]]
        df_display.columns = ["SKU", "Nombre", "Stock Total", "Stock Mínimo", "Categoría ABC"]
        
        def highlight_abc_row(row):
            if row["Categoría ABC"] == "A":
                return ['background-color: #dcfce7'] * len(row)
            elif row["Categoría ABC"] == "B":
                return ['background-color: #fef3c7'] * len(row)
            return ['background-color: #fee2e2'] * len(row)
        
        styled_df = df_display.style.apply(highlight_abc_row, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name=f"productos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv',
            use_container_width=True
        )
    else:
        st.info("ℹ️ No hay productos disponibles.")

with tab2:
    st.markdown("### 📊 Reportes de Movimientos")
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    today = datetime.now()
    with col1:
        fecha_inicio = st.date_input("Fecha inicio", value=today - timedelta(days=30))
    with col2:
        fecha_fin = st.date_input("Fecha fin", value=today)
    with col3:
        tipo_movimiento = st.selectbox("Tipo de movimiento", ["Todos", "ENTRADA", "SALIDA", "TRASLADO"], key="tipo_movimiento")
    
    tipo_filtro = tipo_movimiento if tipo_movimiento != "Todos" else None
    movements = get_movements_by_date_range(str(fecha_inicio), str(fecha_fin), tipo_filtro)
    
    if movements:
        df_movements = pd.DataFrame(movements)
        df_movements["fecha_movimiento"] = df_movements["fecha_movimiento"].apply(format_date)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Gráfico de movimientos por día**")
        grouped_movements = get_movements_grouped_by_day(str(fecha_inicio), str(fecha_fin))
        if grouped_movements:
            df_grouped = pd.DataFrame(grouped_movements)
            fig = px.line(df_grouped, x="fecha", y="cantidad", color="tipo", 
                         title="Movimientos por día",
                         color_discrete_map={"ENTRADA": "#10B981", "SALIDA": "#EF4444", "TRASLADO": "#F59E0B"})
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Lista de movimientos**")
        df_display = df_movements[["fecha_movimiento", "tipo", "sku", "producto_nombre", "cantidad", "usuario_nombre", "estado"]]
        df_display.columns = ["Fecha", "Tipo", "SKU", "Producto", "Cantidad", "Usuario", "Estado"]
        
        def highlight_tipo_row(row):
            if row["Tipo"] == "ENTRADA":
                return ['background-color: #dcfce7'] * len(row)
            elif row["Tipo"] == "SALIDA":
                return ['background-color: #fee2e2'] * len(row)
            return ['background-color: #fef3c7'] * len(row)
        
        styled_df = df_display.style.apply(highlight_tipo_row, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name=f"movimientos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv',
            use_container_width=True
        )
    else:
        st.info("ℹ️ No hay movimientos en el rango de fechas seleccionado.")

with tab3:
    st.markdown("### 🗺️ Reportes de Ubicaciones")
    
    status_counts = count_locations_by_status()
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.metric("📍 Total", f"{status_counts['total']:,}")
    with col2:
        st.metric("🟢 Ocupadas", f"{status_counts['ocupadas']:,}")
    with col3:
        st.metric("🔴 Libres", f"{status_counts['libres']:,}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    estado_filtro = st.selectbox("Filtrar por estado", ["Todos", "Ocupada", "Libre"], key="estado_ubicacion")
    
    locations = get_locations_with_zones()
    if locations:
        df_locations = pd.DataFrame(locations)
        
        if estado_filtro == "Ocupada":
            df_locations = df_locations[df_locations["ocupada"] == 1]
        elif estado_filtro == "Libre":
            df_locations = df_locations[df_locations["ocupada"] == 0]
        
        df_display = df_locations[["codigo", "zona_nombre", "pasillo", "estante", "nivel", "posicion", "ocupada"]]
        df_display["ocupada"] = df_display["ocupada"].apply(lambda x: "Sí" if x == 1 else "No")
        df_display.columns = ["Código", "Zona", "Pasillo", "Estante", "Nivel", "Posición", "Ocupada"]
        
        def highlight_ubicacion_row(row):
            if row["Ocupada"] == "Sí":
                return ['background-color: #fee2e2'] * len(row)
            return ['background-color: #dcfce7'] * len(row)
        
        styled_df = df_display.style.apply(highlight_ubicacion_row, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name=f"ubicaciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv',
            use_container_width=True
        )
    else:
        st.info("ℹ️ No hay ubicaciones disponibles.")
