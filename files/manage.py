import errno
import json
import shutil
import subprocess
import sys
import time

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
    path_exists(BACKUP_PATH)

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


def path_exists(path):
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


def mount_server(local_path=LOCAL_SERVER_PATH, password=SUDO_PASSWD):
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
        print(f"\nErro ao desmontar o diretório {directory_path}.")
        print("\nNova tentativa em 5 segundos...")
        time.sleep(5)
        subprocess.run(["umount", directory_path], check=True)
        print(f"\nDiretório {directory_path} desmontado com sucesso.")
