import random
import uuid
from datetime import datetime, timedelta
import pandas as pd


# =========================
# 📥 UNIDADES
# =========================
def carregar_unidades(file):

    try:
        df = pd.read_excel(file, dtype=str)
    except:
        try:
            file.seek(0)
            df = pd.read_csv(file, dtype=str)
        except:
            raise ValueError("Arquivo inválido.")

    df.columns = [col.strip().lower() for col in df.columns]

    col_codigo = next((c for c in df.columns if "codigo" in c or "código" in c), None)
    col_nome = next((c for c in df.columns if "nome" in c), None)

    if not col_codigo:
        raise ValueError("Coluna de Código não encontrada.")

    if not col_nome:
        df["nome"] = ""
        col_nome = "nome"

    col_analitico = next((c for c in df.columns if "sintético" in c or "analitico" in c), None)

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

    # =========================
    # TENTAR LEITURA NORMAL
    # =========================
    try:
        df = pd.read_excel(file, dtype=str)
    except:
        try:
            file.seek(0)
            df = pd.read_csv(file, dtype=str)
        except:
            raise ValueError("Arquivo inválido.")

    # Normalizar colunas
    df.columns = [str(col).strip().lower() for col in df.columns]

    # =========================
    # DETECTAR CABEÇALHO DUPLO
    # =========================
    if not any("código" in col or "codigo" in col for col in df.columns):
        try:
            file.seek(0)

            # Releitura ignorando primeira linha
            df = pd.read_excel(file, dtype=str, skiprows=1)

            df.columns = [str(col).strip().lower() for col in df.columns]

        except:
            raise ValueError("Não foi possível interpretar o cabeçalho do arquivo.")

    # =========================
    # DETECTAR COLUNAS
    # =========================
    if "código" in df.columns and "nome centro de custo externo" in df.columns:
        col_codigo = "código"
        col_nome = "nome centro de custo externo"
    else:
        col_codigo = next((c for c in df.columns if "codigo" in c or "código" in c), None)
        col_nome = next((c for c in df.columns if "nome" in c), None)

    if not col_codigo:
        raise ValueError("Coluna de Código não encontrada.")

    if not col_nome:
        df["nome"] = ""
        col_nome = "nome"

    # =========================
    # LIMPEZA
    # =========================
    df = df[df[col_codigo].notnull()]
    df[col_codigo] = df[col_codigo].astype(str).str.strip()

    if df.empty:
        raise ValueError("Nenhum código válido encontrado.")

    # =========================
    # RETORNO
    # =========================
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
    delta = fim - inicio
    return inicio + timedelta(days=random.randint(0, delta.days))


def gerar_valor(decimais):
    valor = round(random.uniform(50, 5000), decimais)
    return f"{valor:.{decimais}f}".replace(".", ",")


# =========================
# 🚀 GERAÇÃO
# =========================
def gerar_movimentacoes(qtd, decimais, data_inicio_liq, data_fim_liq, params=None):

    dados = []
    hoje = datetime.now()
    inicio_base = hoje - timedelta(days=365)

    inicio_liq = datetime.combine(data_inicio_liq, datetime.min.time())
    fim_liq = datetime.combine(data_fim_liq, datetime.min.time())

    if fim_liq > hoje:
        fim_liq = hoje

    for i in range(qtd):

        natureza = random.choice(["E", "S"])
        valor = gerar_valor(decimais)

        data_emissao = gerar_data(inicio_base, hoje)
        data_vencimento = data_emissao + timedelta(days=random.randint(1, 60))

        data_liquidacao = (
            gerar_data(inicio_liq, fim_liq) if random.random() > 0.5 else None
        )

        if data_liquidacao and data_emissao > data_liquidacao:
            data_emissao = data_liquidacao

        data_inclusao = hoje

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

        cod_cliente_fornec = (
            f"CF{random.randint(1,5)}"
            if random.random() < 0.15
            else (f"C{random.randint(1,50)}" if natureza == "E" else f"F{random.randint(1,50)}")
        )

        doc_edit = "S" if data_vencimento > hoje and not data_liquidacao else "N"

        dados.append({
            "documento": f"DOC-{1000+i}",
            "natureza": natureza,
            "valor": valor,
            "cod_unidade": cod_unidade,
            "cod_centro_de_custo": cod_centro_custo,
            "cod_tesouraria": "1",
            "cod_tipo_de_documento": "10",
            "cod_classificacao_financeira": "500",
            "cod_projeto": "1000",
            "prev_s_doc": "N",
            "suspenso": "N",
            "pend_aprov": "N",
            "data_vencimento": data_vencimento.strftime("%Y-%m-%d"),
            "data_liquidacao": data_liquidacao.strftime("%Y-%m-%d") if data_liquidacao else "",
            "data_inclusao": data_inclusao.strftime("%Y-%m-%d"),
            "erp_origem": "STREAMLIT",
            "erp_uuid": str(uuid.uuid4()),
            "data_emissao": data_emissao.strftime("%Y-%m-%d"),
            "historico": f"Lancamento {'entrada' if natureza == 'E' else 'saida'}",
            "cod_cliente_fornec": cod_cliente_fornec,
            "doc_edit": doc_edit
        })

    return pd.DataFrame(dados)
