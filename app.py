# app.py
import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime

# -----------------------
# Configurações da página
# -----------------------
st.set_page_config(page_title="Registro de Plantões Cirúrgicos", layout="centered")

st.markdown(
    "<h1 style='display:flex;gap:12px;align-items:center;'>"
    "<span>Registro de Plantões Cirúrgicos</span>"
    "</h1>",
    unsafe_allow_html=True,
)

# -----------------------
# Estado da aplicação
# -----------------------
if "registros" not in st.session_state:
    # cada registro: {data: date, setor: str, horario: str, horas: float}
    st.session_state.registros = []

if "nome_medico" not in st.session_state:
    st.session_state.nome_medico = ""

if "valor_hora" not in st.session_state:
    st.session_state.valor_hora = 160.0

if "produtividade" not in st.session_state:
    st.session_state.produtividade = 0.0

# -----------------------
# Utilitários
# -----------------------
HORARIOS = {
    "07h - 19h": 12.0,
    "19h - 07h": 12.0,
    "07h - 13h": 6.0,
    "13h - 19h": 6.0,
}

SETORES = ["Ambulatório", "Diarismo", "Centro"]

RECORRENCIA = {
    "Plantão isolado": 0,
    "Semanal": 7,
    "Quinzenal": 14,
}

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

def fim_do_mes(d: date) -> date:
    """Devolve o último dia do mês da data d."""
    primeiro_prox_mes = date(d.year + (1 if d.month == 12 else 0),
                             1 if d.month == 12 else d.month + 1,
                             1)
    return primeiro_prox_mes - timedelta(days=1)

def adicionar_registro(d: date, setor: str, horario: str):
    st.session_state.registros.append(
        {"data": d, "setor": setor, "horario": horario, "horas": HORARIOS[horario]}
    )

def excluir_registro(index: int):
    if 0 <= index < len(st.session_state.registros):
        st.session_state.registros.pop(index)

def formatar_data(d: date) -> str:
    return d.strftime("%d/%m/%Y")

def ordenar_registros():
    st.session_state.registros.sort(key=lambda r: (r["data"], r["setor"], r["horario"]))

# -----------------------
# Configurações fixas (uma vez por mês)
# -----------------------
with st.expander("Configurações do mês (preencher uma vez)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.nome_medico = st.text_input(
            "Nome do cirurgião", value=st.session_state.nome_medico
        )
    with col2:
        st.session_state.valor_hora = st.number_input(
            "Valor da hora (R$)", min_value=0.0, step=10.0, value=float(st.session_state.valor_hora), format="%.2f"
        )

    st.session_state.produtividade = st.number_input(
        "Produtividade mensal (R$) — valor único para o mês",
        min_value=0.0, step=50.0, value=float(st.session_state.produtividade), format="%.2f",
        help="Esse valor é somado apenas uma vez no fechamento."
    )

# -----------------------
# Entrada de plantões
# -----------------------
st.subheader("Novo plantão")

c1, c2 = st.columns(2)
with c1:
    data_plantao = st.date_input("Data", value=date.today())
    setor = st.selectbox("Local", SETORES, index=2)  # Centro como padrão
with c2:
    horario = st.selectbox("Horário", list(HORARIOS.keys()), index=0)
    recorrencia = st.selectbox("Recorrência", list(RECORRENCIA.keys()), index=0)

# Ao escolher o horário, horas são definidas automaticamente (campo só informativo)
st.text_input("Horas (auto)", value=f"{HORARIOS[horario]:.0f}h", disabled=True)

colA, colB = st.columns([1, 1])
with colA:
    if st.button("Adicionar plantão"):
        # adiciona o selecionado
        adicionar_registro(data_plantao, setor, horario)

        # adiciona recorrência no mesmo mês, caso necessário
        passo = RECORRENCIA[recorrencia]
        if passo > 0:
            d = data_plantao + timedelta(days=passo)
            limite = fim_do_mes(data_plantao)
            while d <= limite:
                adicionar_registro(d, setor, horario)
                d += timedelta(days=passo)

        ordenar_registros()
        st.success("Plantão(s) registrado(s) com sucesso.")

with colB:
    if st.button("Limpar todos os plantões"):
        st.session_state.registros = []
        st.info("Lista de plantões limpa.")

# -----------------------
# Exibição e exclusão
# -----------------------
st.subheader("Plantões registrados")

if st.session_state.registros:
    # tabela "manual" com botão excluir
    header = st.columns([2, 2, 2, 1, 1])
    header[0].markdown("**Data**")
    header[1].markdown("**Local**")
    header[2].markdown("**Horário**")
    header[3].markdown("**Horas**")
    header[4].markdown("**Ação**")

    for i, reg in enumerate(st.session_state.registros):
        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1, 1])
        c1.write(formatar_data(reg["data"]))
        c2.write(reg["setor"])
        c3.write(reg["horario"])
        c4.write(f'{int(reg["horas"])}h')
        if c5.button("Excluir", key=f"del_{i}"):
            excluir_registro(i)
            st.experimental_rerun()

else:
    st.info("Nenhum plantão registrado.")

# -----------------------
# Relatório final (visual)
# -----------------------
st.markdown("---")
st.subheader("Relatório final (copiar e colar)")

if not st.session_state.registros:
    st.info("Inclua ao menos um plantão para visualizar o relatório.")
else:
    # Determina mês/ano com base no primeiro registro (todos do mês corrente que você está lançando)
    ordenar_registros()
    primeiro = st.session_state.registros[0]["data"]
    mes_nome = MESES_PT[primeiro.month]
    ano = primeiro.year
    nome = st.session_state.nome_medico.strip() or "Médico"

    # Agrupa por setor
    df = pd.DataFrame(st.session_state.registros)
    # garante ordenação
    df = df.sort_values(by=["setor", "data", "horario"]).reset_index(drop=True)

    st.markdown(f"**{mes_nome}**")
    st.markdown(f"**Serviços HOE - {nome} - {mes_nome}/{ano}:**")
    st.write("")

    total_horas_geral = 0.0
    total_valor_geral = 0.0
    valor_hora = float(st.session_state.valor_hora)

    for setor in SETORES:
        df_setor = df[df["setor"] == setor].copy()
        if df_setor.empty:
            continue

        st.markdown(f"*{setor}*")
        horas_setor = 0.0

        linhas = []
        for _, r in df_setor.iterrows():
            linhas.append(f"{formatar_data(r['data'])} ({r['horario']}) - {int(r['horas'])}h")
            horas_setor += float(r["horas"])

        # lista de linhas
        st.markdown("\n".join(linhas))
        st.write("")
        st.markdown(f"Total: {int(horas_setor)} horas")
        st.markdown(f"Valor: {int(horas_setor)} X {int(valor_hora)} = {int(horas_setor) * valor_hora:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))  # formatação PT-BR simples

        st.write("")
        total_horas_geral += horas_setor
        total_valor_geral += horas_setor * valor_hora

    st.markdown(f"**Valor total:** {total_valor_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown(f"**Produtividade**\n{mes_nome}: {st.session_state.produtividade:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    valor_final = total_valor_geral + float(st.session_state.produtividade)
    st.markdown(f"**Valor final:** {valor_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
