import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
import unicodedata


# =========================
# 🔧 NORMALIZAÇÃO
# =========================
def normalizar_texto(texto):
    if not texto:
        return ""
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

    try:
        df = pd.read_excel(file, dtype=str)
    except:
        file.seek(0)
        df = pd.read_csv(file, dtype=str)

    df = normalizar_colunas(df)

    col_codigo = next((c for c in df.columns if "codigo" in c), None)
    col_nome = next((c for c in df.columns if "nome" in c), None)

    if not col_codigo:
        raise ValueError("Coluna de Código não encontrada.")

    if not col_nome:
        df["nome"] = ""
        col_nome = "nome"

    # Detectar analítico
    col_analitico = next((c for c in df.columns if "analitico" in c), None)

    if col_analitico:
        df = df[df[col_analitico].str.upper() == "A"]

        if df.empty:
            raise ValueError("Nenhuma unidade analítica encontrada.")

    df = df[df[col_codigo].notnull()]
    df[col_codigo] = df[col_codigo].astype(str).str.strip()

    return {
        "cod_unidade": df[col_codigo].unique().tolist(),
        "preview": df[[col_codigo, col_nome]].rename(
            columns={col_codigo: "Código", col_nome: "Nome da unidade"}
        )
    }


# =========================
# 📥 CENTRO DE CUSTO
# =========================
def carregar_centro_custo(file):

    try:
        df = pd.read_excel(file, dtype=str)
    except:
        file.seek(0)
        df = pd.read_csv(file, dtype=str)

    df = normalizar_colunas(df)

    # Cabeçalho duplo
    if not any("codigo" in c for c in df.columns):
        file.seek(0)
        df = pd.read_excel(file, dtype=str, skiprows=1)
        df = normalizar_colunas(df)

    # Detectar colunas
    if "codigo" in df.columns and "nome centro de custo externo" in df.columns:
        col_codigo = "codigo"
        col_nome = "nome centro de custo externo"
    else:
        col_codigo = next((c for c in df.columns if "codigo" in c), None)

        col_nome = next((
            c for c in df.columns
            if "nome centro de custo externo" in c
            or "centro de custo externo" in c
            or "nome" in c
        ), None)

    if not col_codigo:
        raise ValueError("Coluna de Código não encontrada.")

    if not col_nome:
        df["nome"] = ""
        col_nome = "nome"

    df = df[df[col_codigo].notnull()]
    df[col_codigo] = df[col_codigo].astype(str).str.strip()

    return {
        "cod_centro_custo": df[col_codigo].unique().tolist(),
        "preview": df[[col_codigo, col_nome]].rename(
            columns={
                col_codigo: "Código",
                col_nome: "Centro de custo externo"
            }
        )
    }


# =========================
# 🔧 AUXILIARES
# =========================
def gerar_data(inicio, fim):
    return inicio + timedelta(days=random.randint(0, (fim - inicio).days))


def gerar_valor(decimais):
    v = round(random.uniform(50, 5000), decimais)
    return f"{v:.{decimais}f}".replace(".", ",")


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
        valor = gerar_valor(decimais)

        emissao = gerar_data(inicio_base, hoje)
        venc = emissao + timedelta(days=random.randint(1, 60))

        liquid = gerar_data(inicio_liq, fim_liq) if random.random() > 0.5 else None

        cod_unidade = (
            random.choice(params["cod_unidade"])
            if params and "cod_unidade" in params
            else "01"
        )

        cod_centro_custo = (
            random.choice(params["cod_centro_custo"])
            if params and "cod_centro_custo" in params
            else ""
        )

        dados.append({
            "documento": f"DOC-{1000+i}",
            "natureza": natureza,
            "valor": valor,
            "cod_unidade": cod_unidade,
            "cod_centro_de_custo": cod_centro_custo,
            "data_vencimento": venc.strftime("%Y-%m-%d"),
            "data_liquidacao": liquid.strftime("%Y-%m-%d") if liquid else ""
        })

    return pd.DataFrame(dados)
