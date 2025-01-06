import smtplib
from email.message import EmailMessage
from openpyxl import load_workbook
import pandas as pd

def email_id_remove(id_number, email_copia, unidade):

    # Enviar o email de cancelamento
    email_origem = "pedro.parrini@equityrio.com.br"
    senha_do_email = 'upvz ljbh zszn kipb'

    msg = EmailMessage()
    msg['From'] = email_origem
    msg['Subject']  = f'Cancelamento do {id_number} na Banka {unidade}'
    msg['To'] = ['pedro.parrini@equityrio.com.br','brunodnpeniche@gmail.com', 'financeiro.banka@gmail.com', email_copia]
#    msg['To'] = ['pedro.parrini@equityrio.com.br', email_copia]
    mensagem = f''' 

O lançamento (ID = <b>{id_number}</b>) da Banka {unidade} foi cancelado.

'''

    msg.set_content(mensagem, 'html')

    try:

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_origem, senha_do_email)
            smtp.send_message(msg)
    
    except:
        pass


