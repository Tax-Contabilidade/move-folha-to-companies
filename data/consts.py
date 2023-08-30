import os
from datetime import datetime

SUDO_PASSWD = "dev@123"
DESTINATION_SUFIX_PATH = "PESSOAL/01 - FOLHAS E MOVIMENTACOES/{DATE}"
CURRENT_DATE_SUFIX_PATH = datetime.now().strftime("%Y/%m - %B")
LOCAL_SERVER_PATH = "{}/server".format(os.path.expanduser("~"))
ADIANT_FOLHA_FOLDER_PATH = "{}/AUTOMAÇÕES/PESSOAL/FOLHA ADIANTAMENTO".format(
    LOCAL_SERVER_PATH
)
FOLHA_FOLDER_PATH = "{}/programacao/SETOR PESSOAL/FILES".format(LOCAL_SERVER_PATH)
COMPANIES_PATH = "{}/EMPRESAS".format(LOCAL_SERVER_PATH)
BACKUP_PATH = r"{}/AUTOMAÇÕES/PESSOAL/BACKUP/{}/".format(
    LOCAL_SERVER_PATH, datetime.now().strftime("%d-%m-%Y")
)
