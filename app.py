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
if st.button("Registrar plantão"):
    st.session_state.registros.append({"Data": data, "Horas": horas})
    st.success("Plantão registrado com sucesso!")

# Exibir registros
if st.session_state.registros:
    st.subheader("Registros do mês")
    df = pd.DataFrame(st.session_state.registros)
    df["Valor (R$)"] = df["Horas"] * valor_hora
    st.dataframe(df)

    total_valor = df["Valor (R$)"].sum()
    st.markdown(f"**Total do mês (sem produtividade):** R$ {total_valor:.2f}")
    st.markdown(f"**Produtividade:** R$ {produtividade:.2f}")
    st.markdown(f"**Total geral:** R$ {total_valor + produtividade:.2f}")
