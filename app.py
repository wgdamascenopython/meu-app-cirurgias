import streamlit as st
import pandas as pd
from docx import Document
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Registro de Plantões", layout="centered")

st.title("Registro de Plantões Médicos")

# Campos de entrada
nome = st.text_input("Nome do médico")
data = st.date_input("Data do plantão", format="DD/MM/YYYY")
local = st.selectbox("Local do plantão", ["Ambulatório", "Centro Cirúrgico", "Diarismo"])
horario = st.selectbox("Horário do plantão", ["7:00 - 19:00", "19:00 - 7:00", "7:00 - 13:00", "13:00 - 19:00"])

# Iniciar ou carregar lista da sessão
if "plantoes" not in st.session_state:
    st.session_state.plantoes = []

# Botão de adicionar plantão
if st.button("Adicionar plantão"):
    if nome.strip() == "":
        st.warning("Digite o nome do médico.")
    else:
        st.session_state.plantoes.append({
            "Data": data.strftime("%d/%m/%Y"),
            "Local": local,
            "Horário": horario,
            "Nome": nome.strip()
        })

# Mostrar plantões adicionados com opção de remover
if st.session_state.plantoes:
    st.subheader("Plantões Registrados")
    for i, plantao in enumerate(st.session_state.plantoes):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"📅 **{plantao['Data']}** | 🏥 {plantao['Local']} | ⏰ {plantao['Horário']} | 👨‍⚕️ {plantao['Nome']}")
        with col2:
            if st.button("❌", key=f"delete_{i}"):
                st.session_state.plantoes.pop(i)
                st.experimental_rerun()

# Função para gerar o DOCX
def gerar_relatorio(plantoes):
    doc = Document()

    doc.add_heading(f"Relatório de Plantões – {plantoes[0]['Nome']}", level=1)

    locais = ["Ambulatório", "Centro Cirúrgico", "Diarismo"]
    total_geral = 0

    for local in locais:
        doc.add_heading(f"{local}", level=2)
        total_horas = 0
        for p in plantoes:
            if p["Local"] == local:
                doc.add_paragraph(f"{p['Data']} - {p['Horário']} ({p['Nome']})")
                h_inicio, h_fim = p["Horário"].split(" - ")
                h_inicio = datetime.strptime(h_inicio, "%H:%M")
                h_fim = datetime.strptime(h_fim, "%H:%M")
                horas = (h_fim - h_inicio).seconds // 3600 if h_fim > h_inicio else ((h_fim + pd.Timedelta(days=1)) - h_inicio).seconds // 3600
                total_horas += horas
        doc.add_paragraph(f"Total de horas: {total_horas}h")
        total_geral += total_horas

    doc.add_paragraph(f"\nTotal geral de horas: {total_geral}h")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Botão para gerar relatório final
if st.session_state.plantoes:
    if st.button("📄 Gerar Relatório Word"):
        docx_file = gerar_relatorio(st.session_state.plantoes)
        st.download_button(
            label="📥 Baixar Relatório .docx",
            data=docx_file,
            file_name="relatorio_plantoes.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
