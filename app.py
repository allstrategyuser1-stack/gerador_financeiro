import streamlit as st
from generator import gerar_movimentacoes, carregar_unidades
from datetime import date
import pandas as pd
import io

st.title("Gerador de Movimentações Financeiras")

# =========================
# 📥 TEMPLATE
# =========================
st.markdown("### 📄 Template de Unidades")

def gerar_template_unidade():
    return pd.DataFrame({
        "Código": [],
        "Nome da unidade": []
    })

buffer = io.BytesIO()
gerar_template_unidade().to_excel(buffer, index=False, engine="openpyxl")

st.download_button(
    label="Baixar template simplificado",
    data=buffer.getvalue(),
    file_name="template_unidades.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption("Você pode importar um arquivo completo ou apenas com Código e Nome da unidade.")

# =========================
# 📤 IMPORTAÇÃO
# =========================
st.markdown("### 📤 Importar Unidades")

file_unidade = st.file_uploader("Upload (CSV ou XLSX)", type=["csv", "xlsx"])

params = {}

if file_unidade:
    try:
        resultado = carregar_unidades(file_unidade)
        params["cod_unidade"] = resultado["cod_unidade"]

        st.success("Unidades carregadas com sucesso!")

        st.markdown("#### 🔍 Pré-visualização")
        st.dataframe(resultado["preview"])

    except Exception as e:
        st.error(f"Erro no arquivo: {e}")
        st.stop()

# =========================
# ⚙️ PARÂMETROS
# =========================
st.markdown("### ⚙️ Parâmetros")

qtd = st.number_input("Quantidade de registros", 1, 10000, 100)
decimais = st.slider("Casas decimais do valor", 2, 6, 2)

# =========================
# 📅 INTERVALO DE LIQUIDAÇÃO
# =========================
st.markdown("### 📅 Intervalo de liquidação")

data_inicio, data_fim = st.date_input(
    "Selecione o período de liquidação",
    value=(date.today().replace(day=1), date.today())
)

st.info("Este intervalo afeta apenas o campo de data de liquidação.")

if data_inicio > data_fim:
    st.error("A data inicial não pode ser maior que a data final.")
    st.stop()

# =========================
# 🚀 GERAÇÃO
# =========================
if st.button("Gerar CSV"):

    df = gerar_movimentacoes(qtd, decimais, data_inicio, data_fim, params)

    st.dataframe(df.head())

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Baixar CSV",
        data=csv,
        file_name="movimentacoes.csv",
        mime="text/csv"
    )
