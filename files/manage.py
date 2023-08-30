import errno
import json
import shutil
import subprocess
import sys
import time
from datetime import timedelta

from data import tools
from data.consts import *
from data.exceptions import FileNotFound


def move_file(company_name, file_name, complete_path):
    destination_path = tools.generate_folder_path(company_name, file_name)
    destination_path = tools.generate_new_file_suffix(destination_path, file_name)
    try:
        shutil.move(complete_path, destination_path)
    except FileNotFoundError as e:
        raise FileNotFound(e)

    text = f"\nMovido {file_name} para: \n{destination_path}\n"
    print(text)

    dicionario_export = {"file": file_name, "path": destination_path}
    return dicionario_export


def backup_files(type_of_event):
    __path_exists(BACKUP_PATH)

    for item in os.listdir(type_of_event):
        origin = os.path.join(type_of_event, item)
        dest = os.path.join(BACKUP_PATH, item)

        if os.path.isdir(origin):
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(origin, dest)
            print(f"\nCopiado {origin} para {dest}\n")
        else:  # Se não for um diretório, assumimos que é um arquivo
            shutil.copy2(origin, dest)
            print(f"\nCopiado arquivo {origin} para {dest}\n")

    # Imprimir o separador no final
    print("/" * 40 + "*" * 5 + "/" * 40)


def generate_report_file(list_object: list, name, json_file=False):
    if not json_file:
        with open(f"{os.getcwd()}/output/{name}.txt", "w") as file:
            for text in list_object:
                file.write(text + "\n")
    else:
        with open(f"{os.getcwd()}/output/{name}.json", "w") as file:
            json.dump(list_object, file)


def __path_exists(path):
    # Verificar se o diretório existe
    if not os.path.exists(path):
        # Se não existir, criar o diretório
        os.makedirs(path)
        print(f'\nDiretório "{path}" criado com sucesso.')


def __is_server_mounted(directory_path):
    try:
        # Execute o comando "mount" e capture a saída
        output = subprocess.check_output(["mount"], text=True)

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
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        if e.errno == errno.ENOENT:
            return False
    return True


def __install_sshfs():
    """Instala o sshfs usando o gerenciador de pacotes apt."""
    print(
        "\nSSHFS não encontrado! Isto é necessário para montar o diretário remoto. Tentando instalar...\n"
    )
    time.sleep(5)
    try:
        subprocess.run(["sudo", "apt", "install", "-y", "sshfs"], check=True)
    except subprocess.CalledProcessError:
        print(
            "Erro ao atualizar ou instalar o sshfs. Por favor, tente manualmente.\n\nUSE: 'sudo apt update && sudo apt-get install sshfs'"
        )
        sys.exit(1)


# Função para verificar e gerenciar o último stash
def __manage_last_stash():
    try:
        # Verificar se há stashes
        stash_list = (
            subprocess.check_output(["git", "stash", "list"])
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
                    ["git", "stash", "show", "-s", stash_name]
                ).decode()
                stash_date_str = stash_details.split("\n")[0].split(": ")[1].strip()
                stash_date = datetime.strptime(
                    stash_date_str, "%a %b %d %H:%M:%S %Y %z"
                )

                # Calcular a diferença de tempo
                time_difference = datetime.now() - stash_date

                # Definir um limite de 1 dia
                one_day = timedelta(days=1)

                if time_difference > one_day:
                    print("Removendo stash mais antigo:", stash_name)
                    subprocess.call(["git", "stash", "drop", stash_name])
                else:
                    print(
                        f"Modificações em stash encontradas ({stash_message})."
                        " Você pode recuperá-las usando 'git stash apply'."
                        " A atualização prosseguirá normalmente.\n"
                    )
            else:
                print("O último stash não possui um nome válido.\n")

    except subprocess.CalledProcessError as e:
        raise Exception("Erro ao executar o comando git.\nErro: " + str(e))


def check_for_updates():
    # Configuração global para rebase
    subprocess.call(["git", "config", "--global", "pull.rebase", "true"])
    __manage_last_stash()

    print("Verificando se o repositário local está atualizado com o remoto...")
    try:
        # Obtém a saída do comando 'git rev-parse HEAD', que retorna o hash do último commit no repositório local
        local_hash = (
            subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        )

        # Obtém a saída do comando 'git ls-remote origin -h refs/heads/main', que retorna o hash do último commit no repositório remoto
        remote_hash = (
            subprocess.check_output(
                ["git", "ls-remote", "origin", "-h", "refs/heads/main"]
            )
            .decode()
            .split()[0]
        )

        # Compara os hashes dos commits locais e remotos
        if local_hash == remote_hash:
            print(
                "O repositório local está atualizado com o remoto. Nenhuma ação é necessária.\n"
            )
            time.sleep(2)
        else:
            print(
                "O repositório local não está atualizado com o remoto. Executando pull from origin\n"
            )
            time.sleep(2)
            output = subprocess.run(
                ["git", "pull", "origin", "main"], stderr=subprocess.PIPE, text=True
            )
            if (
                "error: cannot pull with rebase: You have unstaged changes."
                in output.stderr
            ):
                subprocess.call(["git", "stash", "save", "app auto-stash"])
                time.sleep(2)
                print("\nAtualização concluída.\n")
            else:
                print("Atualização concluída.")

    except subprocess.CalledProcessError as e:
        time.sleep(2)
        raise Exception("Erro ao executar o comando git.\nErro: " + str(e))


def mount_server(local_path=LOCAL_SERVER_PATH, password=SUDO_PASSWD):
    __path_exists(local_path)
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
        )

        stdout, stderr = process.communicate(input=f"{password}\n")

        if process.returncode == 0:
            print(f"\nSSHFS montado com sucesso em: {local_path}\n")
        else:
            print("\nErro ao montar SSHFS: ")
            raise Exception(stderr)

        return True

    print(f"\nSSHFS já está montado em:\n{local_path}\n")
    return True


def umount_server(directory_path=LOCAL_SERVER_PATH):
    try:
        subprocess.run(["fusermount", "-u", directory_path], check=True)
        print(f"\nDiretório {directory_path} desmontado com sucesso.")
    except subprocess.CalledProcessError:
        # print(f"\nErro ao desmontar o diretório {directory_path}.")
        # print("\nNova tentativa em 5 segundos...")
        time.sleep(5)
        subprocess.run(["umount", directory_path], check=True)
        print(f"\nDiretório {directory_path} desmontado com sucesso.")
