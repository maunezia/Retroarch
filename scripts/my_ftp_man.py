import datetime
import os
import argparse
import logging
import configparser
from ftplib import FTP, error_perm

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FTPManager:
    def __init__(self, config_path="config.ini"):
        """
        Inicializa a conexão FTP usando as configurações fornecidas no arquivo config.ini.
        """
        config = configparser.ConfigParser()
        config.read(config_path)

        self.host = config.get('PS3', 'ps3_ftp_ip', fallback='192.168.1.66')
        self.port = config.getint('PS3', 'ps3_ftp_port', fallback=21)
        self.username = config.get('PS3', 'ps3_ftp_user', fallback='anonymous')
        self.password = config.get('PS3', 'ps3_ftp_pass', fallback='anonymous')

        self.ftp = FTP()
        try:
            self.ftp.connect(self.host, self.port)
            self.ftp.login(user=self.username, passwd=self.password)
            logging.info("Conectado ao FTP %s:%s", self.host, self.port)
        except Exception as e:
            logging.error("Erro ao conectar/login no FTP: %s", e)
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    def is_connected(self):
        """
        Verifica se a conexão FTP está ativa.
        """
        try:
            self.ftp.voidcmd("NOOP")
            return True
        except Exception as e:
            logging.error("Erro ao verificar conexão FTP: %s", e)
            return False
        
    def upload_files(self, local_path, remote_path, overwrite='always'):
        """
        Faz upload de arquivos do diretório local para o diretório remoto no servidor FTP.
        """
        for root, _, files in os.walk(local_path):
            for file in files:
                local_path = os.path.join(root, file)
                remote_file = os.path.join(remote_path, file)
                try:
                    if overwrite != 'always' and self.file_exists(remote_file):
                        if overwrite == 'rename':
                            remote_file = self.get_unique_remote_filename(remote_file)
                        elif overwrite == 'skip':
                            logging.info("Pulando upload do arquivo %s por opção 'skip'", local_path)
                            continue
                        elif overwrite == 'larger' and not self.is_local_path_larger(local_path, remote_file):
                            logging.info("Arquivo local %s não é maior que remoto", local_path)
                            continue
                        elif overwrite == 'newer' and not self.is_local_path_newer(local_path, remote_file):
                            logging.info("Arquivo local %s não é mais novo que remoto", local_path)
                            continue

                    with open(local_path, 'rb') as f:
                        self.ftp.storbinary(f'STOR {remote_file}', f)
                        logging.info("Upload realizado: %s -> %s", local_path, remote_file)
                except Exception as e:
                    logging.error("Erro ao fazer upload de %s: %s", local_path, e)

    def list_directories(self, remote_path):
        """
        Lista os diretórios de um diretório remoto no servidor FTP.
        """
        try:
            # Divide o caminho e navega por cada diretório
            directories = remote_path.strip('/').split('/')
            for directory in directories:
                if directory:  # Ignora strings vazias
                    self.ftp.cwd(directory)

            # Lista os diretórios no último diretório
            directories = self.ftp.nlst()
            directories = [d for d in directories if self.ftp.sendcmd(f"TYPE A {d}").startswith("2")]
            directories = [d for d in directories if d not in ('.', '..')]
            return directories
        
        except Exception as e:
            logging.error("Erro ao listar diretórios do diretório remoto %s: %s", remote_path, e)
            return []
        
    def list_files(self, remote_path, ext="*.*", recursive=False):
        """
        Lista os arquivos de um diretório remoto no servidor FTP.
        Navega por cada diretório no caminho fornecido antes de listar os arquivos.
        """

        try:
            # Divide o caminho e navega por cada diretório
            directories = remote_path.strip('/').split('/')
            for directory in directories:
                if directory:  # Ignora strings vazias
                    self.ftp.cwd(directory)

            # Lista os arquivos no último diretório
            files = self.ftp.nlst()
            if ext != "*.*":
                files = [f for f in files if f.lower().endswith(ext.lower())]

            return files
        
        except Exception as e:
            logging.error("Erro ao listar arquivos do diretório remoto %s: %s", remote_path, e)
            return []
    
    def download_file(self, remote_file, local_file=None, overwrite='always'):
        """
        Faz download de um arquivo do servidor FTP para o sistema local.
        """
        if local_file is None:
            remote_file_name = os.path.basename(remote_file)
            local_file = f"/data/downloads/tmp/{remote_file_name}"
            print(f"O arquivo será salvo em: {local_file}")
        try:
            # Verifica se o arquivo local já existe e aplica a lógica de sobrescrita
            if os.path.exists(local_file):
                if overwrite == 'skip':
                    logging.info("Pulando download do arquivo %s por opção 'skip'", remote_file)
                    return False
                elif overwrite == 'rename':
                    local_file = self.get_unique_local_pathname(local_file)
                elif overwrite == 'larger' and not self.is_remote_file_larger(remote_file, local_file):
                    logging.info("Arquivo remoto %s não é maior que local", remote_file)
                    return False
                elif overwrite == 'newer' and not self.is_remote_file_newer(remote_file, local_file):
                    logging.info("Arquivo remoto %s não é mais novo que local", remote_file)
                    return False

            # Cria o diretório local, se necessário
            local_dir = os.path.dirname(local_file)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)
                logging.info("Diretório criado: %s", local_dir)

            # Faz o download do arquivo
            with open(local_file, 'wb') as f:
                self.ftp.retrbinary(f'RETR {remote_file}', f.write)
            logging.info("Download realizado: %s -> %s", remote_file, local_file)
            return True
        except error_perm as e:
            if '550' in str(e):
                logging.error("Arquivo remoto não encontrado: %s", remote_file)
            else:
                logging.error("Erro de permissão ao acessar %s: %s", remote_file, e)
        except FileNotFoundError as e:
            logging.error("Erro ao acessar o arquivo local %s: %s", local_file, e)
        except Exception as e:
            logging.error("Erro inesperado ao fazer download de %s: %s", remote_file, e)
        return False


    def download_files(self, local_path, remote_path, overwrite='always'):
        """
        Faz download de arquivos do diretório remoto no servidor FTP para o diretório local.
        Utiliza MLSD para obter informações detalhadas dos arquivos.
        """
        try:
            entries = list(self.ftp.mlsd(remote_path))
        except Exception as e:
            logging.error("Erro ao listar o diretório remoto %s: %s", remote_path, e)
            return

        for name, facts in entries:
            # Considera apenas arquivos; pode filtrar por 'type'
            if facts.get("type") != "file":
                continue
            remote_file = os.path.join(remote_path, name)
            local_path = os.path.join(local_path, name)

            try:
                if overwrite != 'always' and os.path.exists(local_path):
                    if overwrite == 'rename':
                        local_path = self.get_unique_local_pathname(local_path)
                    elif overwrite == 'skip':
                        logging.info("Pulando download do arquivo %s por opção 'skip'", remote_file)
                        continue
                    elif overwrite == 'larger' and not self.is_remote_file_larger(remote_file, local_path):
                        logging.info("Arquivo remoto %s não é maior que local", remote_file)
                        continue
                    elif overwrite == 'newer' and not self.is_remote_file_newer(remote_file, local_path):
                        logging.info("Arquivo remoto %s não é mais novo que local", remote_file)
                        continue

                with open(local_path, 'wb') as f:
                    self.ftp.retrbinary(f'RETR {remote_file}', f.write)
                    logging.info("Download realizado: %s -> %s", remote_file, local_path)
            except Exception as e:
                logging.error("Erro ao fazer download de %s: %s", remote_file, e)
    def get_size(self, remote_file):
        """
        Retorna o tamanho de um arquivo no servidor FTP.
        """
        try:
            return self.ftp.size(remote_file)
        except Exception as e:
            logging.error("Erro ao obter tamanho de %s: %s", remote_file, e)
            return 0

    def file_exists(self, remote_file):
        """
        Verifica se um arquivo existe no servidor FTP.
        """
        try:
            self.ftp.size(remote_file)
            return True
        except error_perm as e:
            if '550' in str(e):
                return False
            else:
                logging.error("Erro ao verificar existência de %s: %s", remote_file, e)
                return False
        except Exception as e:
            logging.error("Erro ao verificar existência de %s: %s", remote_file, e)
            return False

    def get_unique_remote_filename(self, remote_file):
        """
        Gera um nome de arquivo único no servidor FTP para evitar sobrescrita.
        """
        base, ext = os.path.splitext(remote_file)
        counter = 1
        unique_name = remote_file
        while self.file_exists(unique_name):
            unique_name = f"{base}_{counter}{ext}"
            counter += 1
        return unique_name

    def get_unique_local_pathname(self, local_path):
        """
        Gera um nome de arquivo único no sistema local para evitar sobrescrita.
        """
        base, ext = os.path.splitext(local_path)
        counter = 1
        unique_name = local_path
        while os.path.exists(unique_name):
            unique_name = f"{base}_{counter}{ext}"
            counter += 1
        return unique_name

    def is_local_path_larger(self, local_path, remote_file):
        """
        Verifica se o arquivo local é maior que o arquivo remoto.
        """
        try:
            local_size = os.path.getsize(local_path)
            remote_size = self.ftp.size(remote_file)
            return local_size > remote_size
        except Exception as e:
            logging.error("Erro ao comparar tamanho entre %s e %s: %s", local_path, remote_file, e)
            return False

    def is_local_path_newer(self, local_path, remote_file):
        """
        Verifica se o arquivo local é mais novo que o arquivo remoto.
        """
        try:
            local_mtime = os.path.getmtime(local_path)
            remote_mtime_str = self.ftp.sendcmd(f"MDTM {remote_file}")[4:]
            remote_mtime = datetime.datetime.strptime(remote_mtime_str, "%Y%m%d%H%M%S").timestamp()
            return local_mtime > remote_mtime
        except Exception as e:
            logging.error("Erro ao comparar data entre %s e %s: %s", local_path, remote_file, e)
            return False

    def is_remote_file_larger(self, remote_file, local_path):
        """
        Verifica se o arquivo remoto é maior que o arquivo local.
        """
        try:
            remote_size = self.ftp.size(remote_file)
            local_size = os.path.getsize(local_path)
            return remote_size > local_size
        except Exception as e:
            logging.error("Erro ao comparar tamanho entre %s e %s: %s", remote_file, local_path, e)
            return False

    def is_remote_file_newer(self, remote_file, local_path):
        """
        Verifica se o arquivo remoto é mais novo que o arquivo local.
        """
        try:
            remote_mtime_str = self.ftp.sendcmd(f"MDTM {remote_file}")[4:]
            remote_mtime = datetime.datetime.strptime(remote_mtime_str, "%Y%m%d%H%M%S").timestamp()
            local_mtime = os.path.getmtime(local_path)
            return remote_mtime > local_mtime
        except Exception as e:
            logging.error("Erro ao comparar data entre %s e %s: %s", remote_file, local_path, e)
            return False

    def close(self):
        """
        Fecha a conexão FTP.
        """
        try:
            self.ftp.quit()
            logging.info("Conexão FTP fechada.")
        except Exception as e:
            logging.error("Erro ao fechar a conexão FTP: %s", e)


if __name__ == '__main__':
    def exemplo1():
        parser = argparse.ArgumentParser(description='FTP Uploader/Downloader')
        parser.add_argument('action', choices=['upload', 'download'], help='Ação a realizar')
        parser.add_argument('local_path', help='Caminho local para upload/download')
        parser.add_argument('remote_path', help='Caminho remoto para upload/download')
        parser.add_argument('--overwrite', choices=['rename', 'larger', 'newer', 'skip', 'always'], default='always', help='Opção de sobrescrita')
        args = parser.parse_args()

        with FTPManager() as ftp_man:
            if args.action == 'upload':
                ftp_man.upload_files(args.local_path, args.remote_path, args.overwrite)
            elif args.action == 'download':
                ftp_man.download_files(args.local_path, args.remote_path, args.overwrite)

    exemplo1()