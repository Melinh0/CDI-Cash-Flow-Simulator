from datetime import datetime
from src.calendar_utils import (
    criar_calendario_brasil, lista_dias_uteis, gerar_datas_pagamento
)

def aplicar_capitalizacao_diaria(saldo, fator):
    return saldo * fator

def calcular_fator_diario(taxa_cdi, taxa_fixa):
    return (1 + taxa_cdi) * (1 + taxa_fixa)

def simular_emprestimo(
    principal, data_liberacao, taxa_cdi, taxa_fixa,
    parcela_mensal, num_meses
):
    if isinstance(data_liberacao, datetime):
        data_liberacao = data_liberacao
    else:
        data_liberacao = datetime.combine(data_liberacao, datetime.min.time())

    calendario = criar_calendario_brasil()
    datas_pagamento = gerar_datas_pagamento(data_liberacao, num_meses, calendario)
    data_fim = datas_pagamento[-1] if datas_pagamento else data_liberacao
    dias_uteis = lista_dias_uteis(data_liberacao, data_fim, calendario)
    
    saldo_atual = principal
    juros_acumulados_periodo = 0.0
    ultimo_pagamento = data_liberacao
    relatorio_mensal = []
    
    juros_totais_pagos = 0.0
    amortizacao_total = 0.0
    valor_total_pago = 0.0
    
    fator_diario = calcular_fator_diario(taxa_cdi, taxa_fixa)
    
    for dia in dias_uteis:
        saldo_anterior = saldo_atual
        saldo_atual = aplicar_capitalizacao_diaria(saldo_atual, fator_diario)
        juros_dia = saldo_atual - saldo_anterior
        juros_acumulados_periodo += juros_dia
        
        if dia in datas_pagamento:
            juros_a_pagar = min(juros_acumulados_periodo, parcela_mensal)
            amortizacao = parcela_mensal - juros_a_pagar
            saldo_atual -= parcela_mensal
            
            if juros_acumulados_periodo > parcela_mensal:
                amortizacao = 0.0
            
            if saldo_atual < 0:
                saldo_atual = 0.0
            
            relatorio_mensal.append({
                "data_pagamento": dia,
                "juros_acumulados_periodo": juros_acumulados_periodo,
                "amortizacao_principal": amortizacao,
                "saldo_devedor_rem": saldo_atual
            })
            
            juros_totais_pagos += juros_a_pagar
            amortizacao_total += amortizacao
            valor_total_pago += parcela_mensal
            
            juros_acumulados_periodo = 0.0
            ultimo_pagamento = dia
            
            if saldo_atual <= 0:
                break
    
    saldo_final = max(0.0, saldo_atual)
    
    return {
        "relatorio": relatorio_mensal,
        "juros_totais_pagos": juros_totais_pagos,
        "amortizacao_total": amortizacao_total,
        "valor_total_pago": valor_total_pago,
        "saldo_devedor_final": saldo_final
    }