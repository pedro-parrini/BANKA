# Importar bibliotecas necessárias para a aplicação

import os
import re
import pytz
import time
import shutil
import random
import smtplib
import threading
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from openpyxl import load_workbook
from email.message import EmailMessage

# Importar funções de outros arquivos

from functions.id_generate import id_number
from functions.boleto_date import obter_data_vencimento
from functions.boleto_validate import validar_boleto
from functions.boleto_value import obter_valor_boleto
from functions.folder_clean import limpar_pasta
from functions.mail_boleto import enviar_email_boleto
from functions.mail_pix import enviar_email_pix
from functions.mail_id_remove import email_id_remove
from functions.excel_merge import remove_id
from functions.cnpj_validate import validar_cnpj
from functions.cnpj_format import formatar_cnpj
from functions.folder_create import criar_pasta
from functions.folder_delete import apagar_pasta
from functions.current_date import data_atual
from functions.excel_newRow import new_last_row
from functions.excel_backup import backup_planilha
from functions.excel_merge import excel_merge
from functions.dic_value import dic_value

# Configuração inicial da página
st.set_page_config(page_title="BANKA", page_icon="💰", layout="centered", initial_sidebar_state="expanded")

st.title(":green[BANKA - Registro de Compras]")

# Barra lateral com duas opções

st.sidebar.title("Menu")
option = st.sidebar.selectbox("Escolha uma opção:", ("Lançamento de Compras", "Controle Operacional", "Cancelar Lançamento", "Cadastrar Fornecedores", "Resultados"))

# Configurar fuso horário para o Brasil
brazil_tz = pytz.timezone("America/Sao_Paulo")
current_time = datetime.now(brazil_tz)
current_hour = current_time.hour

# Conteúdo para Opção 1
if option == "Lançamento de Compras":

    # Verificar se o horário atual está entre 13:00 e 20:00
    if not 13 <= current_hour < 20:
        st.error("Acesso restrito! Esta aba pode ser acessada entre 13:00 e 20:00 no horário do Brasil.")

    else:

        # Definir a unidade
        loja = st.radio("Selecione a loja em que você trabalha:", ["Baixo Gávea", "São Conrado", "Tijuca"])

        # Definir o tipo de registro
        tipo_registro = st.radio("Qual tipo de registro você quer fazer?", ['Boleto', 'PIX'])

        destinatarios_emails = ['pedro.parrini@equityrio.com.br','brunodnpeniche@gmail.com','financeiro.banka@gmail.com','gerencia.banka@gmail.com']

