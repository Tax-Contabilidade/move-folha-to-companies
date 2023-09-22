import os
import shutil

from files.manage import path_exists
from lib.consts import CONFERENCIA_PATH, LOCAL_SERVER_PATH

emp_file = open("empresas.txt", "r")
period_suffix = "/PESSOAL/01 - FOLHAS E MOVIMENTACOES/2023/09 - setembro"
root_dir = f"{LOCAL_SERVER_PATH}/EMPRESAS/$EMP$/{period_suffix}"
conferencia_dir = CONFERENCIA_PATH

for line in emp_file:
    emp_folder = root_dir.replace("$EMP$", line.strip())
    conferencia_folder = conferencia_dir.replace("MODULO", "FOLHA").replace(
        "COMPANY", line.strip()
    )

    path_exists(conferencia_folder)

    for file in os.listdir(emp_folder):
        if file.endswith(".pdf"):
            shutil.copy(
                os.path.join(emp_folder, file), os.path.join(conferencia_folder, file)
            )
            print(
                "Copiando: {} \nde {} \npara {}".format(
                    file, line.strip(), conferencia_folder
                )
            )


emp_file.close()
