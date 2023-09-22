import locale
import os

from data import tools
from data.exceptions import CompanyNotFound, FileNotFound
from files.manage import generate_report_file, move_file
from lib.settings import (
    end_application,
    get_args_from_command_line,
    init_setup,
    restart_application,
)

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
companies = tools.get_companies_list()
companies_not_found = []
companies_moved = []


def main(companies, success_list, error_list, modulo: tools.modulos, umount=True):
    tools.prints_separator(message="INICIO APLICAÇÃO: Movendo Arquivos...")
    for file_name in os.listdir(modulo.value):
        complete_path = os.path.join(modulo.value, file_name)
        if os.path.isfile(complete_path):
            company_cod = tools.get_company_cod_by_filename(companies, file_name)
            company_name = tools.get_company_name_by_cod(companies, company_cod)

            try:
                file_text = move_file(company_name, file_name, complete_path, modulo)
                success_list.append(file_text)

            except (CompanyNotFound, FileNotFound) as e:
                text = "{}\n{}".format((company_name, file_name), e)
                tools.console(message=text, simples=True)
                error_list.append(text)

    generate_report_file(success_list, "movidos", json_file=True)
    generate_report_file(error_list, "erros", json_file=False)

    if umount:
        end_application()


def execute_module(**kwargs):
    modulo = kwargs["modulo"]
    needs_restart = init_setup(modulo, kwargs["clean_conferencia"])

    if needs_restart:
        return True

    ##--
    main(**kwargs)


if __name__ == "__main__":
    args = get_args_from_command_line()
    umount_flag = not args.no_umount

    needs_restart = execute_module(
        umount=umount_flag,
        companies=companies,
        success_list=companies_moved,
        error_list=companies_not_found,
        modulo=tools.modulos.ADIANTAMENTO_FOLHA if args.adiant else tools.modulos.FOLHA,
        clean_conferencia=args.clean,
    )

    if needs_restart:
        tools.prints_separator(message="UPDATE DA APLICAÇÃO: Reiniciando Servidor...")
        restart_application()