#        destinatarios_emails = ['pedro.parrini@equityrio.com.br',]

        lista_familias = [
            "",
            "Bebidas",
            "Bomboniere",
            "Cigarros",
            "Diversos",
            "Jornais",
            "Livros",
            "Revistas",
            "Sorvetes",
            "Tabacaria"
        ]

        dic_emails = {
            "Baixo Gávea":"bankagavea@gmail.com", 
            "São Conrado":"bankasaoconrado@gmail.com", 
            "Tijuca":"bankatijuca@gmail.com",
        }

        email_funcionario = st.text_input("Digite seu email para receber o registro em cópia:", value=dic_value(dic_emails ,loja))

        # Obter os nomes dos fornecedores a partir da planilha de Fornecedores
        lista_fornecedores = pd.read_excel("planilhas auxiliares/Fornecedores.xlsx", sheet_name="Fornecedores")['Fornecedores'].to_list()

        # Inserir um elemento em branco na lista, para não aparecer, inicialmente, nenhum fornecedor no dropdown
        lista_fornecedores.insert(0,"")

        if tipo_registro == 'Boleto':

            # Registrar as informações 
            nota_upload = st.file_uploader("*Nota Fiscal ou Recibo de Compra (PDF ou Foto Escaneada)", type=["pdf", "jpg", "jpeg", "png"])

            numero_nota = st.text_input("*Número da Nota:")

            boleto_upload = st.file_uploader("*Boleto (PDF ou Foto Escaneada)", type=["pdf", "jpg", "jpeg", "png"])

            numero_boleto = st.text_input("*Número do Boleto:").replace(" ", "").replace(".", "").replace("-", "")

            xml_upload = st.file_uploader("XML da Nota Fiscal", type=["xml"])

            fornecedor = st.selectbox("*Fornecedor:", lista_fornecedores)

            familia = st.selectbox("*Família:", lista_familias)

            valor_boleto = st.number_input("*Valor do Boleto (BRL):", value=obter_valor_boleto(numero_boleto))

            data_vencimento = st.date_input("*Data de Vencimento do Boleto (AAAA/MM/DD)", value=obter_data_vencimento(numero_boleto))

            comentarios = st.text_input("Observações:")
       
            # Botão para registrar
            if st.button(f"Registrar Informações - {loja}"):
                    
                # Validações simples antes do registro
                if loja and email_funcionario and nota_upload and numero_nota and boleto_upload and numero_boleto and fornecedor and familia and valor_boleto and data_vencimento :

                    if validar_boleto(numero_boleto):

                        data_vencimento = data_vencimento.strftime("%d/%m/%Y")

                        destinatarios_emails.append(email_funcionario)

                        valor_boleto_formatado = 'R$ ' + str(valor_boleto)

                        criar_pasta("uploads")

                        # Salvar os arquivos inseridos na pasta correta
                        nota_path = os.path.join("uploads", nota_upload.name)
                        with open(nota_path, "wb") as f:
                            f.write(nota_upload.getbuffer())

                        boleto_path = os.path.join("uploads", boleto_upload.name)
                        with open(boleto_path, "wb") as f:
                            f.write(boleto_upload.getbuffer())
                                    
                        try:

                            xml_path = os.path.join("uploads", xml_upload.name)
                            with open(xml_path, "wb") as f:
                                f.write(xml_upload.getbuffer())

                        except:

                            xml_path = 'Qualquer coisa, apenas para não ser um str vazia'
                                    
                            pass

                        codigo_identificação = id_number()

                        nova_linha_planilha_gerencial = {"ID number": codigo_identificação, 
                                            "Data 1 (lançamento pgto)": data_atual(), 
                                            "Data 2 (dia do pgto)": data_vencimento,
                                            "Fornecedor": fornecedor, 
                                            "Banca": loja, 
                                            "Família": familia, 
                                            "Custo de Aquisição": float(valor_boleto),
                                            "Tipo": tipo_registro,
                                }
                        
                        loja_planilha = {
                            "Baixo Gávea":"planilhas auxiliares/BaixoGavea.xlsx", 
                            "São Conrado":"planilhas auxiliares/Tijuca.xlsx", 
                            "Tijuca":"planilhas auxiliares/SaoConrado.xlsx",
                        }

                        new_last_row(loja_planilha[loja], 'Controle de NFs Tomadas', nova_linha_planilha_gerencial)

                        # Enviar o email
                        enviar_email_boleto(tipo_registro, loja, fornecedor, numero_nota, data_vencimento, valor_boleto_formatado, numero_boleto, comentarios, nota_path, boleto_path, xml_path, destinatarios_emails, codigo_identificação)

                        # Limpar todos os arquivos da pasta uploads
                        apagar_pasta('uploads')

                        # Informar o usuário que os arquivos foram salvos com sucesso
                        st.success("Registro salvo com sucesso!")
                        
                    else:
                        st.error("O número do boleto é inválido.")

                else:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                

                

        elif tipo_registro == 'PIX':
            
            chave_pix = st.text_input("*Chave PIX:")

            valor_pix = st.number_input("*Valor do Pagamento (BRL):")

            arquivo_upload = st.file_uploader("*Nota Fiscal ou Recibo de Compra (PDF ou Foto Escaneada)", type=["pdf", "jpg", "jpeg", "png"])

            data_vencimento = st.date_input("*Data de Vencimento do Boleto:")

            fornecedor = st.selectbox("*Fornecedor:", lista_fornecedores)

            familia = st.selectbox("*Família:", lista_familias)

            comentarios = st.text_input("Observações:")

            # Botão para registrar
            if st.button(f"Registrar Informações - {loja}"):

                # Validações simples antes do registro
                if loja and email_funcionario and chave_pix and valor_pix and arquivo_upload and data_vencimento and fornecedor and familia:

                    data_vencimento = data_vencimento.strftime("%d/%m/%Y")
                    
                    destinatarios_emails.append(email_funcionario)

                    valor_pix_formatado = "R$ " + str(valor_pix)

                    criar_pasta("uploads")

                    # Salvar os arquivos inseridos na pasta correta
                    arquivo_path = os.path.join("uploads", arquivo_upload.name)
                    with open(arquivo_path, "wb") as f:
                        f.write(arquivo_upload.getbuffer())

                    codigo_identificação = id_number()

                    nova_linha_planilha_gerencial = {"ID number": codigo_identificação, 
                                    "Data 1 (lançamento pgto)": data_atual(), 
                                    "Data 2 (dia do pgto)": data_vencimento,
                                    "Fornecedor": fornecedor, 
                                    "Banca": loja, 
                                    "Família": familia, 
                                    "Custo de Aquisição": float(valor_pix),
                                    "Tipo": tipo_registro,
                        }
                    
                    loja_planilha = {
                            "Baixo Gávea":"planilhas auxiliares/BaixoGavea.xlsx", 
                            "São Conrado":"planilhas auxiliares/SaoConrado.xlsx", 
                            "Tijuca":"planilhas auxiliares/Tijuca.xlsx",
                        }

                    new_last_row(loja_planilha[loja], 'Controle de NFs Tomadas', nova_linha_planilha_gerencial)

                    # Enviar o email
                    enviar_email_pix(tipo_registro, loja, chave_pix, valor_pix_formatado, data_vencimento, fornecedor, comentarios, arquivo_path, destinatarios_emails, codigo_identificação)

                    # Limpar todos os arquivos da pasta uploads
                    apagar_pasta('uploads')

                    # Informar o usuário que os arquivos foram salvos com sucesso
                    st.success("Registro salvo com sucesso!")

                else:
                    st.error("Por favor, preencha todos os campos obrigatórios")

