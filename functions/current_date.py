from datetime import datetime

# Obter a data no momento atual
def data_atual():
    data_atual = datetime.now()
    return data_atual.strftime("%d/%m/%Y")


