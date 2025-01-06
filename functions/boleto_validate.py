def validar_boleto(linha_digitavel):

    linha_digitavel = linha_digitavel.replace(" ", "").replace(".", "").replace("-", "")

    try:

        int(linha_digitavel)

    except:

        return False

    if len(linha_digitavel) == 47 or len(linha_digitavel) == 48:
        return True
    
    else:
        return False


