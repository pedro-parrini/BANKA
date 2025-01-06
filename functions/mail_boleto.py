import os
import smtplib
from pathlib import Path
from email.message import EmailMessage

def enviar_email_boleto(tipo_registro, loja, fornecedor, codigo_nota, data_vencimento, valor_boleto, codigo_boleto, comentarios, nota_path, boleto_path, xml_path, destinatarios, codigo_identificação):

    email_origem = "pedro.parrini@equityrio.com.br"
    senha_do_email = 'upvz ljbh zszn kipb'

    msg = EmailMessage()
    msg['From'] = email_origem
    msg['Subject']  = f'[Registro de Compra] - {tipo_registro} - {loja} - {fornecedor} - {codigo_nota} - {data_vencimento}'
    msg['To'] = destinatarios

    mensagem = f''' 

Prezado, Bruno Peniche!
<br><br>
Informo que uma nova compra foi registrada! Seguem as informações para registro e validação:
<br><br>
Tipo de registro: {tipo_registro}<br>
Unidade: {loja}<br>
Número da NF: {codigo_nota}<br>
Valor do boleto: {valor_boleto}<br>
<b>Número do boleto: {codigo_boleto}</b><br>
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

        with open(nota_path, 'rb') as content_file:

            nota_path = Path(nota_path)
            content = content_file.read()
            msg.add_attachment(content, maintype='application', subtype=nota_path.suffix[1:], 
                            filename=os.path.basename(nota_path))
            
        with open(boleto_path, 'rb') as content_file:

            boleto_path = Path(boleto_path)
            content = content_file.read()
            msg.add_attachment(content, maintype='application', subtype=boleto_path.suffix[1:], 
                            filename=os.path.basename(boleto_path))

        with open('database.xlsx', 'rb') as content_file:
            content = content_file.read()
            msg.add_attachment(content, maintype='application', subtype="xlsx", 
                            filename='database.xlsx') 

        with open(xml_path, 'rb') as content_file:

            xml_path = Path(xml_path)
            content = content_file.read()
            msg.add_attachment(content, maintype='application', subtype=xml_path.suffix[1:], 
                            filename=os.path.basename(xml_path))   

    except:
        pass

    try:

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_origem, senha_do_email)
            smtp.send_message(msg)
    
    except:
        pass