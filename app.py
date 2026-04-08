import streamlit as st
from generator import gerar_movimentacoes, carregar_unidades
from datetime import date

st.title("Gerador de Movimentações Financeiras")

# =========================
# 📥 IMPORTAÇÃO DE UNIDADE
# =========================
st.markdown("### 📥 Importar base de Unidades")

file_unidade = st.file_uploader("Upload do arquivo de Unidades", type=["csv"])

params = {}

if file_unidade:
    try:
        resultado = carregar_unidades(file_unidade)
        params["cod_unidade"] = resultado["cod_unidade"]

        st.success("Unidades carregadas com sucesso!")

        st.markdown("#### 🔍 Pré-visualização das unidades analíticas")
        st.dataframe(resultado["preview"])

    except Exception as e:
        st.error(f"Erro no arquivo: {e}")
        st.stop()

# =========================
# ⚙️ PARÂMETROS
# =========================
qtd = st.number_input("Quantidade de registros", 1, 10000, 100)
decimais = st.slider("Casas decimais do valor", 2, 6, 2)

# =========================
# 📅 INTERVALO DE LIQUIDAÇÃO
# =========================
st.markdown("### Intervalo de liquidação")

data_inicio, data_fim = st.date_input(
    "Selecione o período de liquidação",
    value=(date.today().replace(day=1), date.today())
)

st.info("Este intervalo afeta apenas o campo de data de liquidação. As demais datas não são impactadas.")

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
