import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registro de Plantões Cirúrgicos", layout="centered")

st.title("📋 Registro de Plantões Cirúrgicos")

# Sessões para armazenar dados
if "plantões" not in st.session_state:
    st.session_state["plantões"] = []

if "produtividade_mensal" not in st.session_state:
    st.session_state["produtividade_mensal"] = 0.0

# PRODUTIVIDADE MENSAL (campo separado, único por mês)
st.subheader("Produtividade mensal")
produtividade_input = st.number_input(
    "Informe o valor da produtividade mensal (R$)", min_value=0.0, format="%.2f"
)

if produtividade_input != st.session_state["produtividade_mensal"]:
    st.session_state["produtividade_mensal"] = produtividade_input

st.markdown("---")

# FORMULÁRIO DE REGISTRO DE PLANTÃO
st.subheader("Novo plantão")

data = st.date_input("Data", format="YYYY-MM-DD")
cirurgiao = st.text_input("Nome do cirurgião", "Washington Guimarães Damasceno")
local = st.selectbox("Local", ["Ambulatório", "Centro Cirúrgico", "Diarista"])

# Horários disponíveis e carga horária automática
opcoes_horario = {
    "07h - 13h": 6,
    "07h - 19h": 12,
    "13h - 19h": 6,
    "19h - 07h": 12,
}

horario = st.selectbox("Horário", list(opcoes_horario.keys()))
valor_hora = st.number_input("Valor da hora (R$)", min_value=0.0, value=160.0, format="%.2f")

# Botão para adicionar plantão
if st.button("Adicionar plantão"):
    st.session_state["plantões"].append({
        "data": data,
        "local": local,
        "horario": horario,
        "horas": opcoes_horario[horario],
        "valor_hora": valor_hora
    })
    st.success("Plantão registrado com sucesso.")

st.markdown("---")

# EXIBIÇÃO DOS PLANTÕES REGISTRADOS
st.subheader("Plantões registrados")
plantões = pd.DataFrame(st.session_state["plantões"])

if not plantões.empty:
    for local_unico in plantões["local"].unique():
        st.markdown(f"**{local_unico}**")
        total_horas_local = 0
        total_valor_local = 0

        for _, row in plantões[plantões["local"] == local_unico].iterrows():
            st.markdown(f"- {row['data'].strftime('%d/%m/%Y')} — {row['horario']} — {row['horas']}h")
            total_horas_local += row['horas']
            total_valor_local += row['horas'] * row['valor_hora']

        st.markdown(f"**Total: {total_horas_local} horas = R$ {total_valor_local:,.2f}**")

    # RESUMO FINAL
    st.markdown("---")
    st.subheader("Resumo final:")

    total_horas = plantões["horas"].sum()
    valor_plantões = sum(p["horas"] * p["valor_hora"] for p in st.session_state["plantões"])
    produtividade = st.session_state["produtividade_mensal"]
    total_geral = valor_plantões + produtividade

    st.markdown(f"Total de horas trabalhadas: {total_horas}h")
    st.markdown(f"Valor pelos plantões: R$ {valor_plantões:,.2f}")
    st.markdown(f"Produtividade mensal: R$ {produtividade:,.2f}")
    st.markdown(f"**Total geral: R$ {total_geral:,.2f}**")
else:
    st.info("Nenhum plantão registrado até o momento.")
