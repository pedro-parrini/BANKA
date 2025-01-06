import re
import streamlit as st

def validar_cnpj(cnpj):

    # Remove quaisquer caracteres que não sejam números
    cnpj = re.sub(r'\D', '', cnpj)
    
    # Verifica se o CNPJ possui 14 dígitos
    if len(cnpj) != 14:
        st.error("CNPJ inválido: Deve conter 14 dígitos.")
    
    # Função auxiliar para cálculo dos dígitos verificadores
    def calcular_digito(cnpj_parcial, pesos):
        soma = sum(int(digito) * peso for digito, peso in zip(cnpj_parcial, pesos))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    # Verifica os dois dígitos verificadores
    pesos_primeiro = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_segundo = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    primeiro_digito = calcular_digito(cnpj[:12], pesos_primeiro)
    segundo_digito = calcular_digito(cnpj[:12] + primeiro_digito, pesos_segundo)
    
    if cnpj[-2:] != primeiro_digito + segundo_digito:
        st.error("CNPJ inválido: Dígitos verificadores não conferem.")
    