import ftplib
import json
import os
import logging
from contextlib import contextmanager

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FTPOrganizer:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self._load_or_create_config()
        self.server_ip = self.config.get('ip', '192.168.1.66')
        self.username = self.config.get('usuario', 'user')
        self.password = self.config.get('senha', 'senha')
        self.target_folder = self.config.get('ftp_pasta', '/dev_hdd0/packages')
        self.prefix = self.config.get('prefixo', 'Download')
        self.extension = self.config.get('extensao', '.pkg')

    def _load_or_create_config(self):
        """
        Carrega o arquivo de configuração. Se não existir, cria um com valores padrão.
        """
        if not os.path.exists(self.config_path):
            default_config = {
                'ip': '192.168.1.66',
                'usuario': 'user',
                'senha': 'senha',
                'ftp_pasta': '/dev_hdd0/packages',
                'prefixo': 'Download',
                'extensao': '.pkg'
            }
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as file:
                json.dump(default_config, file, indent=4)
            logging.info("Arquivo de configuração criado em %s", self.config_path)
            return default_config
        else:
            with open(self.config_path, 'r') as file:
                config = json.load(file)
            logging.info("Configuração carregada de %s", self.config_path)
            return config

    @contextmanager
    def ftp_connection(self):
        """
        Gerencia a conexão FTP como um contexto.
        """
        ftp = ftplib.FTP()
        try:
            ftp.connect(self.server_ip)
            ftp.login(self.username, self.password)
            logging.info("Conectado ao FTP %s", self.server_ip)
            yield ftp
        except ftplib.all_errors as e:
            logging.error("Erro na conexão FTP: %s", e)
            raise
        finally:
            try:
                ftp.quit()
                logging.info("Conexão FTP encerrada")
            except ftplib.all_errors:
                pass

    def rename_files(self):
        """
        Renomeia arquivos na pasta FTP de acordo com as configurações e salva um log dos renomes.
        """
        renamed_files = []
        with self.ftp_connection() as ftp:
            try:
                ftp.cwd(self.target_folder)
                files = ftp.nlst()
                size_count = {}

                for file in files:
                    if file.endswith(self.extension):
                        try:
                            size = ftp.size(file)
                        except ftplib.all_errors as e:
                            logging.error("Não foi possível obter tamanho para %s: %s", file, e)
                            continue
                        size_str = self.get_size_char(size)
                        count = size_count.get(size_str, 0) + 1
                        size_count[size_str] = count
                        new_name = f"{self.prefix}_{count}_{size_str}{self.extension}"
                        renamed_files.append((file, new_name))
                        ftp.rename(file, new_name)
                        logging.info("Renomeado: %s --> %s", file, new_name)
                self._save_renamed_files_log(renamed_files, ftp)
            except ftplib.all_errors as e:
                logging.error("Erro durante renomeação: %s", e)

    def get_size_char(self, size):
        """
        Converte o tamanho em bytes para uma string com unidade.
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.0f}{unit}"
            size /= 1024
        return f"{size:.0f}PB"

    def _save_renamed_files_log(self, renamed_files, ftp):
        """
        Salva um log dos arquivos renomeados localmente e faz upload para o FTP.
        """
        local_file_path = 'renamed_files.txt'
        try:
            with open(local_file_path, 'w') as file:
                for old_name, new_name in renamed_files:
                    file.write(f"{old_name} --> {new_name}\n")
            logging.info("Arquivo de log criado: %s", local_file_path)
            
            # Upload do log para a pasta FTP
            with open(local_file_path, 'rb') as file:
                remote_log_path = os.path.join(self.target_folder, 'renamed_files.txt')
                ftp.storbinary(f'STOR {remote_log_path}', file)
            logging.info("Arquivo de log enviado para o FTP: %s", remote_log_path)
        except Exception as e:
            logging.error("Erro ao salvar/enviar log: %s", e)
        finally:
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                logging.info("Arquivo de log local removido.")

if __name__ == '__main__':
    organizer = FTPOrganizer('data/config/ftp_config.json')
    organizer.rename_files()
