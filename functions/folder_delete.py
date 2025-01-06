import os
import shutil

def apagar_pasta(nome_pasta="uploads"):

    if os.path.exists(nome_pasta) and os.path.isdir(nome_pasta):
        shutil.rmtree(nome_pasta) 