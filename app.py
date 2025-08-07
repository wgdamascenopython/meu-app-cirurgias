import streamlit as st
import pandas as pd

st.set_page_config(page_title="Relatório de Cirurgias", layout="centered")

st.title("Registro de Cirurgias")

# Campos de entrada
nome_medico = st.text_input("Nome do médico")

# Inicializa o estado da sessão se não existir
if "cirurgias" not in st.session_state:
    st.session_state.cirurgias = []

# Formulário para adicionar cirurgia
with st.form(key="form_cirurgia"):
    data = st.date_input("Data")
    local = st.selectbox("Local", ["Ambulatório", "Centro Cirúrgico", "Diarismo"])
    horario = st.selectbox("Horário", [
        "07:00 - 19:00",
        "19:00 - 07:00",
        "07:00 - 13:00",
        "13:00 - 19:00"
    ])
    horas = st.number_input("Quantidade de horas", min_value=1, max_value=24, step=1)
    valor_hora = st.number_input("Valor da hora (R$)", min_value=0.0, step=10.0, value=100.0)
    adicionar = st.form_submit_button("Adicionar plantão")

    if adicionar:
        st.session_state.cirurgias.append({
            "data": data.strftime("%d/%m/%Y"),
            "local": local,
            "horario": horario,
            "horas": horas,
            "valor_hora": valor_hora
        })

# Exibir tabela com botão de excluir
if st.session_state.cirurgias:
    st.subheader("Plantões registrados")
    for i, cirurgia in enumerate(st.session_state.cirurgias):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.write(
                f"📅 **{cirurgia['data']}** | 🏥 {cirurgia['local']} | 🕒 {cirurgia['horario']} "
                f"| ⏱️ {cirurgia['horas']}h | 💰 R$ {cirurgia['valor_hora']}/h"
            )
        with col2:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.cirurgias.pop(i)
                st.experimental_rerun()

# Gerar relatório
if nome_medico and st.session_state.cirurgias:
    if st.button("Gerar relatório"):
        df = pd.DataFrame(st.session_state.cirurgias)

        st.subheader("📄 Relatório final (copiar e colar no Word ou WhatsApp)")

        relatorio = f"Relatório de plantões do Dr. {nome_medico}\n\n"

        total_geral = 0
        for local in df["local"].unique():
            relatorio += f"Local: {local}\n"
            df_local = df[df["local"] == local]
            for _, row in df_local.iterrows():
                valor_total = row["horas"] * row["valor_hora"]
                relatorio += (
                    f"- {row['data']} ({row['horario']}) — {row['horas']}h "
                    f"x R$ {row['valor_hora']:.2f}/h = R$ {valor_total:.2f}\n"
                )
            subtotal = (df_local["horas"] * df_local["valor_hora"]).sum()
            relatorio += f"Subtotal {local}: R$ {subtotal:.2f}\n\n"
            total_geral += subtotal

        relatorio += f"Total geral: R$ {total_geral:.2f}"

        st.text_area("Copie abaixo:", relatorio, height=400)
