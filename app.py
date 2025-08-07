import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from docx import Document

st.title("Registro de Cirurgias")

# Inicializar registros
if "registros" not in st.session_state:
    st.session_state.registros = []

# Configuração fixa (preenchida uma vez)
with st.expander("Configurações iniciais (preencher uma vez)"):
    nome = st.text_input("Nome do cirurgião", key="nome")
    hospital = st.text_input("Hospital", key="hospital")
    valor_hora = st.number_input("Valor da hora trabalhada (R$)", key="valor_hora")
    produtividade = st.number_input("Valor da produtividade mensal (R$)", key="produtividade")

# Novo plantão
st.subheader("Novo Plantão")

data = st.date_input("Data do plantão")
horas = st.number_input("Quantidade de horas trabalhadas", min_value=1.0, step=0.5)
horario = st.selectbox("Horário do plantão", ["07:00 - 13:00", "13:00 - 19:00", "07:00 - 19:00", "19:00 - 07:00"])
local = st.selectbox("Local de trabalho", ["Ambulatório", "Centro Cirúrgico", "Diarismo"])

if st.button("Registrar plantão"):
    novo = {
        "Data": data,
        "Horário": horario,
        "Horas": horas,
        "Local": local,
        "Valor": horas * valor_hora
    }
    st.session_state.registros.append(novo)
    st.success("Plantão registrado com sucesso!")

# Exibir registros e permitir exclusão
if st.session_state.registros:
    st.subheader("Registros do mês")
    df = pd.DataFrame(st.session_state.registros)

    for i, row in df.iterrows():
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"{row['Data'].strftime('%d/%m/%Y')} ({row['Horário']}) - {row['Horas']}h | {row['Local']}")
        with col2:
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.registros.pop(i)
                st.experimental_rerun()

    total_horas = df["Horas"].sum()
    total_valor = df["Valor"].sum()
    st.markdown(f"**Total do mês (sem produtividade):** R$ {total_valor:.2f}")
    st.markdown(f"**Produtividade:** R$ {produtividade:.2f}")
    st.markdown(f"**Total geral:** R$ {total_valor + produtividade:.2f}")

    # Botão para gerar DOCX
    if st.button("📄 Gerar relatório em Word"):
        doc = Document()
        doc.add_heading(f"Serviços {hospital} {nome} - {data.strftime('%B/%Y')}", level=1)

        for local_trabalho in df["Local"].unique():
            doc.add_paragraph(f"\n*{local_trabalho}*", style="List Bullet")

            registros_local = df[df["Local"] == local_trabalho]
            for _, r in registros_local.iterrows():
                linha = f"{r['Data'].strftime('%d/%m/%Y')} ({r['Horário']}) - {int(r['Horas'])}h"
                doc.add_paragraph(linha, style="List Bullet 2")

            total_horas_local = registros_local["Horas"].sum()
            total_valor_local = registros_local["Valor"].sum()
            doc.add_paragraph(f"Total: {int(total_horas_local)} horas", style="Normal")
            doc.add_paragraph(f"Valor: {int(total_horas_local)} X {valor_hora:.0f} = {total_valor_local:.2f}", style="Normal")

        doc.add_paragraph(f"\nValor total: {total_valor:.2f}")
        doc.add_paragraph(f"Produtividade: {produtividade:.2f}")
        doc.add_paragraph(f"Valor final: {total_valor + produtividade:.2f}")

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="📥 Baixar Relatório Word",
            data=buffer,
            file_name=f"relatorio_{nome.lower().replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
else:
    st.info("Ainda não há plantões registrados.")
