import streamlit as st
import pandas as pd
from docx import Document
from io import BytesIO

st.set_page_config(page_title="Registro de Cirurgias", layout="centered")

# Inicializar estado da sessão
if "registros" not in st.session_state:
    st.session_state.registros = []
if "config" not in st.session_state:
    st.session_state.config = {}

st.title("🩺 Registro de Cirurgias")

# Configurações iniciais
with st.expander("⚙️ Configurações iniciais (preencher apenas uma vez)", expanded=True):
    nome = st.text_input("Nome do cirurgião", key="nome")
    hospital = st.text_input("Hospital", key="hospital")
    valor_hora = st.number_input("Valor da hora trabalhada (R$)", step=10.0, key="valor_hora")
    produtividade = st.number_input("Valor da produtividade mensal (R$)", step=10.0, key="produtividade")
    if nome and hospital and valor_hora > 0:
        st.session_state.config = {
            "nome": nome,
            "hospital": hospital,
            "valor_hora": valor_hora,
            "produtividade": produtividade,
        }

# Entrada de novo plantão
st.subheader("➕ Novo Plantão")

col1, col2 = st.columns(2)
with col1:
    data = st.date_input("Data do plantão")
with col2:
    local = st.selectbox("Local", ["Ambulatório", "Centro Cirúrgico", "Diarismo"])

horario = st.selectbox("Horário do plantão", [
    "07:00 - 13:00", "13:00 - 19:00", "07:00 - 19:00", "19:00 - 07:00"
])
horas = st.number_input("Quantidade de horas trabalhadas", step=1.0)

if st.button("Registrar plantão"):
    if st.session_state.config == {}:
        st.error("Preencha as configurações iniciais primeiro.")
    else:
        st.session_state.registros.append({
            "Data": str(data),
            "Local": local,
            "Horário": horario,
            "Horas": horas,
            "Valor (R$)": horas * st.session_state.config["valor_hora"]
        })
        st.success("Plantão registrado com sucesso!")

# Exibir registros
st.subheader("📋 Registros do mês")

if st.session_state.registros:
    for i, r in enumerate(st.session_state.registros):
        st.markdown(
            f"**{r['Data']}** ({r['Horário']}) - {r['Horas']}h | Local: {r['Local']} | R$ {r['Valor (R$)']:.2f} "
        )
        if st.button(f"🗑️ Excluir", key=f"del_{i}"):
            st.session_state.registros.pop(i)
            st.experimental_rerun()

    df = pd.DataFrame(st.session_state.registros)
    total_valor = df["Valor (R$)"].sum()
    produtividade = st.session_state.config.get("produtividade", 0.0)
    total_geral = total_valor + produtividade

    st.markdown(f"**💰 Total do mês (sem produtividade):** R$ {total_valor:.2f}")
    st.markdown(f"**💼 Produtividade:** R$ {produtividade:.2f}")
    st.markdown(f"**✅ Total geral:** R$ {total_geral:.2f}")

    # Gerar relatório
    if st.button("📄 Gerar relatório Word"):
        doc = Document()
        doc.add_heading(f"Relatório de Cirurgias - {st.session_state.config['nome']}", level=1)
        doc.add_paragraph(f"Hospital: {st.session_state.config['hospital']}")
        doc.add_paragraph("")

        agrupado = df.groupby("Local")

        for local, grupo in agrupado:
            doc.add_heading(f"{local}", level=2)
            for _, row in grupo.iterrows():
                doc.add_paragraph(
                    f"{row['Data']} ({row['Horário']}) - {int(row['Horas'])}h"
                )
            total_horas = grupo["Horas"].sum()
            total_valor_local = grupo["Valor (R$)"].sum()
            doc.add_paragraph(f"Total: {int(total_horas)} horas")
            doc.add_paragraph(
                f"Valor: {int(total_horas)} X R$ {st.session_state.config['valor_hora']:.2f} = R$ {total_valor_local:.2f}"
            )
            doc.add_paragraph("")

        doc.add_paragraph(f"Valor produtividade: R$ {produtividade:.2f}")
        doc.add_paragraph(f"Valor final: R$ {total_geral:.2f}")

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="📥 Baixar relatório Word",
            data=buffer,
            file_name="relatorio_plantao.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
else:
    st.info("Ainda não há plantões registrados.")
