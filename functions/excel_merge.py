import pandas as pd
from openpyxl import load_workbook

# Passar as infos das 3 planilhas para a planilha principal

# Retirar os cancelamentos da planilha principal

def remove_id(planilha_gerencial, excel_cancelamentos):

    # Lista com todos os IDs para remover
    wrong_ids = list(pd.read_excel(excel_cancelamentos, sheet_name="Cancelar IDs"))

    for i in wrong_ids:

        # Carregar os dados da aba no DataFrame
        df = pd.read_excel(planilha_gerencial, sheet_name="Controle de NFs Tomadas")

        # Filtrar as linhas onde o ID não é igual ao especificado
        try:

            df_filtered = df[df['ID number'] != i]
        
        except:
            pass

        # Escrever os dados filtrados de volta para a aba
        with pd.ExcelWriter(planilha_gerencial, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_filtered.to_excel(writer, sheet_name="Controle de NFs Tomadas", index=False)

def delete_df_rows(excel_path, sheet_name):

    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    df = df.drop(df.index)

    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

def excel_merge(excel_bg, excel_tjk, excel_sc, excel_cancelamentos, planilha_gerencial):

    bankas = [excel_bg, excel_tjk, excel_sc]

    for i in bankas:

        excel_data = pd.read_excel(planilha_gerencial, sheet_name="Controle de NFs Tomadas")

        new_df = pd.read_excel(i, sheet_name="Controle de NFs Tomadas")
 
        updated_data = pd.concat([excel_data, new_df], ignore_index=True)

        with pd.ExcelWriter(planilha_gerencial, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            updated_data.to_excel(writer, sheet_name="Controle de NFs Tomadas", index=False)

        delete_df_rows(i, "Controle de NFs Tomadas")
    
    remove_id(planilha_gerencial, excel_cancelamentos)

    delete_df_rows(excel_cancelamentos, "Cancelar IDs")



