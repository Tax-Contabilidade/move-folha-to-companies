import os
import shutil
import time
from datetime import datetime

from files.manage import path_exists, resolve_permissions_conflicts
from lib.consts import CONFERENCIA_PATH, LOCAL_SERVER_PATH

emp_file = open("empresas.txt", "r")
date = datetime.now()
period_suffix = (
    f"/PESSOAL/01 - FOLHAS E MOVIMENTACOES/{date.year}/{date.strftime('%m - %B')}"
)
root_dir = f"{LOCAL_SERVER_PATH}/EMPRESAS/$EMP$/{period_suffix}"
conferencia_dir = CONFERENCIA_PATH


def generate_empresas_txt(modulo_conferencia_path):
    with open("empresas.txt", "w") as file:
        file.truncate(0)
        for company in os.listdir(modulo_conferencia_path):
            file.write(company + "\n")


def copy_file(file, empresa, complete_path=None):
    origin_path = (
        complete_path if complete_path else os.path.join(emp_server_folder, file)
    )

    if file.endswith(".pdf"):
        shutil.copy(origin_path, os.path.join(company_conferencia_folder, file))
        print(
            "\nCopiando: {} \nde {} \npara {}".format(
                file, empresa, company_conferencia_folder
            )
        )


for emp_name in emp_file:
    emp_server_folder = root_dir.replace("$EMP$", emp_name.strip())
    all_conferencia_folder = conferencia_dir.replace("MODULO", "FOLHA")
    conferencia_folder = all_conferencia_folder.replace("COMPANY/", "")
    company_conferencia_folder = all_conferencia_folder.replace(
        "COMPANY", emp_name.strip()
    )
    #
    generate_empresas_txt(conferencia_folder)
    #
    path_exists(company_conferencia_folder)
    #
    resolve_permissions_conflicts(conferencia_folder)
    #
    for file in os.listdir(emp_server_folder):
        # Verifica se é diretório
        if not os.path.isdir(os.path.join(emp_server_folder)):
            continue

        if file == "DCTFWeb":
            inss_folder = os.path.join(emp_server_folder, file)
            for inss_file in os.listdir(inss_folder):
                copy_file(
                    inss_file,
                    emp_name.strip(),
                    complete_path=os.path.join(inss_folder, inss_file),
                )
        else:
            copy_file(file, empresa=emp_name.strip())

emp_file.close()
