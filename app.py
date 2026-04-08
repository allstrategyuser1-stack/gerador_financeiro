import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

st.title("Gerador de Movimentações Financeiras")

qtd = st.number_input("Quantidade de registros", 1, 1000, 100)

if st.button("Gerar CSV"):
    dados = []

    for _ in range(qtd):
        tipo = random.choice(["entrada", "saida"])
        valor = round(random.uniform(10, 1000), 2)

        data = datetime.now() - timedelta(days=random.randint(0, 365))

        dados.append({
            "data": data.strftime("%Y-%m-%d"),
            "tipo": tipo,
            "valor": valor
        })

    df = pd.DataFrame(dados)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Baixar CSV",
        data=csv,
        file_name="movimentacoes.csv",
        mime="text/csv"
    )
