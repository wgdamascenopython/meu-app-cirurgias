import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registro de Plantões", layout="centered")

st.title("📋 Registro de Plantões Cirúrgicos")

# Inicializa a sessão de estado para armazenar os plantões
if "plantoes" not in st.session_state:
    st.session_state.plantoes = []
if "produtividade_mensal" not in st.session_state:
    st.session_state.produtividade_mensal = 0.0

# Entrada de dados
with st.form("formulario_plantao"):
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", value=datetime.today())
        local = st.selectbox("Local", ["Centro Cirúrgico", "Ambulatório", "Diarista"])
        horario = st.selectbox("Horário", ["07h - 13h", "07h - 19h", "13h - 19h"])
    with col2:
        nome = st.text_input("Nome do cirurgião")
        valor_hora = st.number_input("Valor da hora (R$)", min_value=0.0, format="%.2f")
        produtividade_mensal = st.number_input("Produtividade mensal (R$)", min_value=0.0, format="%.2f")

    enviar = st.form_submit_button("Adicionar plantão")

    if enviar:
        horas_por_turno = {
            "07h - 13h": 6,
            "07h - 19h": 12,
            "13h - 19h": 6
        }
        horas = horas_por_turno.get(horario, 0)
        plantao = {
            "data": data.strftime("%d/%m/%Y"),
            "local": local,
            "nome": nome,
            "horario": horario,
            "horas": horas,
            "valor_hora": valor_hora
        }
        st.session_state.plantoes.append(plantao)
        st.session_state.produtividade_mensal = produtividade_mensal

# Lista de plantões registrados
st.subheader("📌 Plantões registrados")
for i, p in enumerate(st.session_state.plantoes):
    col1, col2 = st.columns([10, 1])
    with col1:
        st.markdown(
            f"- 📅 {p['data']} | 🏥 {p['local']} | 👨‍⚕️ {p['nome']} | 🕒 {p['horario']} | ⏱️ {p['horas']}h | 💰 R$ {p['valor_hora']:.2f}/h"
        )
    with col2:
        if st.button("❌", key=f"delete_{i}"):
            st.session_state.plantoes.pop(i)
            st.experimental_rerun()

# Geração do relatório
if st.session_state.plantoes:
    st.subheader("📄 Relatório final")
    df = pd.DataFrame(st.session_state.plantoes)
    relatorio = ""

    for local in df['local'].unique():
        relatorio += f"\n📍 **{local.upper()}**\n"
        df_local = df[df['local'] == local]
        total_horas = 0
        total_valor = 0
        for _, row in df_local.iterrows():
            valor_total = row['horas'] * row['valor_hora']
            relatorio += f"- {row['data']} - {row['nome']} - {row['horario']} - {row['horas']}h - R$ {valor_total:.2f}\n"
            total_horas += row['horas']
            total_valor += valor_total
        relatorio += f"**Total de horas:** {total_horas}h\n"
        relatorio += f"**Total R$:** R$ {total_valor:.2f}\n"

    relatorio += f"\n📌 **Produtividade mensal:** R$ {st.session_state.produtividade_mensal:.2f}"
    st.text_area("Relatório gerado:", value=relatorio, height=300)
