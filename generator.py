import random
import uuid
from datetime import datetime, timedelta
import pandas as pd


def gerar_data(inicio, fim):
    delta = fim - inicio
    dias = random.randint(0, delta.days)
    return inicio + timedelta(days=dias)


def gerar_valor(decimais):
    valor = round(random.uniform(50, 5000), decimais)
    return f"{valor:.{decimais}f}".replace(".", ",")


def gerar_movimentacoes(qtd, decimais):
    dados = []

    hoje = datetime.now()
    inicio = hoje - timedelta(days=365)

    for i in range(qtd):

        # Natureza (E ou S)
        natureza = random.choice(["E", "S"])

        # Valor formatado
        valor = gerar_valor(decimais)

        # Datas base
        data_emissao = gerar_data(inicio, hoje)
        data_vencimento = data_emissao + timedelta(days=random.randint(1, 60))

        # Data liquidação (pode ser vazia)
        if random.random() < 0.5:
            data_liquidacao = None
        else:
            data_liquidacao = data_vencimento + timedelta(days=random.randint(-10, 10))
            if data_liquidacao > hoje:
                data_liquidacao = hoje

        # Ajuste: emissão nunca pode ser > vencimento/liquidação
        if data_emissao > data_vencimento:
            data_emissao = data_vencimento

        if data_liquidacao and data_emissao > data_liquidacao:
            data_emissao = data_liquidacao

        # Data inclusão = hoje
        data_inclusao = hoje

        # Cliente / Fornecedor
        if random.random() < 0.15:
            cod_cliente_fornec = f"CF{random.randint(1,5)}"
        else:
            if natureza == "E":
                cod_cliente_fornec = f"C{random.randint(1,50)}"
            else:
                cod_cliente_fornec = f"F{random.randint(1,50)}"

        # doc_edit regra
        if data_vencimento > hoje and not data_liquidacao:
            doc_edit = "S"
        else:
            doc_edit = "N"

        registro = {
            "documento": f"DOC-{1000+i}",
            "natureza": natureza,
            "valor": valor,
            "cod_unidade": random.choice([1, 2, 3]),
            "cod_centro_de_custo": random.choice([101, 102, 103]),
            "cod_tesouraria": random.choice([1, 2]),
            "cod_tipo_de_documento": random.choice([10, 20]),
            "cod_classificacao_financeira": random.choice([500, 600]),
            "cod_projeto": random.choice([1000, 2000]),

            # Sempre N
            "prev_s_doc": "N",
            "suspenso": "N",
            "pend_aprov": "N",

            # Datas formatadas
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
