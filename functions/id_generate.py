import pandas as pd
import random

# Gerar um ID number para identificar cada compra
def id_number():

    df = list(pd.read_excel('Banka l Planilha Gerencial.xlsx', sheet_name='Controle de NFs Tomadas')['ID number'])
    i=1

    while i>0:

        numero = ''.join(str(random.randint(0, 9)) for _ in range(6))
        
        if numero in df or int(numero[0]) == 0:
            continue
        
        else:
            return numero
