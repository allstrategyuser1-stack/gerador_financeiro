import random
from datetime import datetime, timedelta
import pandas as pd

def gerar_movimentacoes(qtd):
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
    return df
