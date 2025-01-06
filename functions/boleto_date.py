from datetime import datetime, timedelta

def obter_data_vencimento(codigo_barras):

    try:

        # O fator de vencimento está nos dígitos 34 a 37 do código de barras
        fator_vencimento = int(codigo_barras[33:37])
            
        # A data-base é 07/10/1997
        data_base = datetime(1997, 10, 7)
            
        # Calcula a data de vencimento adicionando o fator de vencimento à data-base
        data_vencimento = data_base + timedelta(days=fator_vencimento)
            
        # Retorna a data
        return data_vencimento
    
    except:
        pass