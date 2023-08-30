import locale
import os

from data import tools
from data.consts import *
from data.exceptions import CompanyNotFound, FileNotFound
from files.manage import (
    backup_files,
    generate_report_file,
    mount_server,
    move_file,
    umount_server,
)

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
companies = tools.get_companies_list()
companies_not_found = []
companies_moved = []


def config_server_and_backup(type_of_event):
    mount_server()
    # backup_files(type_of_event)


def main(companies, success_list, error_list, modulo: tools.Modulos):
    config_server_and_backup(
        modulo.value
    )  # FOLHA_FOLDER_PATH or ADIANT_FOLHA_FOLDER_PATH

    for file_name in os.listdir(modulo.value):
        complete_path = os.path.join(modulo.value, file_name)
        if os.path.isfile(complete_path):
            company_cod = tools.get_company_cod_by_filename(companies,file_name)
            company_name = tools.get_company_name_by_cod(companies, company_cod)

            try:
                file_text = move_file(company_name, file_name, complete_path)
                success_list.append(file_text)

            except (CompanyNotFound, FileNotFound) as e:
                text = "{}\n{}".format((company_name, file_name), e)
                error_list.append(text)

    generate_report_file(success_list, "movidos", json_file=True)
    generate_report_file(error_list, "erros", json_file=False)

    umount_server()


if __name__ == "__main__":
    args = tools.get_args_from_command_line()
    if args.adiant:
        print("Executando módulo ADIANTAMENTO DE FOLHA...")
        main(
            companies, companies_moved, companies_not_found, tools.Modulos.ADIANT_FOLHA
        )

    print("Executando módulo FOLHA DE PAGAMENTO...")
    main(companies, companies_moved, companies_not_found, tools.Modulos.FOLHA)
