import os
import shutil

def limpar_pasta(pasta):
    
    # Limpar todos os arquivos da pasta uploads
    for filename in os.listdir(pasta):
        file_path = os.path.join(pasta, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  # Remove arquivo ou link
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # Remove diretório


