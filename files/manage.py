import shutil
import subprocess
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

    text = f"Moved {file_name} to: {destination_path}"
    print(text)

    dicionario_export = {"file": file_name, "path": destination_path}
    return dicionario_export


def backup_files(type_of_event):
    print(type_of_event)
    time.sleep(50)
    for item in os.listdir(type_of_event):
        origin = os.path.join(type_of_event, item)
        dest = os.path.join(BACKUP_PATH, item)

        if os.path.isdir(origin):
            shutil.copytree(origin, dest)


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


def mount_server(local_path=f"{os.path.expanduser('~')}/server", password="dev@123"):
    path_exists(local_path)
    if not __is_server_mounted(local_path):
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
            print(f"SSHFS montado com sucesso em:\n{local_path}\n")
        else:
            print("Erro ao montar SSHFS: ")
            raise Exception(stderr)

        return True

    print(f"SSHFS já está montado em:\n{local_path}\n")
    return True


def unmount_server(directory_path):
    try:
        subprocess.run(["fusermount", "-u", directory_path], check=True)
        print(f"Diretório {directory_path} desmontado com sucesso.")
    except subprocess.CalledProcessError:
        print(f"Erro ao desmontar o diretório {directory_path}.")
