import argparse
import enum
import os
import re
import sys
from datetime import datetime
from typing import Union

import pandas as pd

import data.consts as consts
from data.exceptions import CompanyNotFound


class modulos(enum.Enum):
    FOLHA = consts.FOLHA_FOLDER_PATH
    ADIANTAMENTO_FOLHA = consts.ADIANT_FOLHA_FOLDER_PATH


def get_args_from_command_line():
    parser = argparse.ArgumentParser(
        description="Um script para processar e salvar os arquivos de Folha e Adiantamento de Folha nas empresas corretamente"
    )

    # Adicione os argumentos que você deseja aceitar
    parser.add_argument("-f", "--folha", action="store_true", help="Processar a folha")
    parser.add_argument(
        "-u",
        "--no-umount",
        action="store_true",
        help="Não desmonta o servidor após conclusão",
    )
    parser.add_argument(
        "-a", "--adiant", action="store_true", help="Processar o adiantamento"
    )

    args = parser.parse_args()

    if args.folha and args.adiant:
        print(
            "\nErro: Não use os flags -f e -a juntas. Ainda não há suporte para a execução dos módulos FOLHA e ADIANTAMENTO_FOLHA simultaneamente"
        )
        sys.exit(1)

    return args


def generate_folder_path(company_name, company_file, specific_month=False, month=None):
    if specific_month:
        if not month:
            raise Exception("Month not informed")

        if month == datetime.now().month:
            date = consts.CURRENT_DATE_SUFIX_PATH
        else:
            date = datetime(year=datetime.now().year, month=month, day=1).strftime(
                "%Y/%m - %B"
            )

        return "{}/{}/{}".format(
            consts.COMPANIES_PATH,
            company_name,
            consts.DESTINATION_SUFIX_PATH.replace("{DATE}", date),
        )

    # Padrão de regex para capturar o mês e o ano
    if company_file[:13] == "GuiaPagamento":
        pattern = r"_(\d{2})(\d{4})_"
    else:
        pattern = r"(\d{2})(\d{4}).pdf"

    match = re.search(pattern, company_file)
    if match:
        month = int(match.group(1))
        year = int(match.group(2))
        date = datetime(year, month, 1).strftime("%Y/%m - %B")
    else:
        raise Exception("Pattern not found on this file")

    return "{}/{}/{}".format(
        consts.COMPANIES_PATH,
        company_name,
        consts.DESTINATION_SUFIX_PATH.replace("{DATE}", date),
    )


def __get_dataframe(excel_file_path):
    df = pd.read_excel(excel_file_path)
    df.drop(
        columns=[
            "Procedimento",
            "Est",
            "Pro-Labore",
            "E-mail",
            "Responsavel",
            "Codigo De Acesso",
            "Senha",
            "Domesticas",
            "Mei",
            "Lotacao",
            "Certificado",
            "Quant-est",
            "Excluir",
            "Calculo",
            "Listagem De Pagamento",
            "Recibo",
            "Controle de Frequencia",
            "Abrir Competencia",
            "Fechar Competencia",
            "Dctf-web",
            "Enviar E-mail",
            "Adiantamento De Folha",
            "Recibo De Adiantamento",
            "Recibo De Adiantamento",
            "Data Adiantamento",
            "Envio Da Folha De Adiantamento",
            "TIPO",
            "MOVIMENTACAO",
        ],
        inplace=True,
    )
    df.reset_index(inplace=True, drop=True)
    df = df.astype(str)
    # df["Cod"] = df["Cod"].apply(lambda x: re.sub("0", "", x))
    df["Cod"] = df["Cod"].apply(lambda x: x.lstrip("0"))

    return df


def __get_companies_list(df):
    return [
        {"name": reg["Caminho"].split("\\")[-1], "cod": reg["Cod"], "cnpj": reg["Cnpj"]}
        for index, reg in df.iterrows()
    ]


def get_companies_list(
    excel_file_path="{}/empresas.xlsx".format(os.getcwd()),
) -> pd.DataFrame:
    df = __get_dataframe(excel_file_path)

    return df.from_dict(__get_companies_list(df))


def get_company_name_by_cod(df, cod: Union[str, int]):
    filtered_line = df.loc[df["cod"] == cod, "name"].values

    if len(filtered_line) > 0:
        return filtered_line[0]
    else:
        raise CompanyNotFound("Company not found")


def __extract_cnpj_from_filename(df, filename):
    cnpj_pattern = r"\d{14}"
    match = re.search(cnpj_pattern, filename)
    if match:
        cnpj = match.group()
        filtered_line = df.loc[df["cnpj"] == cnpj.lstrip("0"), "cod"].values
        if len(filtered_line) > 0:
            return filtered_line[0]
    else:
        raise CompanyNotFound("Company not found")


def get_company_cod_by_filename(df, company_name: str):
    # Definindo o padrão de regex para capturar a sequência de números antes do hífen
    pattern = r"(\d+)-"

    # Encontrando o padrão na string
    cod_found = re.search(pattern, company_name)

    if cod_found:
        return cod_found.group(1)
    elif company_name[:13] == "GuiaPagamento":
        return __extract_cnpj_from_filename(df, company_name)

    raise Exception("Pattern not found on this file")


def __parse_date(date_str):
    year = date_str[-4:]
    month = date_str[:2]
    return f"{month} - {year}"


def __rename_file(filename):
    if "Extrato" in filename:
        new_name = "Extrato.pdf"
    elif any(name in filename for name in ["DAE", "Dae"]):
        match = re.search(r"(\d{6})", filename)
        new_name = "DAE - {}.pdf".format(__parse_date(match.group(1)))
    elif any(name in filename for name in ["Férias", "Ferias", "ferias"]):
        new_name = "Programação de férias - 0001.pdf"
    elif any(name in filename for name in ["Folha", "folha"]):
        new_name = "Folha de Pagamento - 0001.pdf"
    elif "Recibo" in filename:
        new_name = "Recibo de Pagamento - 0001.pdf"
    else:
        new_name = filename

    return new_name


def generate_new_file_suffix(destination_path, file_name):
    new_file_name = __rename_file(file_name)

    return os.path.join(destination_path, new_file_name)
