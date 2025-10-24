import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# === Conexão com o banco ===
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Lu281011*",
    database="service_desk"
)

df = pd.read_sql("SELECT * FROM chamados", conn)
conn.close()

# === Layout ===
st.set_page_config(page_title="Dashboard de Chamados - GLPI", layout="wide")
st.title("📊 Dashboard de Chamados - GLPI")

# === Métricas ===
col1, col2, col3 = st.columns(3)
col1.metric("Total de chamados", len(df))
col2.metric("Tempo médio de resolução", str(df['tempo_resolucao'].mean()))
col3.metric("SLA Cumprido (%)", f"{df['sla_cumprido'].mean()*100:.1f}%")

# === Gráficos ===
col1, col2 = st.columns(2)

if 'status' in df.columns:
    df_status_counts = df['status'].value_counts().reset_index()
    df_status_counts.columns = ['status', 'count']  # renomeia colunas
    fig_status = px.bar(
        df_status_counts,
        x='status',
        y='count',
        labels={'status': 'Status', 'count': 'Quantidade'},
        title='Chamados por Status'
    )
    col1.plotly_chart(fig_status, use_container_width=True)

if 'tecnico' in df.columns:
    df_tecnico_counts = df['tecnico'].value_counts().reset_index()
    df_tecnico_counts.columns = ['tecnico', 'count']  # renomeia colunas
    fig_tecnico = px.bar(
        df_tecnico_counts,
        x='tecnico',
        y='count',
        labels={'tecnico': 'Técnico', 'count': 'Chamados'},
        title='Chamados por Técnico'
    )
    col2.plotly_chart(fig_tecnico, use_container_width=True)

# === Evolução por data ===
if 'data_abertura' in df.columns:
    df['data_abertura'] = pd.to_datetime(df['data_abertura'], errors='coerce')
    chamados_por_dia = df.groupby(df['data_abertura'].dt.date).size().reset_index(name='Chamados')
    fig_tempo = px.line(chamados_por_dia, x='data_abertura', y='Chamados', title='Chamados ao longo do tempo')
    st.plotly_chart(fig_tempo, use_container_width=True)

