import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registro de Plantões Cirúrgicos", layout="centered")

st.markdown("# 📝 Registro de Plantões Cirúrgicos")

# Inicializa o estado da sessão
if "registros" not in st.session_state:
    st.session_state.registros = []

# Formulário de registro
with st.form("registro_form"):
    data = st.date_input("Data", value=datetime.today())
    nome = st.text_input("Nome do cirurgião", "Washington Guimarães Damasceno")

    local = st.selectbox("Local", ["Ambulatório", "Centro Cirúrgico", "Diarismo"])

    horario = st.selectbox("Horário", ["07h - 13h", "07h - 19h", "13h - 19h", "19h - 07h"])

    horas_por_turno = {
        "07h - 13h": 6,
        "07h - 19h": 12,
        "13h - 19h": 6,
        "19h - 07h": 12
    }
    horas = horas_por_turno[horario]

    valor_hora = st.number_input("Valor da hora (R$)", min_value=0.0, value=160.0, step=10.0)

    produtividade_mensal = st.number_input("Produtividade mensal (R$)", min_value=0.0, value=0.0, step=100.0)

    submitted = st.form_submit_button("Adicionar plantão")

    if submitted:
        st.session_state.registros.append({
            "data": data.strftime("%d/%m/%Y"),
            "local": local,
            "horario": horario,
            "horas": horas,
            "valor_hora": valor_hora,
            "produtividade_mensal": produtividade_mensal
        })
        st.success("✅ Plantão registrado com sucesso!")

# Exibição dos plantões
if st.session_state.registros:
    st.markdown("## 📌 Plantões registrados")
    df = pd.DataFrame(st.session_state.registros)

    # Agrupar por local
    for local in df["local"].unique():
        st.markdown(f"### 📍 {local}")
        df_local = df[df["local"] == local]
        total_horas = df_local["horas"].sum()
        total_valor = (df_local["horas"] * df_local["valor_hora"]).sum()

        linhas = []
        for _, row in df_local.iterrows():
            linha = f"- {row['data']} - {row['horario']} - {int(row['horas'])}h"
            linhas.append(linha)

        st.markdown("\n".join(linhas))
        st.markdown(f"**Total: {int(total_horas)} horas = R$ {total_valor:,.2f}**")

    # Mostrar total geral + produtividade
    total_geral_horas = df["horas"].sum()
    total_geral_valor = (df["horas"] * df["valor_hora"]).sum()
    total_produtividade = df["produtividade_mensal"].sum()
    total_completo = total_geral_valor + total_produtividade

    st.markdown("---")
    st.markdown("### 🧾 Resumo final:")
    st.markdown(f"**🕒 Total de horas trabalhadas:** {int(total_geral_horas)}h")
    st.markdown(f"**💰 Valor pelos plantões:** R$ {total_geral_valor:,.2f}")
    st.markdown(f"**📈 Produtividade mensal:** R$ {total_produtividade:,.2f}")
    st.markdown(f"**🧮 Total geral:** R$ {total_completo:,.2f}")
