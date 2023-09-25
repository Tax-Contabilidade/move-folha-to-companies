import os
import shutil

from files.manage import path_exists
from lib.consts import CONFERENCIA_PATH, LOCAL_SERVER_PATH

emp_file = open("empresas.txt", "r")
period_suffix = "/PESSOAL/01 - FOLHAS E MOVIMENTACOES/2023/09 - setembro"
root_dir = f"{LOCAL_SERVER_PATH}/EMPRESAS/$EMP$/{period_suffix}"
conferencia_dir = CONFERENCIA_PATH


def copy_file(file, empresa, complete_path=None):
    origin_path = complete_path if complete_path else os.path.join(emp_folder, file)

    if file.endswith(".pdf"):
        shutil.copy(origin_path, os.path.join(conferencia_folder, file))
        print(
            "\nCopiando: {} \nde {} \npara {}".format(file, empresa, conferencia_folder)
        )


for line in emp_file:
    emp_folder = root_dir.replace("$EMP$", line.strip())
    conferencia_folder = conferencia_dir.replace("MODULO", "FOLHA").replace(
        "COMPANY", line.strip()
    )

    path_exists(conferencia_folder)

    for file in os.listdir(emp_folder):
        if file == "DCTFWeb":
            inss_folder = os.path.join(emp_folder, file)
            for inss_file in os.listdir(inss_folder):
                copy_file(
                    inss_file,
                    line.strip(),
                    complete_path=os.path.join(inss_folder, inss_file),
                )
        # else:
        #     copy_file(file, empresa=line.strip())

emp_file.close()
