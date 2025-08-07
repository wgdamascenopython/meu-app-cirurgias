import streamlit as st import pandas as pd from datetime import datetime

st.set_page_config(page_title="Registro de Plantões Cirúrgicos", layout="centered")

st.title("🗂️ Registro de Plantões Cirúrgicos")

Inicializa sessão para armazenar dados

if "plantao_data" not in st.session_state: st.session_state.plantao_data = []

if "produtividade_mensal" not in st.session_state: st.session_state.produtividade_mensal = 0.0

st.subheader("Preencha os dados do plantão") data = st.date_input("Data", format="YYYY/MM/DD") local = st.selectbox("Local", ["Ambulatório", "Centro Cirúrgico", "Diarista"])

horario_opcoes = { "07h - 13h": 6, "07h - 19h": 12, "13h - 19h": 6, "19h - 07h": 12 }

horario_selecionado = st.selectbox("Horário", list(horario_opcoes.keys())) horas_trabalhadas = horario_opcoes[horario_selecionado]

valor_hora = st.number_input("Valor da hora (R$)", min_value=0.0, step=10.0, value=160.0)

Campo separado para produtividade mensal

st.markdown("---") produtividade_mensal = st.number_input("Produtividade mensal (R$)", min_value=0.0, step=100.0, value=st.session_state.produtividade_mensal) st.session_state.produtividade_mensal = produtividade_mensal st.markdown("---")

if st.button("Adicionar plantão"): novo_plantao = { "data": data.strftime("%d/%m/%Y"), "local": local, "horario": horario_selecionado, "horas": horas_trabalhadas, "valor_hora": valor_hora, "valor_total": horas_trabalhadas * valor_hora } st.session_state.plantao_data.append(novo_plantao) st.success("Plantão adicionado com sucesso!")

Agrupa e mostra os plantões

if st.session_state.plantao_data: st.subheader("📌 Plantões registrados") df = pd.DataFrame(st.session_state.plantao_data) locais = df["local"].unique() total_geral = 0 total_horas = 0

for loc in locais:
    st.markdown(f"<b>{loc}</b>", unsafe_allow_html=True)
    df_loc = df[df["local"] == loc]
    for _, row in df_loc.iterrows():
        st.write(f"- {row['data']} - {row['horario']} - {row['horas']}h")
    total_loc = df_loc["valor_total"].sum()
    horas_loc = df_loc["horas"].sum()
    st.write(f"Total: {horas_loc} horas = R$ {total_loc:,.2f}")
    total_geral += total_loc
    total_horas += horas_loc

st.markdown("---")
st.subheader("📄 Resumo final:")
st.write(f"Total de horas trabalhadas: {total_horas}h")
st.write(f"Valor pelos plantões: R$ {total_geral:,.2f}")
st.write(f"Produtividade mensal: R$ {st.session_state.produtividade_mensal:,.2f}")
st.write(f"Total geral: R$ {(total_geral + st.session_state.produtividade_mensal):,.2f}")

