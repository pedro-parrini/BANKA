import os
import shutil

def criar_pasta(nome_pasta="uploads"):

    os.makedirs(nome_pasta, exist_ok=True)