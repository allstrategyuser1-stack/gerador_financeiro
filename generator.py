import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
import unicodedata


# =========================
# 🔧 NORMALIZAÇÃO
# =========================
def normalizar_texto(texto):
    return unicodedata.normalize("NFKD", str(texto))\
        .encode("ASCII", "ignore")\
        .decode()\
        .lower()\
        .strip()


def normalizar_colunas(df):
    df.columns = [normalizar_texto(col) for col in df.columns]
    return df


# =========================
# 📥 UNIDADES
# =========================
def carregar_unidades(file):

    df = pd.read_excel(file, dtype=str) if file.name.endswith("xlsx") else pd.read_csv(file, dtype=str)
    df = normalizar_colunas(df)

    col_codigo = next((c for c in df.columns if "codigo" in c), None)
    col_nome = next((c for c in df.columns if "nome" in c), None)
    col_analitico = next((c for c in df.columns if "analitico" in c), None)

    if not col_codigo:
        raise ValueError("Código não encontrado.")

    if col_analitico:
        df = df[df[col_analitico].str.upper() == "A"]

    df = df[df[col_codigo].notnull()]
    df[col_codigo] = df[col_codigo].astype(str).str.strip()

    return {
        "cod_unidade": df[col_codigo].unique().tolist(),
        "preview": df[[col_codigo, col_nome]].rename(columns={col_codigo: "Código", col_nome: "Nome"})
    }


# =========================
# 📥 CENTRO DE CUSTO
# =========================
def carregar_centro_custo(file):

    df = pd.read_excel(file, dtype=str) if file.name.endswith("xlsx") else pd.read_csv(file, dtype=str)
    df = normalizar_colunas(df)

    if not any("codigo" in c for c in df.columns):
        file.seek(0)
        df = pd.read_excel(file, dtype=str, skiprows=1)
        df = normalizar_colunas(df)

    col_codigo = next((c for c in df.columns if "codigo" in c), None)
    col_nome = next((
        c for c in df.columns
        if "nome centro de custo externo" in c
        or "centro de custo externo" in c
        or "nome" in c
    ), None)

    df = df[df[col_codigo].notnull()]
    df[col_codigo] = df[col_codigo].astype(str).str.strip()

    return {
        "cod_centro_custo": df[col_codigo].unique().tolist(),
        "preview": df[[col_codigo, col_nome]].rename(columns={col_codigo: "Código", col_nome: "Centro de custo externo"})
    }


# =========================
# 📥 CLASSIFICAÇÃO
# =========================
def carregar_classificacao(estrutura_file, externo_file):

    # -------- estrutura --------
    df_est = pd.read_excel(estrutura_file, dtype=str)
    df_est = normalizar_colunas(df_est)

    col_est = next((c for c in df_est.columns if "estrutura" in c), None)
    col_nat = next((c for c in df_est.columns if "natureza" in c), None)
    col_ana = next((c for c in df_est.columns if "analitico" in c), None)

    df_est = df_est[df_est[col_ana].str.upper() == "A"]

    mapa = dict(zip(df_est[col_est], df_est[col_nat].str.upper()))

    # -------- externo --------
    df_ext = pd.read_excel(externo_file, dtype=str)
    df_ext = normalizar_colunas(df_ext)

    if not any("codigo" in c for c in df_ext.columns):
        externo_file.seek(0)
        df_ext = pd.read_excel(externo_file, dtype=str, skiprows=1)
        df_ext = normalizar_colunas(df_ext)

    col_est_ext = next((c for c in df_ext.columns if "estrutura" in c), None)
    col_codigo = next((c for c in df_ext.columns if "codigo" in c), None)
    col_nome = next((c for c in df_ext.columns if "nome" in c), None)

    resultado = {"E": [], "S": []}
    preview = []

    for _, row in df_ext.iterrows():
        estrutura = str(row[col_est_ext]).strip()
        codigo = str(row[col_codigo]).strip()
        nome = str(row[col_nome]).strip() if col_nome else ""

        natureza = mapa.get(estrutura)

        if natureza in ["E", "S"]:
            resultado[natureza].append(codigo)
            preview.append({
                "Código": codigo,
                "Nome": nome,
                "Natureza": natureza
            })

    return {
        "classificacoes": resultado,
        "preview": pd.DataFrame(preview)
    }


# =========================
# 🚀 GERAÇÃO
# =========================
def gerar_movimentacoes(qtd, decimais, data_inicio_liq, data_fim_liq, params=None):

    dados = []
    hoje = datetime.now()
    inicio_base = hoje - timedelta(days=365)

    inicio_liq = datetime.combine(data_inicio_liq, datetime.min.time())
    fim_liq = datetime.combine(data_fim_liq, datetime.min.time())

    for i in range(qtd):

        natureza = random.choice(["E", "S"])
        valor = f"{round(random.uniform(50,5000), decimais):.{decimais}f}".replace(".", ",")

        emissao = inicio_base + timedelta(days=random.randint(0, 365))
        venc = emissao + timedelta(days=random.randint(1, 60))
        liquid = inicio_liq + timedelta(days=random.randint(0, (fim_liq - inicio_liq).days)) if random.random() > 0.5 else None

        cod_unidade = random.choice(params.get("cod_unidade", ["01"]))
        cod_cc = random.choice(params.get("cod_centro_custo", [""])) if "cod_centro_custo" in params else ""

        if params and "classificacoes" in params:
            lista = params["classificacoes"].get(natureza, [])
            cod_class = random.choice(lista) if lista else ""
        else:
            cod_class = ""

        dados.append({
            "documento": f"DOC-{1000+i}",
            "natureza": natureza,
            "valor": valor,
            "cod_unidade": cod_unidade,
            "cod_centro_de_custo": cod_cc,
            "cod_classificacao_financeira": cod_class,
            "data_vencimento": venc.strftime("%Y-%m-%d"),
            "data_liquidacao": liquid.strftime("%Y-%m-%d") if liquid else ""
        })

    return pd.DataFrame(dados)
