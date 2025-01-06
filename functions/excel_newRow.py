import pandas as pd
from openpyxl import load_workbook


def new_last_row(file_path, sheet_name, new_data):

    # Carregar a aba em um DataFrame
    excel_data = pd.read_excel(file_path, sheet_name=sheet_name)

    # Converter a nova linha para um DataFrame
    new_row_df = pd.DataFrame([new_data])
    
    # Adicionar a nova linha ao DataFrame existente
    updated_data = pd.concat([excel_data, new_row_df], ignore_index=True)

    # Escrever os dados atualizados de volta à planilha
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        updated_data.to_excel(writer, sheet_name=sheet_name, index=False)





