import json
import shutil
from pathlib import Path

from data import tools
from data.exceptions import FileNotFound
from lib.consts import *


def __get_conferencia_path(module):
    return CONFERENCIA_PATH.replace(
        "MODULO", "FOLHA" if module == tools.modulos.FOLHA else "ADIANTAMENTO FOLHA"
    )


def __remove_files_from_conferencia_dir(destiny):
    # Verifica se o diretório existe
    tools.path_exists(destiny)
    # Lista todos os arquivos no diretório
    arquivos_no_diretorio = os.listdir(destiny)

    # Itera sobre a lista de arquivos e exclui cada um deles
    for arquivo in arquivos_no_diretorio:
        caminho_completo = os.path.join(destiny, arquivo)
        try:
            os.unlink(caminho_completo)
            print(f"Arquivo {caminho_completo} excluído com sucesso.")
        except Exception as e:
            print(f"Erro ao excluir o arquivo {caminho_completo}: {str(e)}")


def __send_to_conferencia(origin, file_name, module):
    conferencia_dir = __get_conferencia_path(module)
    conferencia_dir = tools.generate_new_file_suffix(conferencia_dir, file_name, module)

    shutil.copy2(origin, conferencia_dir)
    print(f"\nCopiado arquivo {origin} para {conferencia_dir}")


def move_file(company_name, file_name, complete_path, module):
    try:
        destination_path = tools.generate_folder_path(company_name, file_name)
        destination_path = tools.generate_new_file_suffix(
            destination_path, file_name, module
        )
    except Exception as e:
        print(f"\n{e}\n")
        return
    try:
        __send_to_conferencia(complete_path, file_name, module)
        shutil.move(complete_path, destination_path)
    except FileNotFoundError as e:
        raise FileNotFound(e)

    text = f"\nMovido {file_name} para: \n{destination_path}\n"
    print(text)

    dicionario_export = {"file": file_name, "path": destination_path}
    return dicionario_export


def backup_files(module):
    tools.path_exists(BACKUP_PATH)
    conferencia_dir = __get_conferencia_path(module)

    tools.prints_separator(message=f"EFETUANDO BACKUP - {module}\n\n")
    ##BACKUP
    for item in os.listdir(module):
        origin = os.path.join(module, item)
        dest = os.path.join(BACKUP_PATH, item)

        if os.path.isdir(origin):
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(origin, dest)
            print(f"\nCopiado {origin} para {dest}\n")
        else:  # Se não for um diretório, assumimos que é um arquivo
            shutil.copy2(origin, dest)
            print(f"\nCopiado arquivo {origin} para {dest}\n")

    tools.prints_separator(message=f"LIMPANDO PASTA DE CONFERENCIA - {module}\n\n")
    ##CONFERENCIA
    __remove_files_from_conferencia_dir(conferencia_dir)


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
