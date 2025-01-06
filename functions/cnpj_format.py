import re
import streamlit as st
   
def formatar_cnpj(cnpj):
    
    cnpj_formatado = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj_formatado