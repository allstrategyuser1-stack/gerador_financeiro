import random
import uuid
from datetime import datetime, timedelta
import pandas as pd


def gerar_data(inicio, fim):
    delta = fim - inicio
    dias = random.randint(0, delta.days)
    return inicio + timedelta(days=dias)


def gerar_movimentacoes(qtd):
    dados = []

    hoje = datetime.now()
    inicio = hoje - timedelta(days=365)

    for i in range(qtd):
        natureza = random.choice(["entrada", "saida"])
        valor = round(random.uniform(50, 5000), 2)

        data_emissao = gerar_data(inicio, hoje)
        data_vencimento = data_emissao + timedelta(days=random.randint(5, 30))
        data_liquidacao = data_vencimento + timedelta(days=random.randint(0, 10))
        data_inclusao = data_emissao

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
            "prev_s_doc": random.choice([0, 1]),
            "suspenso": random.choice([0, 1]),
            "data_vencimento": data_vencimento.strftime("%Y-%m-%d"),
            "data_liquidacao": data_liquidacao.strftime("%Y-%m-%d"),
            "data_inclusao": data_inclusao.strftime("%Y-%m-%d"),
            "pend_aprov": random.choice([0, 1]),
            "erp_origem": "STREAMLIT",
            "erp_uuid": str(uuid.uuid4()),
            "data_emissao": data_emissao.strftime("%Y-%m-%d"),
            "historico": f"Lancamento {natureza} gerado automaticamente",
            "cod_cliente_fornec": random.randint(10000, 20000),
            "doc_edit": 0
        }

        dados.append(registro)

    return pd.DataFrame(dados)
