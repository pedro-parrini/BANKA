def obter_valor_boleto(codigo_barras):
    
    try:
        
        # Extrair os últimos 10 dígitos que representam o valor do boleto
        valor_boleto = codigo_barras[37:47]
        # Converter para um número decimal, assumindo dois últimos dígitos como centavos
        valor_decimal = int(valor_boleto) / 100
        return valor_decimal
    
    except ValueError:

        pass
