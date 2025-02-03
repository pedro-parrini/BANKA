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
import plotly.express as px
import plotly.graph_objects as go
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

                        destinatarios_emails.insert(0, email_funcionario)

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
                    
                    destinatarios_emails.insert(0, email_funcionario)

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

    # Carregar a planilha
    file_path = 'Banka l Planilha Gerencial.xlsx'

    # Relacionar o nome da unidade com os nomes das respectivas abas na Planilha Gerencial
    sheets = {
        'Baixo Gávea': pd.read_excel(file_path, sheet_name='Output BG'),
        'Tijuca': pd.read_excel(file_path, sheet_name='Output TJK'),
        'PJ': pd.read_excel(file_path, sheet_name='Output PJ'),
        'São Conrado': pd.read_excel(file_path, sheet_name='Output SC'),
        'Consolidado': pd.read_excel(file_path, sheet_name='Output Consolidado (Caixa)'),
    }

    # Configurar o layout do Streamlit
    unidade = st.radio('*Selecionar a unidade', ['Baixo Gávea', 'Tijuca', 'PJ', 'São Conrado', 'Consolidado'])

    # Opções de escolha (unidade)
    df = dic_value(sheets, unidade)

    # Tratar o df
    def convert_column(column_name):
        try:
            # Tentar converter para o formato mês/ano
            return pd.to_datetime(column_name).strftime('%m/%Y')
        except Exception:
            # Se falhar, manter o nome original da coluna
            return column_name

    df.columns = [convert_column(col) for col in df.columns]

    df = df.drop(df.columns[[1, 2]], axis=1)

    # Filtrar as colunas de interesse
    columns_to_keep = [unidade, '08/2024', '09/2024', '10/2024', '11/2024', '12/2024', '01/2025', '02/2025']

    df = df[columns_to_keep]

    # Definindo a coluna 'unidade' como índice
    df.set_index(unidade, inplace=True)

    # Transpondo o DataFrame para organizar as datas como colunas
    df_transposto = df.T.reset_index()
    df_transposto = df_transposto.rename(columns={'index': 'Data'})

    # Convertendo as datas para datetime
    df_transposto['Data'] = pd.to_datetime(df_transposto['Data'], format='%m/%Y')


    # Gráfico 1 - Receitas vs Custo de Aquisição de Produtos (caixa) + Margem Bruta

    # Criando a figura com barras para Entrada de Caixa e Custo de Aquisição de Produtos
    fig1 = go.Figure()

    # Adicionando as barras
    fig1.add_trace(go.Bar(
        x=df_transposto['Data'],
        y=df_transposto['Entrada de Caixa'],
        name='Entrada de Caixa'
    ))

    fig1.add_trace(go.Bar(
        x=df_transposto['Data'],
        y=df_transposto['Custo de Aquisição de Produtos'],
        name='Custo de Aquisição de Produtos'
    ))

    # Adicionando a linha mgm bruta no eixo Y secundário com linha tracejada e pontos
    fig1.add_trace(go.Scatter(
        x=df_transposto['Data'],
        y=df_transposto['mgm bruta'],
        mode='lines+markers',  # Mantém a linha com bolinhas nos pontos
        name='mgm bruta',
        yaxis='y2',  # Define que será no eixo Y secundário
        line=dict(color='red', width=2, dash='dash'),  # Linha tracejada
        marker=dict(size=8)  # Tamanho das bolinhas
    ))

    # Configurando o layout com eixo Y secundário, título centralizado e legenda ajustada
    fig1.update_layout(
        title={
            'text': 'Entrada de Caixa, Custo de Aquisição de Produtos e mgm bruta',
            'x': 0.5,  # Centraliza o título
            'xanchor': 'center'
        },
        xaxis=dict(
            title='Data',
            tickmode='linear',
            dtick='M1',
            tickformat='%m/%Y'
        ),
        yaxis=dict(
            title='Valor (R$)'
        ),
        yaxis2=dict(
            title='mgm bruta',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            x=1.15,  # Move a legenda para a direita
            y=1,     # Mantém a legenda na parte superior
            bgcolor='rgba(255,255,255,0.5)',  # Fundo semitransparente para não cobrir o gráfico
            bordercolor='black',
            borderwidth=1
        ),
        barmode='group'
    )

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig1)


    # Gráfico 2 - Destrinchar as Receitas (caixa)

    fig2 = go.Figure()

    # Lista das categorias de custo a serem empilhadas
    categorias_custo = [
        'Crédito', 
        'Débito', 
        'Pix', 
        'Antecipação (crédito)', 
        'Cash', 
        'Receitas Financeiras (líquida)', 
    ]

    # Adicionando cada categoria de custo como uma barra empilhada
    for categoria in categorias_custo:
        fig2.add_trace(go.Bar(
            x=df_transposto['Data'],
            y=df_transposto[categoria],
            name=categoria
        ))

    # Configurando o layout com barras empilhadas
    fig2.update_layout(
        title={
            'text': 'Entradas de Caixa por Categoria',
            'x': 0.5,  # Centraliza o título
            'xanchor': 'center'
        },
        xaxis=dict(
            title='Data',
            tickmode='linear',
            dtick='M1',
            tickformat='%m/%Y'
        ),
        yaxis=dict(
            title='Total (R$)'
        ),
        legend=dict(
            x=1.05,  # Move a legenda para a direita para não cobrir o gráfico
            y=1,
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='black',
            borderwidth=1
        ),
        barmode='stack'  # Configuração para barras empilhadas
    )

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig2)


    # Gráfico 3 - Destrinhcar o Custo com Aquisição de Produtos

    fig3 = go.Figure()

    # Lista das categorias de custo a serem empilhadas
    categorias_custo = [
        'Bebidas', 
        'Bomboniere', 
        'Cigarros', 
        'Diversos', 
        'Jornais', 
        'Livros', 
        'Revistas', 
        'Sorvetes', 
        'Tabacaria'
    ]

    # Adicionando cada categoria de custo como uma barra empilhada
    for categoria in categorias_custo:
        fig3.add_trace(go.Bar(
            x=df_transposto['Data'],
            y=df_transposto[categoria],
            name=categoria
        ))

    # Configurando o layout com barras empilhadas
    fig3.update_layout(
        title={
            'text': 'Custos de Aquisição de Produtos por Categoria',
            'x': 0.5,  # Centraliza o título
            'xanchor': 'center'
        },
        xaxis=dict(
            title='Data',
            tickmode='linear',
            dtick='M1',
            tickformat='%m/%Y'
        ),
        yaxis=dict(
            title='Custo Total (R$)'
        ),
        legend=dict(
            x=1.05,  # Move a legenda para a direita para não cobrir o gráfico
            y=1,
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='black',
            borderwidth=1
        ),
        barmode='stack'  # Configuração para barras empilhadas
    )

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig3)


    # Gráfico 4 - Destrinhcar os Custos, em geral

    fig4 = go.Figure()

    # Lista das categorias de custo a serem empilhadas
    categorias_custo = [
        'Equipe Operacional', 
        'Despesas c/ Imóvel', 
        'Despesas Administrativas', 
        'Despesas Tributárias', 
        'Custo c/ Taxas e Devoluções', 
    ]

    # Adicionando cada categoria de custo como uma barra empilhada
    for categoria in categorias_custo:
        fig4.add_trace(go.Bar(
            x=df_transposto['Data'],
            y=df_transposto[categoria],
            name=categoria
        ))

    # Configurando o layout com barras empilhadas
    fig4.update_layout(
        title={
            'text': 'Custos Operacionais',
            'x': 0.5,  # Centraliza o título
            'xanchor': 'center'
        },
        xaxis=dict(
            title='Data',
            tickmode='linear',
            dtick='M1',
            tickformat='%m/%Y'
        ),
        yaxis=dict(
            title='Custo Total (R$)'
        ),
        legend=dict(
            x=1.05,  # Move a legenda para a direita para não cobrir o gráfico
            y=1,
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='black',
            borderwidth=1
        ),
        barmode='stack'  # Configuração para barras empilhadas
    )

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig4)


    # Gráfico 5 - Raio X das finanças

    fig5 = go.Figure()

    # Categorias para as barras empilhadas
    receitas = ['Crédito', 'Débito', 'Pix', 'Antecipação (crédito)', 'Cash', 'Receitas Financeiras (líquida)']
    custos_despesas = [
        'Custo c/ Taxas e Devoluções', 'Bebidas', 'Bomboniere', 'Cigarros', 'Diversos', 
        'Jornais', 'Livros', 'Revistas', 'Sorvetes', 'Tabacaria',
        'Equipe Operacional', 'Despesas c/ Imóvel', 'Despesas Administrativas', 'Despesas Tributárias'
    ]
    resultado = ['Resultado Líquido (caixa)']
    linhas_eixo_y2 = ['mgm bruta', 'mgm líquida']

    # Adicionando as receitas (primeira barra empilhada)
    for categoria in receitas:
        fig5.add_trace(go.Bar(
            x=df_transposto['Data'],
            y=df_transposto[categoria],
            name=categoria,
            offsetgroup=0,  # Primeira barra para cada mês
            legendgroup='Receitas',  # Agrupamento na legenda
            showlegend=True
        ))

    # Adicionando os custos/despesas (segunda barra empilhada com valores negativos)
    for categoria in custos_despesas:
        fig5.add_trace(go.Bar(
            x=df_transposto['Data'],
            y=-df_transposto[categoria],  # Invertendo para aparecer negativo no gráfico
            name=categoria,
            offsetgroup=1,  # Segunda barra para cada mês
            legendgroup='Custos/Despesas',  # Agrupamento na legenda
            showlegend=True
        ))

    # Adicionando o resultado líquido (terceira barra)
    fig5.add_trace(go.Bar(
        x=df_transposto['Data'],
        y=df_transposto['Resultado Líquido (caixa)'],
        name='Resultado Líquido (caixa)',
        offsetgroup=2,  # Terceira barra para cada mês
        marker_color='black',
        legendgroup='Resultado',
        showlegend=True
    ))

    # Adicionando as linhas no eixo Y secundário
    fig5.add_trace(go.Scatter(
        x=df_transposto['Data'],
        y=df_transposto['mgm bruta'],
        mode='lines+markers',
        name='mgm bruta',
        yaxis='y2',
        line=dict(color='red', width=2, dash='dash'),
        marker=dict(size=8),
        legendgroup='Margens'
    ))

    fig5.add_trace(go.Scatter(
        x=df_transposto['Data'],
        y=df_transposto['mgm líquida'],
        mode='lines+markers',
        name='mgm líquida',
        yaxis='y2',
        line=dict(color='blue', width=2, dash='dot'),
        marker=dict(size=8),
        legendgroup='Margens'
    ))

    # Configurando o layout com barras lado a lado e linhas no eixo Y secundário
    fig5.update_layout(
        title={
            'text': 'Receitas, Despesas e Resultado Líquido com MGM Bruta e Líquida',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis=dict(
            title='Data',
            tickmode='linear',
            dtick='M1',
            tickformat='%m/%Y'
        ),
        yaxis=dict(
            title='Valores (R$)'
        ),
        yaxis2=dict(
            title='MGM Bruta / Líquida',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            x=1.05,
            y=1,
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='black',
            borderwidth=1
        ),
        barmode='group',  # Empilhar as barras dentro de cada grupo
        bargap=0.3,  # Espaçamento entre os grupos de barras
        bargroupgap=0.1  # Espaçamento entre as barras dentro do mesmo mês
    )

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig5)


    # Gráfico 7 - Distribuição de Dividendos

    fig7 = go.Figure()

    # Lista das categorias de custo a serem empilhadas
    categorias_custo = [
        'Bruno Titus', 
        'Raphael Zay', 
        'Vicente Falcão', 
    ]

    # Adicionando cada categoria de custo como uma barra empilhada
    for categoria in categorias_custo:
        fig7.add_trace(go.Bar(
            x=df_transposto['Data'],
            y=df_transposto[categoria],
            name=categoria
        ))

    # Configurando o layout com barras empilhadas
    fig7.update_layout(
        title={
            'text': 'Distribuição de Dividendos',
            'x': 0.5,  # Centraliza o título
            'xanchor': 'center'
        },
        xaxis=dict(
            title='Data',
            tickmode='linear',
            dtick='M1',
            tickformat='%m/%Y'
        ),
        yaxis=dict(
            title='Total (R$)'
        ),
        legend=dict(
            x=1.05,  # Move a legenda para a direita para não cobrir o gráfico
            y=1,
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='black',
            borderwidth=1
        ),
        barmode='stack'  # Configuração para barras empilhadas
    )

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig7)