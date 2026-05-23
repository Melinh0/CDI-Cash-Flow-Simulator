def formatar_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_analise_textual(relatorio, juros_totais, amortizacao_total, parcela_mensal, num_meses):
    if not relatorio:
        return "Sem dados para análise."

    saldo_inicial = relatorio[0]["saldo_devedor_rem"] + relatorio[0]["amortizacao_principal"] + relatorio[0]["juros_acumulados_periodo"]
    saldo_final = relatorio[-1]["saldo_devedor_rem"]
    if saldo_final < saldo_inicial:
        comportamento = "amortização"
    else:
        comportamento = "crescimento"

    primeiras_parcelas = relatorio[:3]
    proporcoes_juros = []
    for p in primeiras_parcelas:
        juros = p["juros_acumulados_periodo"]
        amort = p["amortizacao_principal"]
        total = juros + amort
        if total > 0:
            proporcoes_juros.append(juros / total)
    proporcao_media_juros = sum(proporcoes_juros) / len(proporcoes_juros) if proporcoes_juros else 0
    amortizacao_media_primeiras = sum(p["amortizacao_principal"] for p in primeiras_parcelas) / len(primeiras_parcelas) if primeiras_parcelas else 0

    mes_max_juros = max(relatorio, key=lambda x: x["juros_acumulados_periodo"])
    saldo_anterior_mes = mes_max_juros["saldo_devedor_rem"] + mes_max_juros["amortizacao_principal"]
    if saldo_anterior_mes > 0:
        taxa_acumulada_max = (mes_max_juros["juros_acumulados_periodo"] / saldo_anterior_mes) * 100
    else:
        taxa_acumulada_max = 0.0

    texto = (
        f"No período analisado de {num_meses} meses, a linha de crédito para capital de giro apresentou um comportamento de "
        f"{comportamento} do saldo devedor. Nas parcelas iniciais, o juro acumulado consumiu cerca de "
        f"{proporcao_media_juros:.1%} do valor pago, resultando em uma amortização líquida média de {formatar_br(amortizacao_media_primeiras)}. "
        f"O mês com maior pressão de juros foi {mes_max_juros['data_pagamento'].strftime('%B/%Y')}, indicando o impacto "
        f"da capitalização composta diária sob a taxa acumulada de {taxa_acumulada_max:.2f}%."
    )
    return texto