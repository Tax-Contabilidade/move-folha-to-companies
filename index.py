import locale
import os

from data import tools
from data.consts import *
from data.exceptions import CompanyNotFound, FileNotFound
from files.manage import backup_files, mount_server, move_file, unmount_server

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
companies = tools.get_companies_list()
companies_not_found = []
companies_moved = []


def generate_report_file(list_object: list, name, json=False):
    if not json:
        with open(f"{os.getcwd()}/output/{name}.txt", "w") as file:
            for text in list_object:
                file.write(text + "\n")


def config_server_and_backup(type_of_event):
    mount_server()
    backup_files(type_of_event)
    # tools.umount_server()


def main(companies, success_list, error_list):
    for file_name in os.listdir(FOLHA_FOLDER_PATH):
        complete_path = os.path.join(FOLHA_FOLDER_PATH, file_name)
        if os.path.isfile(complete_path):
            company_cod = tools.get_company_cod_by_filename(file_name)
            company_name = tools.get_company_name_by_cod(companies, company_cod)

            try:
                file_text = move_file(company_name, file_name, complete_path)
                success_list.append(file_text)

            except (CompanyNotFound, FileNotFound) as e:
                text = "{}\n{}".format((company_name, file_name), e)
                error_list.append(text)

    generate_report_file(success_list, "movidos")
    generate_report_file(error_list, "erros")


if __name__ == "__main__":
    config_server_and_backup(FOLHA_FOLDER_PATH)  # or ADIANT_FOLHA_FOLDER_PATH
    main(companies, companies_moved, companies_not_found)
