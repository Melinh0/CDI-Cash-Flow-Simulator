from datetime import datetime, timedelta
from workalendar.america.brazil import Brazil

def criar_calendario_brasil():
    return Brazil()

def eh_dia_util(data, calendario):
    if isinstance(data, datetime):
        data = data.date()
    return calendario.is_working_day(data)

def primeiro_dia_util_mes(ano, mes, calendario):
    data = datetime(ano, mes, 1)
    while not eh_dia_util(data, calendario):
        data += timedelta(days=1)
    return data

def lista_dias_uteis(data_inicio, data_fim, calendario):
    dias = []
    atual = data_inicio
    while atual <= data_fim:
        if eh_dia_util(atual, calendario):
            dias.append(atual)
        atual += timedelta(days=1)
    return dias

def gerar_datas_pagamento(data_inicio, num_meses, calendario):
    if isinstance(data_inicio, datetime):
        data_inicio = data_inicio.date()
    datas = []
    for i in range(1, num_meses + 1):
        mes_pagamento = data_inicio.month + i
        ano_pagamento = data_inicio.year
        while mes_pagamento > 12:
            mes_pagamento -= 12
            ano_pagamento += 1
        data_pag = primeiro_dia_util_mes(ano_pagamento, mes_pagamento, calendario)
        if data_pag.date() > data_inicio:
            datas.append(data_pag)
    return datas