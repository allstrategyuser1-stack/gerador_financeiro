import streamlit as st
from generator import gerar_movimentacoes
from datetime import date

st.title("Gerador de Movimentações Financeiras")

# Quantidade de registros
qtd = st.number_input("Quantidade de registros", 1, 10000, 100)

# Casas decimais
decimais = st.slider("Casas decimais do valor", 2, 6, 2)

# Intervalo de liquidação
st.markdown("### Intervalo de liquidação")

data_inicio, data_fim = st.date_input(
    "Selecione o período de liquidação",
    value=(date.today().replace(day=1), date.today())
)

st.info("Este intervalo afeta apenas o campo data_liquidacao. As demais datas não são impactadas.")

# Validação
if data_inicio > data_fim:
    st.error("A data inicial não pode ser maior que a data final.")
    st.stop()

# Botão gerar
if st.button("Gerar CSV"):

    df = gerar_movimentacoes(qtd, decimais, data_inicio, data_fim)

    st.dataframe(df.head())

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Baixar CSV",
        data=csv,
        file_name="movimentacoes.csv",
        mime="text/csv"
    )
