import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Registro de Plantões Cirúrgicos", layout="centered")

# =========================
# Estado inicial da sessão
# =========================
if "plantao_data" not in st.session_state:
    st.session_state.plantao_data = []

if "produtividade_mensal" not in st.session_state:
    st.session_state.produtividade_mensal = 0.0

if "nome_medico" not in st.session_state:
    st.session_state.nome_medico = ""

if "hospital" not in st.session_state:
    st.session_state.hospital = ""

# =========================
# Utilidades
# =========================
HORAS_TURNO = {
    "07h - 13h": 6,
    "13h - 19h": 6,
    "07h - 19h": 12,
    "19h - 07h": 12,
}

def brl(v: float) -> str:
    s = f"{v:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def mes_ano_pt(dt: datetime) -> str:
    # Julho/2025 etc.
    return dt.strftime("%B/%Y").capitalize()

# =========================
# Cabeçalho
# =========================
st.title("📋 Registro de Plantões Cirúrgicos")

# -------------------------
# Identificação (fixos)
# -------------------------
st.subheader("Identificação")
c1, c2 = st.columns(2)
with c1:
    st.session_state.nome_medico = st.text_input(
        "Nome do cirurgião",
        value=st.session_state.nome_medico,
        placeholder="Ex.: Washington Guimarães Damasceno",
    )
with c2:
    st.session_state.hospital = st.text_input(
        "Hospital",
        value=st.session_state.hospital,
        placeholder="Ex.: Hospital Ortopédico da Bahia",
    )

# -------------------------
# Formulário de plantão
# -------------------------
st.subheader("Novo plantão")

col1, col2 = st.columns(2)
with col1:
    data = st.date_input("Data", datetime.today())
    local = st.selectbox("Local", ["Ambulatório", "Centro Cirúrgico", "Diarismo"])
    horario = st.selectbox("Horário", ["07h - 13h", "13h - 19h", "07h - 19h", "19h - 07h"])

with col2:
    valor_hora = st.number_input("Valor da hora (R$)", min_value=0.0, step=10.0, value=st.session_state.get("valor_hora_padrao", 0.0))
    produtividade_input = st.number_input("Produtividade mensal (R$)", min_value=0.0, step=10.0, value=float(st.session_state.produtividade_mensal))
    repeticao = st.selectbox("Repetição", ["Isolado", "Semanal", "Quinzenal"])

# Horas automáticas pelo horário
horas = HORAS_TURNO[horario]

# Botão adicionar
if st.button("Adicionar plantão", use_container_width=False):
    # Atualiza produtividade (única por mês)
    if produtividade_input != st.session_state.produtividade_mensal:
        st.session_state.produtividade_mensal = produtividade_input

    # Guarda valor da hora como padrão para os próximos
    st.session_state.valor_hora_padrao = valor_hora

    # Calcula datas a inserir (isolado/semanal/quinzenal no MESMO mês)
    datas_adicionar = [data]
    if repeticao != "Isolado":
        passo = 7 if repeticao == "Semanal" else 14
        d = data + timedelta(days=passo)
        while d.month == data.month and d.year == data.year:
            datas_adicionar.append(d)
            d += timedelta(days=passo)

    for d in datas_adicionar:
        st.session_state.plantao_data.append(
            {
                "Data": d,
                "Local": local,
                "Horário": horario,
                "Horas": horas,
                "Valor hora": valor_hora,
            }
        )

# =========================
# Lista de plantões
# =========================
st.subheader("📌 Plantões registrados")

df = pd.DataFrame(st.session_state.plantao_data)
if df.empty:
    st.info("Nenhum plantão registrado.")
else:
    # Ordena por data
    df = df.sort_values("Data").reset_index(drop=True)

    # Tabela simples + botões para excluir
    for idx, row in df.iterrows():
        c1, c2 = st.columns([5, 1])
        with c1:
            st.write(
                f"{row['Data'].strftime('%d/%m/%Y')}  •  {row['Local']}  •  {row['Horário']}  •  {row['Horas']}h"
            )
        with c2:
            if st.button("Excluir", key=f"excluir_{idx}"):
                st.session_state.plantao_data.pop(idx)
                st.experimental_rerun()

# =========================
# Relatório final
# =========================
if not df.empty:
    st.markdown("---")
    st.subheader("Relatório final (copiar e colar)")

    # Mês/ano do relatório a partir da primeira data
    base_date = df.iloc[0]["Data"]
    titulo_mes_ano = mes_ano_pt(base_date)

    nome = st.session_state.nome_medico.strip() or "Nome do Médico"
    hosp = st.session_state.hospital.strip() or "Hospital"

    # Cabeçalho
    st.markdown(f"**{titulo_mes_ano.split('/')[0]}**")
    st.markdown(f"Serviços HOE - {nome} - {titulo_mes_ano}:")
    st.markdown(f"*Hospital:* {hosp}")
    st.write("")

    total_horas_mes = 0
    valor_plantao_mes = 0.0

    # Por setor (local)
    for setor in ["Diarismo", "Ambulatório", "Centro Cirúrgico"]:
        bloco = df[df["Local"] == setor].sort_values("Data")
        if bloco.empty:
            continue

        st.markdown(f"**{setor}**\n")
        # Uma linha por plantão
        linhas = []
        horas_setor = 0
        valor_setor = 0.0
        for _, r in bloco.iterrows():
            linhas.append(f"{r['Data'].strftime('%d/%m/%Y')} ({r['Horário']}) - {r['Horas']}h")
            horas_setor += r["Horas"]
            valor_setor += r["Horas"] * r["Valor hora"]

        # Renderiza cada linha separada
        for linha in linhas:
            st.markdown(linha)

        st.write("")
        st.write(f"Total: {horas_setor} horas")
        st.write(f"Valor: {horas_setor} X {brl(bloco.iloc[0]['Valor hora'])} = {brl(valor_setor)}")
        st.write("")

        total_horas_mes += horas_setor
        valor_plantao_mes += valor_setor

    # Rodapé
    st.write(f"Valor total: {brl(valor_plantao_mes)}")
    st.write(f"Produtividade {titulo_mes_ano.split('/')[0]}: {brl(st.session_state.produtividade_mensal)}")
    st.write(f"Valor final: {brl(valor_plantao_mes + st.session_state.produtividade_mensal)}")
