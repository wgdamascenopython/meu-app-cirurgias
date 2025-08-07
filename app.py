import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar

st.set_page_config(page_title="Registro de Plantões", layout="centered")
st.title("Registro de Plantões")

# -----------------------------
# Estado de sessão
# -----------------------------
if "registros" not in st.session_state:
    st.session_state.registros = []     # cada item: {data: date, local: str, horario: str, horas: int}
if "produtividade" not in st.session_state:
    st.session_state.produtividade = 0.0

# -----------------------------
# Configurações fixas (uma vez)
# -----------------------------
with st.expander("Configurações do relatório (preencher uma vez)", expanded=True):
    nome_medico = st.text_input("Nome do médico", value="")
    mes_ano_str = st.text_input("Mês/Ano do relatório (ex.: Julho/2025)", value="")
    valor_hora = st.number_input("Valor da hora (R$)", min_value=0.0, value=160.0, step=10.0, format="%.2f")
    produtividade = st.number_input("Produtividade mensal (R$)", min_value=0.0, value=float(st.session_state.produtividade), step=100.0, format="%.2f")
    st.session_state.produtividade = produtividade

st.markdown("---")

# -----------------------------
# Formulário de novo plantão
# -----------------------------
st.subheader("Adicionar plantão")

col1, col2, col3 = st.columns(3)
with col1:
    data_base = st.date_input("Data", value=date.today())
with col2:
    local = st.selectbox("Local", ["Ambulatório", "Centro", "Diarismo"])
with col3:
    horario = st.selectbox(
        "Horário",
        ["07h - 13h", "13h - 19h", "07h - 19h", "19h - 07h"]
    )

# horas calculadas automaticamente a partir do horário
horas_por_horario = {
    "07h - 13h": 6,
    "13h - 19h": 6,
    "07h - 19h": 12,
    "19h - 07h": 12,
}
horas_calc = horas_por_horario[horario]
st.caption(f"Horas calculadas: {horas_calc}h")

recorrencia = st.radio(
    "Recorrência no mês",
    ["Isolado (somente esta data)", "Semanal (mesmo dia da semana no mês)", "Quinzenal (a cada 14 dias no mês)"],
    index=0
)

def datas_recorrentes_no_mes(d0: date, modo: str):
    """Retorna as datas no mesmo mês de d0, conforme recorrência."""
    datas = []
    year, month = d0.year, d0.month
    # limite final: último dia do mês
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    step = 0
    if modo.startswith("Semanal"):   # a cada 7 dias
        step = 7
    elif modo.startswith("Quinzenal"):  # a cada 14 dias
        step = 14
    else:  # Isolado
        return [d0]

    current = d0
    while current <= end_date and current.month == month:
        datas.append(current)
        current = current + timedelta(days=step)

    return datas

if st.button("Adicionar"):
    datas_para_inserir = datas_recorrentes_no_mes(data_base, recorrencia)
    # cria registros e anexa
    for d in datas_para_inserir:
        st.session_state.registros.append({
            "data": d,
            "local": local,
            "horario": horario,
            "horas": horas_calc
        })
    st.success(f"{len(datas_para_inserir)} plantão(ões) adicionado(s).")

st.markdown("---")

# -----------------------------
# Lista com opção de excluir
# -----------------------------
st.subheader("Plantões registrados")
if st.session_state.registros:
    # ordenar por data
    st.session_state.registros.sort(key=lambda r: r["data"])
    for i, r in enumerate(st.session_state.registros):
        c1, c2, c3, c4, c5 = st.columns([1.2, 1.1, 1.2, 4, 1])
        c1.write(r["data"].strftime("%d/%m/%Y"))
        c2.write(r["local"])
        c3.write(r["horario"])
        c4.write(f"{int(r['horas'])}h")
        if c5.button("Excluir", key=f"del_{i}"):
            st.session_state.registros.pop(i)
            st.rerun()
else:
    st.info("Nenhum plantão registrado até o momento.")

# -----------------------------
# Relatório final (estilo Aislan)
# -----------------------------
if st.session_state.registros:
    st.markdown("---")
    st.subheader("Relatório final (copiar e colar)")

    df = pd.DataFrame(st.session_state.registros)
    # ordena por data
    df = df.sort_values(by="data")

    # agrupamento em ordem específica
    ordem_setores = ["Diarismo", "Ambulatório", "Centro"]

    # cabeçalho
    cabecalho_linhas = []
    if mes_ano_str.strip():
        cabecalho_linhas.append(mes_ano_str.strip().split("/")[0])  # só o mês (ex.: Julho)
    titulo = f"Serviços HOE {nome_medico} {mes_ao_ano := (mes_ano_str.strip() if mes_ano_str.strip() else '')}:"
    cabecalho_linhas.append(titulo)

    # monta corpo
    linhas = []
    for setor in ordem_setores:
        bloco = df[df["local"] == setor]
        if bloco.empty:
            continue
        # título do setor
        if setor == "Diarismo":
            linhas.append("*Diarismo* Ortopedia:")
        else:
            linhas.append(f"*{setor}*")
        # linhas do setor
        total_horas_setor = int(bloco["horas"].sum())
        valor_setor = total_horas_setor * float(valor_hora)
        for _, row in bloco.iterrows():
            linhas.append(f"{row['data'].strftime('%d/%m/%Y')} ({row['horario']}) - {int(row['horas']):02d}h")
        linhas.append(f"\nTotal: {total_horas_setor} horas")
        linhas.append(f"Valor: {total_horas_setor} X {int(valor_hora)} = {valor_setor:,.2f}\n")

    # totais
    total_horas_geral = int(df["horas"].sum())
    total_valor_geral = total_horas_geral * float(valor_hora)
    linhas.append(f"Valor total: {total_valor_geral:,.2f}\n")
    linhas.append("Produtividade")
    if mes_ao_ano:
        linhas.append(f"{mes_ao_ano}: {float(st.session_state.produtividade):,.2f}\n")
    else:
        linhas.append(f"{float(st.session_state.produtividade):,.2f}\n")
    linhas.append(f"Valor final: {total_valor_geral + float(st.session_state.produtividade):,.2f}")

    # junta tudo
    relatorio_texto = ""
    if cabecalho_linhas:
        relatorio_texto += "\n".join(cabecalho_linhas) + "\n\n"
    relatorio_texto += "\n".join(linhas)

    st.text_area("Relatório:", value=relatorio_texto, height=420)
