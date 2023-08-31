import json
import shutil
from pathlib import Path

from data import tools
from data.consts import *
from data.exceptions import FileNotFound


def move_file(company_name, file_name, complete_path):
    destination_path = tools.generate_folder_path(company_name, file_name)
    destination_path = tools.generate_new_file_suffix(destination_path, file_name)
    try:
        shutil.move(complete_path, destination_path)
    except FileNotFoundError as e:
        raise FileNotFound(e)

    text = f"\nMovido {file_name} para: \n{destination_path}\n"
    print(text)

    dicionario_export = {"file": file_name, "path": destination_path}
    return dicionario_export


def backup_files(type_of_event):
    tools.path_exists(BACKUP_PATH)

    for item in os.listdir(type_of_event):
        origin = os.path.join(type_of_event, item)
        dest = os.path.join(BACKUP_PATH, item)

        if os.path.isdir(origin):
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(origin, dest)
            print(f"\nCopiado {origin} para {dest}\n")
        else:  # Se não for um diretório, assumimos que é um arquivo
            shutil.copy2(origin, dest)
            print(f"\nCopiado arquivo {origin} para {dest}\n")

    # Imprimir o separador no final
    print("/" * 10 + "*" * 30 + "/" * 10)


def generate_report_file(
    list_object: list, name, ctx_path=Path(__file__).parent.parent, json_file=False
):
    if not json_file:
        with open(f"{ctx_path}/output/{name}.txt", "w") as file:
            for text in list_object:
                file.write(text + "\n")
    else:
        with open(f"{ctx_path}/output/{name}.json", "w") as file:
            json.dump(list_object, file)
