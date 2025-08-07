import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Registro de Plantões Cirúrgicos", layout="centered")

# Inicializa storage
if "plantao_data" not in st.session_state:
    st.session_state.plantao_data = []
if "produtividade_mensal" not in st.session_state:
    st.session_state.produtividade_mensal = 0.0

st.title("📋 Registro de Plantões Cirúrgicos")

# Formulário
col1, col2 = st.columns(2)
with col1:
    data = st.date_input("Data", datetime.today())
    local = st.selectbox("Local", ["Ambulatório", "Centro Cirúrgico", "Diarismo"])
    horario = st.selectbox("Horário", ["07h - 13h", "13h - 19h", "07h - 19h", "19h - 07h"])
with col2:
    valor_hora = st.number_input("Valor da hora (R$)", min_value=0.0, step=10.0)
    produtividade = st.number_input("Produtividade mensal (R$)", min_value=0.0, step=10.0)
    repeticao = st.selectbox("Repetição", ["Isolado", "Semanal", "Quinzenal"])

# Define horas automaticamente
horas_por_turno = {
    "07h - 13h": 6,
    "13h - 19h": 6,
    "07h - 19h": 12,
    "19h - 07h": 12
}
horas = horas_por_turno[horario]

if st.button("Adicionar plantão"):
    if produtividade > 0:
        st.session_state.produtividade_mensal = produtividade

    datas_adicionar = [data]
    if repeticao != "Isolado":
        intervalo = 7 if repeticao == "Semanal" else 14
        d = data + timedelta(days=intervalo)
        while d.month == data.month:
            datas_adicionar.append(d)
            d += timedelta(days=intervalo)

    for d in datas_adicionar:
        st.session_state.plantao_data.append({
            "Data": d,
            "Local": local,
            "Horário": horario,
            "Horas": horas,
            "Valor hora": valor_hora
        })

# Lista plantões
st.subheader("📌 Plantões registrados")
df = pd.DataFrame(st.session_state.plantao_data)
if not df.empty:
    for i, row in df.iterrows():
        col1, col2 = st.columns([4,1])
        col1.write(f"{row['Data'].strftime('%d/%m/%Y')} - {row['Local']} - {row['Horário']} - {row['Horas']}h")
        if col2.button("Excluir", key=f"excluir_{i}"):
            st.session_state.plantao_data.pop(i)
            st.experimental_rerun()

# Relatório final
if not df.empty:
    st.subheader("Relatório final (copiar e colar)")

    mes_ano = data.strftime("%B/%Y").capitalize()
    nome_medico = "Washington Guimarães Damasceno"  # Pode mudar se quiser dinamizar

    st.markdown(f"**{mes_ano}**")
    st.markdown(f"Serviços HOE - {nome_medico} - {mes_ano}:")

    for setor in df["Local"].unique():
        st.markdown(f"**{setor}**")
        linhas = []
        for _, r in df[df["Local"] == setor].sort_values("Data").iterrows():
            linhas.append(f"{r['Data'].strftime('%d/%m/%Y')} ({r['Horário']}) - {r['Horas']}h")
        st.markdown("<br>".join(linhas), unsafe_allow_html=True)

    total_horas = df["Horas"].sum()
    valor_plantao = (df["Horas"] * df["Valor hora"]).sum()
    produtividade_mes = st.session_state.produtividade_mensal
    valor_final = valor_plantao + produtividade_mes

    st.write(f"Total: {total_horas} horas")
    st.write(f"Valor pelos plantões: R$ {valor_plantao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.write(f"Produtividade {mes_ano.split('/')[0]}: R$ {produtividade_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.write(f"Valor final: R$ {valor_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
