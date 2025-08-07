import streamlit as st
import pandas as pd

st.title("Registro de Cirurgias")

# Inicializar dados na sessão
if "registros" not in st.session_state:
    st.session_state.registros = []

# Entrada de dados fixos (uma vez só)
with st.expander("Configurações iniciais (preencher apenas uma vez)"):
    nome = st.text_input("Nome do cirurgião", key="nome")
    hospital = st.text_input("Hospital", key="hospital")
    valor_hora = st.number_input("Valor da hora trabalhada (R$)", key="valor_hora")
    produtividade = st.number_input("Valor da produtividade mensal (R$)", key="produtividade")

# Entrada de dados por plantão
st.subheader("Novo Plantão")
data = st.date_input("Data do plantão")
horas = st.number_input("Quantidade de horas trabalhadas")
horario = st.selectbox(
    "Horário do plantão",
    ["07:00 - 13:00", "13:00 - 19:00", "07:00 - 19:00", "19:00 - 07:00"]
)
local = st.selectbox("Local de trabalho", ["Ambulatório", "Centro Cirúrgico", "Diarismo"])

if st.button("Registrar plantão"):
    st.session_state.registros.append({
        "Data": data,
        "Horário": horario,
        "Horas": horas,
        "Local": local
    })
    st.success("Plantão registrado com sucesso!")

# Exibir registros
if st.session_state.registros:
    st.subheader("Relatório final do mês")
    df = pd.DataFrame(st.session_state.registros)
    df["Valor (R$)"] = df["Horas"] * valor_hora

    total_geral = 0
    for local_trabalho in df["Local"].unique():
        st.markdown(f"### {local_trabalho}")
        df_local = df[df["Local"] == local_trabalho]
        total_local = df_local["Horas"].sum()
        valor_local = df_local["Valor (R$)"].sum()
        for _, row in df_local.iterrows():
            data_str = row["Data"].strftime("%d/%m/%Y")
            st.markdown(f"{data_str} ({row['Horário']}) - {int(row['Horas'])}h")
        st.markdown(f"**Total: {int(total_local)} horas**")
        st.markdown(f"**Valor: {int(total_local)} X R$ {valor_hora:.2f} = R$ {valor_local:,.2f}**")
        total_geral += valor_local

    st.markdown("---")
    st.markdown(f"**Valor total (sem produtividade): R$ {total_geral:,.2f}**")
    st.markdown(f"**Produtividade: R$ {produtividade:,.2f}**")
    st.markdown(f"**Valor final: R$ {total_geral + produtividade:,.2f}**")