# Conteúdo para Opção 2 com autenticação por senha
elif option == "Controle Operacional":

    # Caixa de entrada para a senha
    password = st.text_input("Digite a senha para acessar a área restrita:", type="password")
    PASSWORD = "Novembro.2024"
    
    if password == PASSWORD:

        st.success("Senha correta! Agora, você tem acesso à planilha gerencial da Banka.")

        st.title("Baixar a planilha existente:")

        if st.button('Sincronizar o Sistema'):

            excel_merge(
                "planilhas auxiliares/BaixoGavea.xlsx", 
                "planilhas auxiliares/Tijuca.xlsx", 
                "planilhas auxiliares/SaoConrado.xlsx", 
                "planilhas auxiliares/Cancelamentos.xlsx", 
                "Banka l Planilha Gerencial.xlsx"
                )

        # Opção para baixar a planilha existente

        file_path = 'Banka l Planilha Gerencial.xlsx'

        with open(file_path, "rb") as file:

            download_planilha = st.download_button(
                label="Baixar Planilha Gerencial",
                data=file,
                file_name="Banka l Planilha Gerencial.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # Upload de uma nova planilha

        st.title("Salvar uma nova planilha:")

        uploaded_file = st.file_uploader("Selecione a planilha da Banka mais recente", type=["xlsx"])

        if uploaded_file is not None:

            try:
                # Salvar a nova planilha, substituindo a existente
                with open(file_path, "wb") as file:

                    file.write(uploaded_file.getbuffer())

                    time.sleep(5)

                backup_planilha("Banka l Planilha Gerencial.xlsx")

                st.success("Novo arquivo Excel enviado e substituído com sucesso!")

            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")

    elif password:
        st.error("Senha incorreta. Tente novamente.")

elif option == "Cancelar Lançamento":

    destinatarios_emails_cancelamento = ["",
                                'pedro.parrini@equityrio.com.br',
                                'brunodnpeniche@gmail.com', 
                                'financeiro.banka@gmail.com', 
                                'gerencia.banka@gmail.com',
                                "bankagavea@gmail.com", 
                                "bankasaoconrado@gmail.com", 
                                "bankatijuca@gmail.com",
                                ]
    
    email_funcionario = st.selectbox("*Email para receber o registro em cópia:", destinatarios_emails_cancelamento)
    loja = st.radio("*Selecione a unidade:", ["Baixo Gávea", "São Conrado", "Tijuca"])
    id = st.text_input("*ID:")

    if st.button("Remover Lançamento"):

        if email_funcionario and id and loja:

            new_data = {
                'ID number': id,
            }

            new_last_row("planilhas auxiliares/Cancelamentos.xlsx", "Cancelar IDs", new_data)

            email_id_remove(id, email_funcionario, loja)

            st.success("Lançamento removido com sucesso!")
        
        else:

            st.error("Indique o código que será removido, o email e a unidade para confirmar o cancelamento.")

elif option == "Cadastrar Fornecedores":

    # Entrada do nome do fornecedor
    nome_fornecedor = st.text_input("*Nome do Fornecedor:")

    # Entrada do CNPJ
    cnpj_fornecedor = st.text_input("CNPJ do Fornecedor:")

    if cnpj_fornecedor:

        cnpj_fornecedor = formatar_cnpj(cnpj_fornecedor)

        validar_cnpj(cnpj_fornecedor)

    # Contato do Fornecedor
    contato_fornecedor = st.text_input("Contato do Fornecedor:")

    # Botão para salvar os dados
    if st.button("Cadastrar o Fornecedor"):

        if nome_fornecedor:

            new_row_data = {
                'Fornecedores': nome_fornecedor,
                'CNPJ': cnpj_fornecedor,
                'Contato': contato_fornecedor,
                }

            new_last_row("planilhas auxiliares/Fornecedores.xlsx", 'Fornecedores', new_row_data)

            time.sleep(5)

            st.success(f"{nome_fornecedor} cadastrado com sucesso!")

        else:
            st.error("Por favor, informe o nome do fornecedor.")
    
    with open("planilhas auxiliares/Fornecedores.xlsx", "rb") as file:
        st.download_button(
            label="Baixar a planilha com todos os fornecedores",
            data=file,
            file_name=r"Fornecedores.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )    
        
elif option == "Resultados":
    pass