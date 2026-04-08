import streamlit as st
from generator import (
    gerar_movimentacoes,
    carregar_unidades,
    carregar_centro_custo
)
from datetime import date
import pandas as pd
import io

st.title("Gerador de Movimentações Financeiras")

params = {}

# =========================
# 📥 TEMPLATE UNIDADES
# =========================
st.markdown("### 📄 Template de Unidades")

def gerar_template_unidade():
    return pd.DataFrame({
        "Código": [],
        "Nome da unidade": []
    })

buffer_un = io.BytesIO()
gerar_template_unidade().to_excel(buffer_un, index=False, engine="openpyxl")

st.download_button(
    label="Baixar template de Unidades",
    data=buffer_un.getvalue(),
    file_name="template_unidades.xlsx"
)

# =========================
# 📤 IMPORTAR UNIDADES
# =========================
st.markdown("### 📤 Importar Unidades")

file_unidade = st.file_uploader("Upload Unidades", key="unidade")

if file_unidade:
    try:
        resultado = carregar_unidades(file_unidade)
        params["cod_unidade"] = resultado["cod_unidade"]

        st.success("Unidades carregadas com sucesso!")
        st.dataframe(resultado["preview"])

    except Exception as e:
        st.error(f"Erro unidades: {e}")
        st.stop()

# =========================
# 📥 TEMPLATE CENTRO CUSTO
# =========================
st.markdown("### 📄 Template Centro de Custo")

def gerar_template_cc():
    return pd.DataFrame({
        "Código": [],
        "Centro de custo externo": []
    })

buffer_cc = io.BytesIO()
gerar_template_cc().to_excel(buffer_cc, index=False, engine="openpyxl")

st.download_button(
    label="Baixar template de Centro de Custo",
    data=buffer_cc.getvalue(),
    file_name="template_centro_custo.xlsx"
)

# =========================
# 📤 IMPORTAR CENTRO CUSTO
# =========================
st.markdown("### 📤 Importar Centro de Custo")

st.info("Utilize o Centro de Custo Externo do Software Fluxo.")

file_cc = st.file_uploader("Upload Centro de Custo", key="cc")

if file_cc:
    try:
        resultado_cc = carregar_centro_custo(file_cc)
        params["cod_centro_custo"] = resultado_cc["cod_centro_custo"]

        st.success("Centro de custo carregado!")
        st.dataframe(resultado_cc["preview"])

    except Exception as e:
        st.error(f"Erro centro de custo: {e}")
        st.stop()

# =========================
# ⚙️ PARÂMETROS
# =========================
st.markdown("### ⚙️ Parâmetros")

qtd = st.number_input("Quantidade de registros", 1, 10000, 100)
decimais = st.slider("Casas decimais", 2, 6, 2)

# =========================
# 📅 INTERVALO
# =========================
st.markdown("### 📅 Intervalo de liquidação")

data_inicio, data_fim = st.date_input(
    "Período",
    value=(date.today().replace(day=1), date.today())
)

if data_inicio > data_fim:
    st.error("Data inicial maior que final")
    st.stop()

# =========================
# 🚀 GERAR
# =========================
if st.button("Gerar CSV"):

    df = gerar_movimentacoes(qtd, decimais, data_inicio, data_fim, params)

    st.dataframe(df.head())

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Baixar CSV",
        data=csv,
        file_name="movimentacoes.csv"
    )
