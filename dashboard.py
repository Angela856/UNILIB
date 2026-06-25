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

# Ruta al archivo de métricas (sube un nivel si se ejecuta desde src/)
ruta_metricas = "metrics_history.json"
if not os.path.exists(ruta_metricas) and os.path.exists("../metrics_history.json"):
    ruta_metricas = "../metrics_history.json"

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
    # 3.) INDICADORES CLAVE DE RENDIMIENTO (KPIs) - IE1, IE2
    # =====================================================================
    total_consultas = len(df)
    errores = len(df[df['status'] == 'ERROR'])
    tasa_exito = ((total_consultas - errores) / total_consultas) * 100 if total_consultas > 0 else 100
    latencia_promedio = df['latency_sec'].mean()
    total_recursos = df['resource_chars'].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Consultas Auditadas", value=f"{total_consultas} req")
    col2.metric(label="Tasa de Consistencia (Éxito)", value=f"{tasa_exito:.1f}%", delta=f"-{errores} errores" if errores > 0 else "0 errores")
    col3.metric(label="Latencia Promedio", value=f"{latencia_promedio:.2f} seg")
    col4.metric(label="Consumo Acumulado", value=f"{total_recursos:,} caracteres")

    st.markdown("---")
    
    # =====================================================================
    # 4.) ANÁLISIS GRÁFICO INTERACTIVO - IE2, IE4, IE5
    # =====================================================================
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.subheader("📈 Línea de Tiempo de Latencia")
        fig_lat = px.line(
            df, x='timestamp', y='latency_sec', 
            title='Tiempo de Respuesta por Petición (Segundos)',
            labels={'latency_sec': 'Segundos', 'timestamp': 'Fecha/Hora'},
            markers=True, color_discrete_sequence=['#28a745']
        )
        st.plotly_chart(fig_lat, use_container_width=True)
        
    with right_col:
        st.subheader("🛠️ Auditoría de Herramientas (Tools)")
        # Descomponer las listas de herramientas ejecutadas
        all_tools = []
        for tools_list in df['tools_executed']:
            all_tools.extend(tools_list)
        
        df_tools = pd.DataFrame(all_tools, columns=['Herramienta'])
        tool_counts = df_tools['Herramienta'].value_counts().reset_index()
        tool_counts.columns = ['Herramienta', 'Frecuencia']
        
        fig_tools = px.bar(
            tool_counts, x='Herramienta', y='Frecuencia', 
            title='Frecuencia de Invocación por Módulo',
            color='Frecuencia', color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_tools, use_container_width=True)

    st.markdown("---")

    # =====================================================================
    # 5.) REGISTRO DE TRAZABILIDAD PROFUNDA - IE3
    # =====================================================================
    st.subheader("🪵 Historial de Eventos de Ejecución")
    st.markdown("Tabla de auditoría para identificar cuellos de botella o anomalías lógicas:")
    
    # Formatear el DataFrame para la vista del usuario
    df_visual = df[['timestamp', 'user_input', 'response', 'latency_sec', 'status', 'tools_executed']].copy()
    df_visual.columns = ['Fecha/Hora', 'Entrada Estudiante', 'Respuesta Agente', 'Latencia (s)', 'Estado', 'Herramientas Invocadas']
    
    st.dataframe(df_visual.sort_values(by='Fecha/Hora', ascending=False), use_container_width=True)
