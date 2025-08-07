import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime

st.set_page_config(page_title="Registro de Plantões Cirúrgicos", layout="wide")

# --------- Utilidades ---------
HORARIOS = {
    "07h - 19h": 12,
    "19h - 07h": 12,
    "07h - 13h": 6,
    "13h - 19h": 6,
}

SETORES = ["Ambulatório", "Diarismo", "Centro"]

def mes_nome_pt(m):
    nomes = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
             "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    return nomes[m-1]

def fmt_data_pt(d: date) -> str:
    return d.strftime("%d/%m/%Y")

def brl(v: float) -> str:
    s = f"{v:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_datas_recorrentes(data_inicial: date, modo: str):
    """Retorna as datas dentro do mesmo mês para Semanal/Quinzenal."""
    datas = [data_inicial]
    if modo == "Isolado":
        return datas
    passo = 7 if modo == "Semanal" else 14  # Quinzenal
    d = data_inicial + timedelta(days=passo)
    while d.month == data_inicial.month and d.year == data_inicial.year:
        datas.append(d)
        d = d + timedelta(days=passo)
    return datas

def cabecalho_relatorio(nome_medico: str, mes_ano_str: str, registros: list[dict]) -> list[str]:
    linhas = []
    mes_ao_ano = mes_ano_str.strip() if mes_ano_str else ""
    # se não foi informado, tenta inferir do primeiro registro
    if not mes_ao_ano and registros:
        d0 = registros[0]["data"]
        mes_ao_ano = f"{mes_nome_pt(d0.month)}/{d0.year}"
    # primeira linha: apenas mês (ex.: Julho)
    if mes_ao_ano:
        if "/" in mes_ao_ano:
            linhas.append(mes_ao_ano.split("/")[0])
        else:
            linhas.append(mes_ao_ano)
    titulo = f"Serviços HOE - {nome_medico} - {mes_ao_ano}"
    linhas.append("")
    linhas.append(titulo + ":")
    return linhas

def montar_bloco_setor(setor: str, regs: list[dict], valor_hora: float) -> tuple[list[str], int, float]:
    """Retorna (linhas, horas_total, valor_total) para um setor."""
    if not regs:
        return [], 0, 0.0
    linhas = [f"*{setor}*"]
    total_horas = 0
    for r in regs:
        linhas.append(f"{fmt_data_pt(r['data'])} ({r['horario']}) - {r['horas']:02d}h")
        total_horas += r["horas"]
    valor = total_horas * valor_hora
    linhas.append("")
    linhas.append(f"Total: {total_horas} horas")
    linhas.append(f"Valor: {total_horas} X {int(valor_hora)} = {brl(valor)}")
    linhas.append("")
    return linhas, total_horas, valor

# --------- Estado ---------
if "registros" not in st.session_state:
    st.session_state.registros = []  # cada item: {"data", "setor", "horario", "horas"}
if "nome" not in st.session_state:
    st.session_state.nome = ""
if "valor_hora" not in st.session_state:
    st.session_state.valor_hora = 160.0
if "produtividade" not in st.session_state:
    st.session_state.produtividade = 0.0
if "mes_ano" not in st.session_state:
    st.session_state.mes_ano = ""  # ex.: "Julho/2025"

# --------- Cabeçalho ---------
st.title("Registro de Plantões Cirúrgicos")

# --------- Painel de Configurações (preencher 1x por mês) ---------
with st.expander("Configurações do mês (preencher uma vez)"):
    colA, colB, colC = st.columns([1,1,1])
    with colA
