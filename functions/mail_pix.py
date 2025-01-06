import os
import smtplib
from pathlib import Path
from email.message import EmailMessage

def enviar_email_pix(tipo_registro, loja, chave_pix, valor_pix, data_vencimento, fornecedor, comentarios, arquivo_path, destinatarios, codigo_identificação):

    email_origem = "pedro.parrini@equityrio.com.br"
    senha_do_email = 'upvz ljbh zszn kipb'

    msg = EmailMessage()
    msg['From'] = email_origem
    msg['Subject']  = f'[Registro de Compra] - {tipo_registro} - {loja} - {fornecedor} - {data_vencimento}'
    msg['To'] = destinatarios
    mensagem = f''' 

Prezado, Bruno Peniche!
<br><br>
Informo que uma nova compra foi registrada! Seguem as informações para registro e validação:
<br><br>
Tipo de registro: {tipo_registro}<br>
Unidade: {loja}<br>
Chave PIX: {chave_pix}<br>
<b>Valor do PIX: {valor_pix}</b><br>
Fornecedor: {fornecedor}<br>
Código de identificação: {codigo_identificação}<br>
<b>Data de Vencimento: {data_vencimento}</b><br>
<br><br>
Comentários extras: {comentarios}<br>
<br><br>
Por favor, prossiga com o agendamento do boleto!
<br><br>
Att.,
<br>
Pedro Vito M. Parrini - Nvestor

'''

    msg.set_content(mensagem, 'html')

    try:

        with open(arquivo_path, 'rb') as content_file:

            arquivo_path = Path(arquivo_path)
            content = content_file.read()
            msg.add_attachment(content, maintype='application', subtype=arquivo_path.suffix[1:], 
                            filename=os.path.basename(arquivo_path))
            
    except:
        pass

    try:

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_origem, senha_do_email)
            smtp.send_message(msg)
    
    except:
        pass
