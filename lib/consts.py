import os
import socket
from datetime import datetime
from pathlib import Path

SUDO_PASSWD = "dev@123"
REPO_CWD = Path(__file__).parent.parent
IS_RUN_IN_SERVER = socket.getfqdn() == "servidor"
DESTINATION_SUFIX_PATH = "PESSOAL/01 - FOLHAS E MOVIMENTACOES/{DATE}"
CURRENT_DATE_SUFIX_PATH = datetime.now().strftime("%Y/%m - %B")
LOCAL_SERVER_PATH_SUFIX = "server" if not IS_RUN_IN_SERVER else "/hd/server"
LOCAL_SERVER_PATH = "{}/{}".format(os.path.expanduser("~"), LOCAL_SERVER_PATH_SUFIX)
ADIANT_FOLHA_FOLDER_PATH = "{}/AUTOMAÇÕES/PESSOAL/FOLHA ADIANTAMENTO".format(
    LOCAL_SERVER_PATH
)
FOLHA_FOLDER_PATH = "{}/AUTOMAÇÕES/PESSOAL/FOLHA MENSAL".format(LOCAL_SERVER_PATH)
COMPANIES_PATH = "{}/EMPRESAS".format(LOCAL_SERVER_PATH)
BACKUP_PATH = r"{}/AUTOMAÇÕES/PESSOAL/BACKUP/{}/".format(
    LOCAL_SERVER_PATH, datetime.now().strftime("%d-%m-%Y")
)
CONFERENCIA_PATH = f"{LOCAL_SERVER_PATH}/AUTOMAÇÕES/PESSOAL/CONFERENCIA/MODULO"
