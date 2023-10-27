import enum
import os
import re
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Union

import pandas as pd

import lib.consts as consts
from data import tools
from data.exceptions import CompanyNotFound, FileNotFound
from lib.patterns import ADIANTAMENTO_FOLHA_PATTERN, FOLHA_PATTERN


class modulos(enum.Enum):
    FOLHA = consts.FOLHA_FOLDER_PATH
    ADIANTAMENTO_FOLHA = consts.ADIANT_FOLHA_FOLDER_PATH


def __get_dataframe(excel_file_path):
    df = pd.read_excel(excel_file_path, dtype=str)
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
    # df = df.astype(str)
    # df["Cod"] = df["Cod"].apply(lambda x: re.sub("0", "", x))
    df["Cod"] = df["Cod"].apply(lambda x: x.lstrip("0"))

    return df


def __get_companies_list(df):
    return [
        {"name": reg["Caminho"].split("\\")[-1], "cod": reg["Cod"], "cnpj": reg["Cnpj"]}
        for index, reg in df.iterrows()
    ]


def __extract_cnpj_from_filename(df, filename):
    # CASO EXCEPCIONAL DO EXCELENTÍSSIMO DR RODRIGO
    if "512150123302" in filename:
        return 195

    cnpj_pattern = r"\d{14}"
    match = re.search(cnpj_pattern, filename)
    if match:
        cnpj = match.group()
        # print(df.info())
        # for cnpj_df in df["cnpj"].values:
        #     print(cnpj, cnpj_df)
        #     if cnpj in cnpj_df:
        #         time.sleep(50)
        filtered_line = df.loc[df["cnpj"] == cnpj, "cod"].values
        # filtered_line = df.loc[df["cnpj"].isin([cnpj]), "cod"].values
        if len(filtered_line) > 0:
            return filtered_line[0]
        elif len(filtered_line) <= 0:
            raise CompanyNotFound("Company not found by CNPJ: {}".format(cnpj))
    else:
        raise CompanyNotFound(
            f"CNPJ ou COD da empresa não foi encontrado: \nFILENAME:{filename}"
        )


def __parse_date(date_str):
    year = date_str[-4:]
    month = date_str[:2]
    return f"{month} - {year}"


def __rename_file(filename, module):
    def rename_with_date(template, date):
        return template.replace("{date}", __parse_date(date))

    patterns = (
        ADIANTAMENTO_FOLHA_PATTERN
        if module == tools.modulos.ADIANTAMENTO_FOLHA
        else FOLHA_PATTERN
    )

    for patterns_list, template in patterns:
        if any(pattern in filename for pattern in patterns_list):
            if "DAE" in patterns_list:
                match = re.search(r"(\d{6})", filename)
                if match:
                    return rename_with_date(template, match.group(1))
            elif any(word in filename for word in ["folha", "freq"]):
                match = re.search(r"(\d{4})", filename)
                if match:
                    return template.replace("{EST}", match.group(1))
                else:
                    raise FileNotFound(
                        f"Pattern not found on this file\n FILENAME: {filename}"
                    )
            else:
                return template

    return filename


def console(message, tab=True):
    indented_message = textwrap.indent(message, "    ") if tab else message
    message = "{}{}\n".format("\n" if tab else "", indented_message)

    print(message)
    return message


def prints_separator(message=None, simples=False):
    # Imprimir o separador no final
    print("/" * 10 + "*" * 30 + "/" * 10) if not simples else print("--" * 20)
    if message:
        console("{}".format(message), tab=True if simples else False)


def generate_new_file_suffix(destination_path, file_name, module):
    new_file_name = __rename_file(file_name, module)

    return os.path.join(destination_path, new_file_name)


def get_companies_list(
    excel_file_path="{}".format(
        os.path.join(Path(__file__).parent, "api/empresas.xlsx")
    ),
) -> pd.DataFrame:
    df = __get_dataframe(excel_file_path)
    return df.from_dict(__get_companies_list(df))


def get_company_cod_by_filename(df, company_name: str):
    # Definindo o padrão de regex para capturar a sequência de números antes do hífen
    pattern = r"(\d+)-"

    # Encontrando o padrão na string
    cod_found = re.search(pattern, company_name)

    if cod_found:
        return cod_found.group(1)
    elif any(doc_type in company_name for doc_type in ["GuiaPagamento", "GRF", "grf"]):
        return __extract_cnpj_from_filename(df, company_name)

    raise Exception(f"Pattern not found on this file\n FILENAME: {company_name}")


def get_company_name_by_cod(df, cod: Union[str, int]):
    filtered_line = df.loc[df["cod"] == cod, "name"].values

    if len(filtered_line) > 0:
        return filtered_line[0]
    else:
        raise CompanyNotFound("Company not found - cod: {}".format(cod))


def generate_folder_path(company_name, company_file, specific_month=False, month=None):
    is_guia_pagamento = "GuiaPagamento" in company_file
    is_grf = any(doc_type in company_file for doc_type in ["Grf", "GRF"])
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
    if is_guia_pagamento:
        pattern = r"_(\d{2})(\d{4})_"
        output_path = "{}/{}/{}/DCTFWeb".format(
            consts.COMPANIES_PATH,
            company_name,
            consts.DESTINATION_SUFIX_PATH,
        )
    elif is_grf:
        pattern = "NÃO TEM"
        output_path = "{}/{}/{}".format(
            consts.COMPANIES_PATH,
            company_name,
            consts.DESTINATION_SUFIX_PATH,
        )
    else:
        pattern = (
            r"(\d{2})(\d{4}).pdf"
            if not "DAE" in company_file
            else r"(\d{2})(\d{4}).PDF"
        )
        output_path = "{}/{}/{}".format(
            consts.COMPANIES_PATH,
            company_name,
            consts.DESTINATION_SUFIX_PATH,
        )

    match = re.search(pattern, company_file)
    if match:
        month = int(match.group(1))
        year = int(match.group(2))
        date = datetime(year, month, 1).strftime("%Y/%m - %B")
    else:
        if not is_grf:
            raise Exception("Pattern not found on this file")

        date = consts.CURRENT_DATE_SUFIX_PATH

    return output_path.replace("{DATE}", date)
