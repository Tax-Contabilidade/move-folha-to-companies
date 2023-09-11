import argparse
import errno
import subprocess
import sys
import time
from datetime import timedelta

from data.tools import console, path_exists, prints_separator
from files.manage import backup_files
from lib.consts import *


def __is_server_mounted(directory_path):
    try:
        # Execute o comando "mount" e capture a saída
        output = subprocess.check_output(["mount"], text=True, cwd=REPO_CWD)

        # Verifique se o caminho do diretório está na saída
        if directory_path in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        # Lidar com erros ao executar o comando
        return False


def __is_tool_available(name):
    """Verifica se uma ferramenta específica está disponível no sistema."""
    try:
        devnull = open(os.devnull)
        subprocess.Popen(
            [name], stdout=devnull, stderr=devnull, cwd=REPO_CWD
        ).communicate()
    except OSError as e:
        if e.errno == errno.ENOENT:
            return False
    return True


def __install_sshfs():
    """Instala o sshfs usando o gerenciador de pacotes apt."""
    console(
        "\nSSHFS não encontrado! Isto é necessário para montar o diretário remoto. Tentando instalar...\n"
    )
    time.sleep(5)
    try:
        subprocess.run(
            ["sudo", "apt", "install", "-y", "sshfs"], check=True, cwd=REPO_CWD
        )
    except subprocess.CalledProcessError:
        console(
            "Erro ao atualizar ou instalar o sshfs. Por favor, tente manualmente.\n\nUSE: 'sudo apt update && sudo apt-get install sshfs'"
        )
        sys.exit(1)


def __manage_last_stash():
    try:
        # Verificar se há stashes
        stash_list = (
            subprocess.check_output(["git", "stash", "list"], cwd=REPO_CWD)
            .decode()
            .strip()
            .split("\n")
        )

        if stash_list:
            last_stash_entry = stash_list[0]
            stash_info = last_stash_entry.split(": ")
            stash_name = stash_info[0]
            stash_message = (
                stash_info[1] if len(stash_info) > 1 else "Mensagem não disponível"
            )

            # Verificar se o stash possui nome válido
            if stash_name:
                # Obter informações detalhadas sobre o stash
                stash_details = subprocess.check_output(
                    ["git", "stash", "show", "-s", stash_name], cwd=REPO_CWD
                ).decode()

                stash_lines = stash_details.split("\n")
                if len(stash_lines) > 0:
                    stash_date_line = stash_lines[0]
                    stash_date_info = stash_date_line.split(": ")
                    if len(stash_date_info) > 1:
                        stash_date_str = stash_date_info[1].strip()
                        stash_date = datetime.strptime(
                            stash_date_str, "%a %b %d %H:%M:%S %Y %z"
                        )

                        # Calcular a diferença de tempo
                        time_difference = datetime.now() - stash_date

                        # Definir um limite de 1 dia
                        one_day = timedelta(days=1)

                        if time_difference > one_day:
                            console("Removendo stash mais antigo:", stash_name)
                            subprocess.call(
                                ["git", "stash", "drop", stash_name], cwd=REPO_CWD
                            )
                        else:
                            console(
                                f"Modificações em stash encontradas ({stash_message})."
                                " Você pode recuperá-las usando 'git stash apply'.\n"
                                " A atualização prosseguirá normalmente.\n"
                            )
                    else:
                        console(
                            "Não foi possível obter informações sobre a data do stash.\n"
                        )
                else:
                    console("Não foi possível obter informações sobre o stash.\n")
            else:
                console("O último stash não possui um nome válido.\n")
        else:
            console("Não há stashes disponíveis.\n")

    except subprocess.CalledProcessError as e:
        raise Exception("Erro ao executar o comando git.\nErro: " + str(e))


def __execute_pull_from_repo(
    origin="origin", branch="main", output=False, stdOut=False
):
    if stdOut:
        return subprocess.run(
            ["git", "pull", origin, branch],
            stderr=subprocess.PIPE,
            text=True,
            cwd=REPO_CWD,
        )
    elif output:
        return subprocess.call(["git", "pull", origin, branch], cwd=REPO_CWD)
    else:
        raise Exception(
            "Informe se a saída do pull será impressa em tela ou string no return"
        )


