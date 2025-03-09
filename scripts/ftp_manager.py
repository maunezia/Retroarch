import datetime
from ftplib import FTP
import configparser
import os
import argparse

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
        self.ftp.connect(self.host, self.port)
        self.ftp.login(user=self.username, passwd=self.password)
    
    def upload_files(self, local_path, remote_path, overwrite='always'):
        """
        Faz upload de arquivos do diretório local para o diretório remoto no servidor FTP.
        """
        for root, dirs, files in os.walk(local_path):
            for file in files:
                local_file = os.path.join(root, file)
                remote_file = os.path.join(remote_path, file)
                
                if overwrite != 'always' and self.file_exists(remote_file):
                    if overwrite == 'rename':
                        remote_file = self.get_unique_remote_filename(remote_file)
                    elif overwrite == 'skip':
                        continue
                    elif overwrite == 'larger' and not self.is_local_file_larger(local_file, remote_file):
                        continue
                    elif overwrite == 'newer' and not self.is_local_file_newer(local_file, remote_file):
                        continue

                with open(local_file, 'rb') as f:
                    self.ftp.storbinary(f'STOR {remote_file}', f)
    
    def download_files(self, local_path, remote_path, overwrite='always'):
        """
        Faz download de arquivos do diretório remoto no servidor FTP para o diretório local.
        """
        for root, dirs, files in self.ftp.mlsd(remote_path):
            for file in files:
                remote_file = os.path.join(root, file)
                local_file = os.path.join(local_path, file)
                
                if overwrite != 'always' and os.path.exists(local_file):
                    if overwrite == 'rename':
                        local_file = self.get_unique_local_filename(local_file)
                    elif overwrite == 'skip':
                        continue
                    elif overwrite == 'larger' and not self.is_remote_file_larger(remote_file, local_file):
                        continue
                    elif overwrite == 'newer' and not self.is_remote_file_newer(remote_file, local_file):
                        continue

                with open(local_file, 'wb') as f:
                    self.ftp.retrbinary(f'RETR {remote_file}', f.write)
    
    def file_exists(self, remote_file):
        """
        Verifica se um arquivo existe no servidor FTP.
        """
        try:
            self.ftp.size(remote_file)
            return True
        except:
            return False

    def get_unique_remote_filename(self, remote_file):
        """
        Gera um nome de arquivo único no servidor FTP para evitar sobrescrita.
        """
        base, ext = os.path.splitext(remote_file)
        counter = 1
        while self.file_exists(remote_file):
            remote_file = f"{base}_{counter}{ext}"
            counter += 1
        return remote_file

    def get_unique_local_filename(self, local_file):
        """
        Gera um nome de arquivo único no sistema local para evitar sobrescrita.
        """
        base, ext = os.path.splitext(local_file)
        counter = 1
        while os.path.exists(local_file):
            local_file = f"{base}_{counter}{ext}"
            counter += 1
        return local_file

    def is_local_file_larger(self, local_file, remote_file):
        """
        Verifica se o arquivo local é maior que o arquivo remoto.
        """
        local_size = os.path.getsize(local_file)
        remote_size = self.ftp.size(remote_file)
        return local_size > remote_size

    def is_local_file_newer(self, local_file, remote_file):
        """
        Verifica se o arquivo local é mais novo que o arquivo remoto.
        """
        local_mtime = os.path.getmtime(local_file)
        remote_mtime = self.ftp.sendcmd(f"MDTM {remote_file}")[4:]
        remote_mtime = datetime.datetime.strptime(remote_mtime, "%Y%m%d%H%M%S").timestamp()
        return local_mtime > remote_mtime

    def is_remote_file_larger(self, remote_file, local_file):
        """
        Verifica se o arquivo remoto é maior que o arquivo local.
        """
        remote_size = self.ftp.size(remote_file)
        local_size = os.path.getsize(local_file)
        return remote_size > local_size

    def is_remote_file_newer(self, remote_file, local_file):
        """
        Verifica se o arquivo remoto é mais novo que o arquivo local.
        """
        remote_mtime = self.ftp.sendcmd(f"MDTM {remote_file}")[4:]
        remote_mtime = datetime.datetime.strptime(remote_mtime, "%Y%m%d%H%M%S").timestamp()
        local_mtime = os.path.getmtime(local_file)
        return remote_mtime > local_mtime

    def close(self):
        """
        Fecha a conexão FTP.
        """
        self.ftp.quit()

if __name__ == '__main__':
    def main():
        parser = argparse.ArgumentParser(description='FTP Uploader/Downloader')
        parser.add_argument('action', choices=['upload', 'download'], help='Action to perform')
        parser.add_argument('local_path', help='Local path to upload/download')
        parser.add_argument('remote_path', help='Remote path to upload/download')
        parser.add_argument('--overwrite', choices=['rename', 'larger', 'newer', 'skip', 'always'], default='always', help='Overwrite option')
        args = parser.parse_args()

        ftp_man = FTPManager()

        if args.action == 'upload':
            ftp_man.upload_files(args.local_path, args.remote_path, args.overwrite)
        elif args.action == 'download':
            ftp_man.download_files(args.local_path, args.remote_path, args.overwrite)

        ftp_man.close()

    main()