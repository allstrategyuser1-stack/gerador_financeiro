import random
import uuid
from datetime import datetime, timedelta
import pandas as pd


# =========================
# 📥 IMPORTAÇÃO ROBUSTA
# =========================
def carregar_unidades(file):

    # Tentar ler como Excel primeiro
    try:
        df = pd.read_excel(file)
    except:
        try:
            file.seek(0)
            df = pd.read_csv(file)
        except:
            raise ValueError("Arquivo inválido. Use CSV ou XLSX.")

    # Normalizar nomes
    df.columns = [col.strip().lower() for col in df.columns]

    # Detectar coluna de código
    col_codigo = None
    for col in df.columns:
        if "código" in col or "codigo" in col:
            col_codigo = col
            break

    if not col_codigo:
        raise ValueError("Coluna de Código não encontrada.")

    # Detectar coluna de nome
    col_nome = None
    for col in df.columns:
        if "nome" in col:
            col_nome = col
            break

    # Se não tiver nome, cria vazio
    if not col_nome:
        df["nome"] = ""
        col_nome = "nome"

    # Limpar dados
    df = df[df[col_codigo].notnull()]

    if df.empty:
        raise ValueError("Nenhum código válido encontrado.")

    return {
        "cod_unidade": df[col_codigo].astype(str).unique().tolist(),
        "preview": df[[col_codigo, col_nome]].rename(
            columns={col_codigo: "Código", col_nome: "Nome da unidade"}
        )
    }


# =========================
# 🔧 AUXILIARES
# =========================
def gerar_data(inicio, fim):
    delta = fim - inicio
    dias = random.randint(0, delta.days)
    return inicio + timedelta(days=dias)


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

        if random.random() < 0.5:
            data_liquidacao = None
        else:
            data_liquidacao = gerar_data(inicio_liq, fim_liq)

        if data_emissao > data_vencimento:
            data_emissao = data_vencimento

        if data_liquidacao and data_emissao > data_liquidacao:
            data_emissao = data_liquidacao

        data_inclusao = hoje

        if params and "cod_unidade" in params:
            cod_unidade = random.choice(params["cod_unidade"])
        else:
            cod_unidade = random.choice([1, 2, 3])

        if random.random() < 0.15:
            cod_cliente_fornec = f"CF{random.randint(1,5)}"
        else:
            cod_cliente_fornec = f"C{random.randint(1,50)}" if natureza == "E" else f"F{random.randint(1,50)}"

        if data_vencimento > hoje and not data_liquidacao:
            doc_edit = "S"
        else:
            doc_edit = "N"

        registro = {
            "documento": f"DOC-{1000+i}",
            "natureza": natureza,
            "valor": valor,
            "cod_unidade": cod_unidade,
            "cod_centro_de_custo": random.choice([101, 102, 103]),
            "cod_tesouraria": random.choice([1, 2]),
            "cod_tipo_de_documento": random.choice([10, 20]),
            "cod_classificacao_financeira": random.choice([500, 600]),
            "cod_projeto": random.choice([1000, 2000]),

            "prev_s_doc": "N",
            "suspenso": "N",
            "pend_aprov": "N",

            "data_vencimento": data_vencimento.strftime("%Y-%m-%d"),
            "data_liquidacao": data_liquidacao.strftime("%Y-%m-%d") if data_liquidacao else "",
            "data_inclusao": data_inclusao.strftime("%Y-%m-%d"),

            "erp_origem": "STREAMLIT",
            "erp_uuid": str(uuid.uuid4()),

            "data_emissao": data_emissao.strftime("%Y-%m-%d"),

            "historico": f"Lancamento {'entrada' if natureza == 'E' else 'saida'} gerado automaticamente",

            "cod_cliente_fornec": cod_cliente_fornec,
            "doc_edit": doc_edit
        }

        dados.append(registro)

    return pd.DataFrame(dados)