def __check_for_updates():
    # Configuração global para rebase
    subprocess.call(["git", "config", "--global", "pull.rebase", "true"], cwd=REPO_CWD)
    __manage_last_stash()

    prints_separator(message="VERIFICANDO POR ATUALIZAÇÕES NO REPOSITORIO REMOTO...")
    try:
        # Obtém a saída do comando 'git rev-parse HEAD', que retorna o hash do último commit no repositório local
        local_hash = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_CWD)
            .decode()
            .strip()
        )

        # Obtém a saída do comando 'git ls-remote origin -h refs/heads/main', que retorna o hash do último commit no repositório remoto
        remote_hash = (
            subprocess.check_output(
                ["git", "ls-remote", "origin", "-h", "refs/heads/main"], cwd=REPO_CWD
            )
            .decode()
            .split()[0]
        )

        # Compara os hashes dos commits locais e remotos
        if local_hash == remote_hash:
            console(
                "O repositório local está atualizado com o remoto. Nenhuma ação é necessária.\n"
            )
            time.sleep(2)
        else:
            console(
                "O repositório local não está atualizado com o remoto. Executando pull from origin\n"
            )
            time.sleep(2)
            output = __execute_pull_from_repo(stdOut=True)
            if (
                "error: cannot pull with rebase: You have unstaged changes."
                in output.stderr
            ):
                subprocess.call(
                    ["git", "stash", "save", "app auto-stash"], cwd=REPO_CWD
                )
                time.sleep(2)
                __execute_pull_from_repo(output=True)
                time.sleep(2)
                console("\nAtualização concluída.")
                console(
                    "Há modificações salvas em stash. use 'git stash pop' para restaurá-las.\n"
                )
            else:
                console("Atualização concluída.\n")

    except subprocess.CalledProcessError as e:
        time.sleep(2)
        raise Exception("Erro ao executar o comando git.\nErro: " + str(e))


def __mount_server(local_path=LOCAL_SERVER_PATH, password=SUDO_PASSWD):
    prints_separator("MONTANDO O SERVIDOR LOCAL...")
    path_exists(local_path)
    if not __is_server_mounted(local_path):
        if not __is_tool_available("sshfs"):
            __install_sshfs()

        command = (
            f"sshfs dev@192.168.1.57:/home/dev/hd/server {local_path} -o password_stdin"
        )

        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=REPO_CWD,
        )

        stdout, stderr = process.communicate(input=f"{password}\n")

        if process.returncode == 0:
            console(f"\nSSHFS montado com sucesso em: {local_path}\n")
        else:
            console("\nErro ao montar SSHFS: ")
            raise Exception(stderr)

        return True

    console(f"\nSSHFS já está montado em:\n{local_path}\n")
    return True


def __umount_server(directory_path=LOCAL_SERVER_PATH):
    prints_separator(message="DESMONTANDO O SERVIDOR LOCAL...")
    try:
        subprocess.run(["fusermount", "-u", directory_path], check=True, cwd=REPO_CWD)
        console(f"\nDiretório {directory_path} desmontado com sucesso.")
    except subprocess.CalledProcessError:
        # print(f"\nErro ao desmontar o diretório {directory_path}.")
        # print("\nNova tentativa em 5 segundos...")
        time.sleep(5)
        subprocess.run(["umount", directory_path], check=True, cwd=REPO_CWD)
        console(f"\nDiretório {directory_path} desmontado com sucesso.")


def __config_server_and_backup(type_of_module):
    __mount_server()
    backup_files(type_of_module)


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
        console(
            "\nErro: Não use os flags -f e -a juntas. Ainda não há suporte para a execução dos módulos FOLHA e ADIANTAMENTO_FOLHA simultaneamente"
        )
        sys.exit(1)

    return args


def init_setup(type_of_module):
    prints_separator(message=f"Executando módulo {type_of_module}...")
    __check_for_updates()
    __config_server_and_backup(type_of_module.value)


def end_application():
    __umount_server()
