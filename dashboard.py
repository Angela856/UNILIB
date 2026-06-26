import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# 1.) CONFIGURACIÓN ESTÉTICA DE LA PÁGINA
st.set_page_config(
    page_title="UNILIB - Panel de Observabilidad",
    layout="wide",
    page_icon="📊"
)

st.title("📊 UNILIB V3 - Panel de Observabilidad y Trazabilidad")
st.markdown("Monitoreo continuo de consistencia, latencia, uso de recursos y seguridad del Agente Autónomo.")
st.markdown("---")

# Ruta directa al archivo de métricas en la raíz del proyecto
ruta_metricas = "metrics_history.json"

# 2.) VALIDACIÓN DE DATOS EXISTENTES
if not os.path.exists(ruta_metricas):
    st.warning("⚠️ No se ha encontrado el archivo 'metrics_history.json'. Ejecuta e interactúa primero con el agente para generar datos de auditoría.")
else:
    # Cargar histórico estructurado
    with open(ruta_metricas, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Conversión a DataFrame de Pandas para analítica de datos
    df = pd.DataFrame(data)
    df['latency_sec'] = df['latency_sec'].astype(float)
    df['resource_chars'] = df['resource_chars'].astype(int)
    
    # =====================================================================
    # 3.) INDICADORES CLAVE DE RENDIMIENTO (KPIs)
    # =====================================================================
    total_consultas = len(df)
    errores = len(df[df['status'] == 'ERROR'])
    tasa_exito = ((total_consultas - errores) / total_consultas) * 100 if total_consultas > 0 else 100
    latencia_promedio = df['latency_sec'].mean()
    total_recursos = df['resource_chars'].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Consultas", value=f"{total_consultas} req")
    col2.metric(label="Tasa de Consistencia", value=f"{tasa_exito:.1f}%")
    col3.metric(label="Latencia Promedio", value=f"{latencia_promedio:.2f} seg")
    col4.metric(label="Consumo Acumulado", value=f"{total_recursos:,} chars")

    st.markdown("---")
    
    # =====================================================================
    # 4.) ANÁLISIS GRÁFICO INTERACTIVO
    # =====================================================================
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.subheader("📈 Mish-Línea de Tiempo de Latencia")
        fig_lat = px.line(
            df, x='timestamp', y='latency_sec', 
            title='Tiempo de Respuesta (Segundos)',
            labels={'latency_sec': 'latency_sec', 'timestamp': 'timestamp'},
            markers=True, color_discrete_sequence=['#28a745']
        )
        st.plotly_chart(fig_lat, use_container_width=True)
        
    with right_col:
        st.subheader("🛠️ Auditoría de Herramientas")
        # Descomponer las listas de herramientas ejecutadas
        all_tools = []
        for tools_list in df['tools_executed']:
            if not tools_list:
                all_tools.extend(['Ninguna'])
            else:
                all_tools.extend(tools_list)
        
        df_tools = pd.DataFrame(all_tools, columns=['Herramienta'])
        tool_counts = df_tools['Herramienta'].value_counts().reset_index()
        tool_counts.columns = ['Herramienta', 'Frecuencia']
        
        fig_tools = px.bar(
            tool_counts, x='Herramienta', y='Frecuencia', 
            title='Uso de Módulos',
            color='Frecuencia', color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_tools, use_container_width=True)

    st.markdown("---")

    # =====================================================================
    # 5.) REGISTRO DE TRAZABILIDAD PROFUNDA
    # =====================================================================
    st.subheader("🪵 Historial de Eventos de Ejecución")
    
    df_visual = df[['timestamp', 'user_input', 'response', 'latency_sec', 'status', 'tools_executed']].copy()
    st.dataframe(df_visual.sort_values(by='timestamp', ascending=False), use_container_width=True)
