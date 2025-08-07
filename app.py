import streamlit as st import pandas as pd from io import StringIO from datetime import datetime

st.set_page_config(page_title="Registro de Cirurgias", layout="centered") st.title("Registro de Cirurgias")

Inicializar dados na sessão

if "registros" not in st.session_state: st.session_state.registros = []

Entrada de dados fixos (uma vez só)

with st.expander("Configurações iniciais (preencher apenas uma vez)"): nome = st.text_input("Nome do cirurgião", key="nome") hospital = st.text_input("Hospital", key="hospital") valor_hora = st.number_input("Valor da hora trabalhada (R$)", key="valor_hora") produtividade = st.number_input("Valor da produtividade mensal (R$)", key="produtividade")

Entrada de dados por plantão

st.subheader("Novo Plantão") data = st.date_input("Data do plantão") horario = st.selectbox("Horário do plantão", [ "07:00 - 13:00", "13:00 - 19:00", "07:00 - 19:00", "19:00 - 07:00" ]) local = st.selectbox("Local de trabalho", [ "Ambulatório", "Centro Cirúrgico", "Diarismo" ]) horas = st.number_input("Quantidade de horas trabalhadas", min_value=1.0, step=0.5)

if st.button("Registrar plantão"): st.session_state.registros.append({ "Data": data.strftime("%d/%m/%Y"), "Horário": horario, "Local": local, "Horas": horas }) st.success("Plantão registrado com sucesso!")

Exibir registros e permitir exclusão

if st.session_state.registros: st.subheader("Registros do mês") for i, reg in enumerate(st.session_state.registros): col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1]) col1.write(reg["Data"]) col2.write(reg["Horário"]) col3.write(reg["Local"]) col4.write(f'{reg["Horas"]:.2f}h') if col5.button("❌", key=f"del_{i}"): st.session_state.registros.pop(i) st.experimental_rerun()

# Calcular totais
total_horas = sum(r["Horas"] for r in st.session_state.registros)
total_valor = total_horas * valor_hora
total_geral = total_valor + produtividade

st.markdown(f"**Total de horas:** {total_horas:.2f}h")
st.markdown(f"**Total (sem produtividade):** R$ {total_valor:.2f}")
st.markdown(f"**Produtividade:** R$ {produtividade:.2f}")
st.markdown(f"**Valor final:** R$ {total_geral:.2f}")

# Gerar relatório de texto
st.subheader("Gerar relatório final")
if st.button("Gerar relatório"):
    relatorio = f"Serviços {hospital} {nome} {datetime.now().strftime('%B/%Y')}\n\n"
    locais = ["Ambulatório", "Centro Cirúrgico", "Diarismo"]
    for loc in locais:
        registros_locais = [r for r in st.session_state.registros if r["Local"] == loc]
        if registros_locais:
            relatorio += f"*{loc}*:\n\n"
            for r in registros_locais:
                relatorio += f"{r['Data']} ({r['Horário']}) - {r['Horas']:.0f}h\n"
            total_loc = sum(r['Horas'] for r in registros_locais)
            valor_loc = total_loc * valor_hora
            relatorio += f"\nTotal: {total_loc:.0f} horas\n"
            relatorio += f"Valor: {total_loc:.0f} X {valor_hora:.2f} = R$ {valor_loc:.2f}\n\n"

    relatorio += f"Valor total: R$ {total_valor:.2f}\n"
    relatorio += f"\nProdutividade\n{datetime.now().strftime('%B')}: R$ {produtividade:.2f}\n"
    relatorio += f"\nValor final: R$ {total_geral:.2f}"

    st.download_button("📄 Baixar relatório (.txt)", relatorio, file_name="relatorio_plantao.txt")

else: st.info("Ainda não há plantões registrados.")

