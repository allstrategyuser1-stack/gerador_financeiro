import streamlit as st
from generator import gerar_movimentacoes

st.title("Gerador de Movimentações Financeiras")

qtd = st.number_input("Quantidade de registros", 1, 10000, 100)

decimais = st.slider("Casas decimais do valor", 2, 6, 2)

if st.button("Gerar CSV"):
    df = gerar_movimentacoes(qtd, decimais)

    st.dataframe(df.head())

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Baixar CSV",
        data=csv,
        file_name="movimentacoes.csv",
        mime="text/csv"
    )
