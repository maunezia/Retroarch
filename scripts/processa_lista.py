import os
from ..scripts.my_ftp_man import FTPManager
import configparser
import pickle


def load_pkl(pkl_path):
    with open(pkl_path, 'rb') as f:
        return pickle.load(f)

def get_image_path(config_path, rom_name):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config['IMAGES'].get(rom_name, "Image path not found")

def process_list(ftp_manager, remote_path, lpl_name, pkl_path, config_path):
    # Baixar o arquivo .lpl
    local_lpl = f'/tmp/{lpl_name}'
    ftp_manager.download_file(os.path.join(remote_path, lpl_name), local_lpl)

    # Carregar o arquivo .lpl
    with open(local_lpl, 'r') as f:
        lines = f.readlines()

    # Carregar o PKL
    rom_data = load_pkl(pkl_path)

    # Processar cada linha do arquivo .lpl
    for line in lines:
        if line.strip().endswith('.zip'):
            rom_path = line.strip()
            rom_name = os.path.basename(rom_path).replace('.zip', '')

            if rom_name in rom_data:
                image_path = get_image_path(config_path, rom_name)
                print(f'ROM: {rom_name}, Image Path: {image_path}')
            else:
                print(f'ROM: {rom_name} not found in PKL.')

if __name__ == '__main__':
    # Configurações do servidor FTP
    ftp = FTPManager()
    print(ftp)
    quit()
    # Caminhos
    remote_path = '/path/to/listas'
    lpl_name = 'example.lpl'
    pkl_path = '/path/to/rom_data.pkl'
    config_path = '/path/to/config.ini'

    # Inicializar o gerenciador FTP
    ftp_manager = FTPManager(ftp_host, ftp_user, ftp_password)

    try:
        process_list(ftp_manager, remote_path, lpl_name, pkl_path, config_path)
    finally:
        ftp_manager.close()