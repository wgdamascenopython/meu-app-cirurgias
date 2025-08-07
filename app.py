import streamlit as st
import pandas as pd

st.title("Registro de Cirurgias")

# Inicializar dados na sessão
if "registros" not in st.session_state:
    st.session_state.registros = []

# Entrada de dados fixos (uma vez só)
with st.expander("Configurações iniciais (preencher uma vez)"):
    nome = st.text_input("Nome do cirurgião")
    hospital = st.text_input("Hospital")
    valor_hora = st.number_input("Valor da hora de trabalho (R$)", step=10.0, format="%.2f")
    produtividade = st.number_input("Produtividade do mês (em R$)", step=100.0, format="%.2f")

# Entrada de plantões
st.subheader("Registrar plantão")
data = st.date_input("Data do plantão")
horas = st.number_input("Horas trabalhadas", min_value=0.0, step=0.5)

if st.button("Adicionar plantão"):
    st.session_state.registros.append({
        "Data": data.strftime("%d/%m/%Y"),
        "Horas": horas
    })

# Mostrar tabela de plantões
if st.session_state.registros:
    st.subheader("Resumo dos plantões")
    df = pd.DataFrame(st.session_state.registros)
    df["Valor recebido"] = df["Horas"] * valor_hora
    st.dataframe(df)

    total_horas = df["Horas"].sum()
    total_valor = df["Valor recebido"].sum()

    st.markdown(f"**Total de horas:** {total_horas} h")
    st.markdown(f"**Total recebido com plantões:** R$ {total_valor:.2f}")
    st.markdown(f"**Produtividade mensal:** R$ {produtividade:.2f}")
    st.markdown(f"**Total geral:** R$ {total_valor + produtividade:.2f}")
Corrigindo erro de digitação 
