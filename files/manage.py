import json
import shutil
import time
from pathlib import Path

from data import tools
from data.exceptions import FileNotFound
from lib.consts import *


def __get_conferencia_path(module, company_name=None):
    path = CONFERENCIA_PATH.replace(
        "MODULO",
        "FOLHA" if module == tools.modulos.FOLHA else "ADIANTAMENTO FOLHA",
    )
    return (
        path.replace("COMPANY", company_name)
        if company_name
        else path.replace("COMPANY", "")
    )


def __remove_files_from_conferencia_dir(destiny):
    # Verifica se o diretório existe
    path_exists(destiny)
    # Lista todos os arquivos no diretório
    arquivos_no_diretorio = os.listdir(destiny)

    # Itera sobre a lista de arquivos e exclui cada um deles
    for arquivo in arquivos_no_diretorio:
        caminho_completo = os.path.join(destiny, arquivo)
        if os.path.isfile(caminho_completo):
            try:
                os.unlink(caminho_completo)
                tools.console(f"ARQUIVO {caminho_completo} excluído com sucesso.")
            except Exception as e:
                tools.console(f"Erro ao excluir o ARQUIVO {caminho_completo}: {str(e)}")
        try:
            shutil.rmtree(caminho_completo)
            tools.console(f"PASTA {caminho_completo} excluído com sucesso.")
        except Exception as e:
            tools.console(f"Erro ao excluir a PASTA {caminho_completo}: {str(e)}")


def __send_to_conferencia(origin, company_name, file_name, module):
    conferencia_dir = __get_conferencia_path(module, company_name)
    new_conferencia_dir = tools.generate_new_file_suffix(
        conferencia_dir, file_name, module
    )

    path_exists(conferencia_dir)
    shutil.copy(origin, new_conferencia_dir)

    return f"Arquivo {conferencia_dir} enviado para CONFERÊNCIA"


def move_file(company_name, file_name, complete_path, module):
    try:
        destination_path = tools.generate_folder_path(company_name, file_name)
        destination_path = tools.generate_new_file_suffix(
            destination_path, file_name, module
        )
    except Exception as e:
        tools.console(f"{e}")
        return
    try:
        conferencia_text = __send_to_conferencia(
            complete_path, company_name, file_name, module
        )
        tools.console(conferencia_text)
        # Move o arquivo
        shutil.move(complete_path, destination_path)
        # Atualiza o dono do arquivo
        os.system(f"chown -R dev {destination_path}")

    except FileNotFoundError as e:
        raise FileNotFound(e)

    tools.console(f"Movido {file_name} para: {destination_path}")

    dicionario_export = {"file": file_name, "path": destination_path}
    return dicionario_export


def backup_files(module, clean_conferencia=False):
    path_exists(BACKUP_PATH)
    conferencia_dir = __get_conferencia_path(module)

    tools.prints_separator(message=f"EFETUANDO BACKUP - {module}")
    ##BACKUP
    for item in os.listdir(module.value):
        origin = os.path.join(module.value, item)
        dest = os.path.join(BACKUP_PATH, item)

        if os.path.isdir(origin):
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(origin, dest)
            tools.prints_separator(
                message=f"Copiado {origin} para {dest}", simples=True
            )
        else:  # Se não for um diretório, assumimos que é um arquivo
            shutil.copy2(origin, dest)
            tools.prints_separator(
                message=f"Copiado arquivo {origin} para {dest}", simples=True
            )
    if clean_conferencia:
        tools.prints_separator(message=f"LIMPANDO PASTA DE CONFERÊNCIA - {module}")
        ##CONFERENCIA FUNCTION
        __remove_files_from_conferencia_dir(conferencia_dir)


def path_exists(path):
    # Verificar se o diretório existe
    if not os.path.exists(path):
        # Se não existir, criar o diretório
        os.makedirs(path)
        tools.console(f'Diretório "{path}" criado com sucesso.\n')


def generate_report_file(
    list_object: list, name, ctx_path=Path(__file__).parent.parent, json_file=False
):
    path = f"{ctx_path}/output/{name}"
    if not json_file:
        with open(f"{path}.txt", "w") as file:
            for text in list_object:
                file.write(text + "\n")
    else:
        with open(f"{path}.json", "w") as file:
            json.dump(list_object, file)
