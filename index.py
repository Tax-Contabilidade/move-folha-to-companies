import locale
import os

from data import tools
from data.consts import *
from data.exceptions import CompanyNotFound, FileNotFound
from files.manage import (
    backup_files,
    check_for_updates,
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
    backup_files(type_of_event)


def main(companies, success_list, error_list, modulo: tools.modulos, umount=True):
    config_server_and_backup(modulo.value)

    for file_name in os.listdir(modulo.value):
        complete_path = os.path.join(modulo.value, file_name)
        if os.path.isfile(complete_path):
            company_cod = tools.get_company_cod_by_filename(file_name)
            company_name = tools.get_company_name_by_cod(companies, company_cod)

            try:
                file_text = move_file(company_name, file_name, complete_path)
                success_list.append(file_text)

            except (CompanyNotFound, FileNotFound) as e:
                text = "{}\n{}".format((company_name, file_name), e)
                error_list.append(text)

    generate_report_file(success_list, "movidos", json_file=True)
    generate_report_file(error_list, "erros", json_file=False)

    if umount:
        umount_server()


def execute_module(**kwargs):
    check_for_updates()

    print(f"Executando módulo {kwargs['modulo']}...")
    main(**kwargs)


if __name__ == "__main__":
    args = tools.get_args_from_command_line()
    umount_flag = not args.no_umount

    if args.adiant:
        execute_module(
            umount=umount_flag,
            companies=companies,
            success_list=companies_moved,
            error_list=companies_not_found,
            modulo=tools.modulos.ADIANTAMENTO_FOLHA,
        )
    else:
        execute_module(
            umount=umount_flag,
            companies=companies,
            success_list=companies_moved,
            error_list=companies_not_found,
            modulo=tools.modulos.FOLHA,
        )
