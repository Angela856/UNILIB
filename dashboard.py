%%writefile dashboard.py
import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

st.set_page_config(page_title="UNILIB - Panel de Observabilidad", layout="wide", page_icon="📊")
st.title("📊 UNILIB V3 - Panel de Observabilidad y Trazabilidad")
st.markdown("Monitoreo continuo del Agente Autónomo.")
st.markdown("---")

ruta_metricas = "metrics_history.json"

if not os.path.exists(ruta_metricas):
    st.warning("⚠️ No se ha encontrado el archivo 'metrics_history.json'. Interactúa primero con el agente para generar datos.")
else:
    with open(ruta_metricas, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['latency_sec'] = df['latency_sec'].astype(float)
    df['resource_chars'] = df['resource_chars'].astype(int)
    
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
    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader(" Mish-Línea de Tiempo de Latencia")
        fig_lat = px.line(df, x='timestamp', y='latency_sec', title='Tiempo de Respuesta (Segundos)', markers=True, color_discrete_sequence=['#28a745'])
        st.plotly_chart(fig_lat, use_container_width=True)
    with right_col:
        st.subheader("🛠️ Auditoría de Herramientas")
        all_tools = [t for tl in df['tools_executed'] for t in tl]
        if all_tools:
            df_tools = pd.DataFrame(all_tools, columns=['Herramienta'])
            tool_counts = df_tools['Herramienta'].value_counts().reset_index()
            tool_counts.columns = ['Herramienta', 'Frecuencia']
            fig_tools = px.bar(tool_counts, x='Herramienta', y='Frecuencia', title='Uso de Módulos', color='Frecuencia', color_continuous_scale='Blues')
            st.plotly_chart(fig_tools, use_container_width=True)
        else:
            st.info("No se han ejecutado herramientas aún.")

    st.markdown("---")
    st.subheader("🪵 Historial de Eventos de Ejecución")
    df_visual = df[['timestamp', 'user_input', 'response', 'latency_sec', 'status', 'tools_executed']].copy()
    st.dataframe(df_visual.sort_values(by='timestamp', ascending=False), use_container_width=True)
