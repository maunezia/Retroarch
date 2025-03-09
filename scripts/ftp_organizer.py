import ftplib
import json
import os

class FTPOrganizer:
    def __init__(self, config_path):
        if not os.path.exists(config_path):
            default_config = {
                'ip': '192.168.1.66',
                'usuario': 'user',
                'senha': 'senha',
                'ftp_pasta': '/dev_hdd0/packages',
                'prefixo': 'Download',
                'extensao': '.pkg'
            }
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as file:
                json.dump(default_config, file, indent=4)
        
        with open(config_path, 'r') as file:
            config = json.load(file)

        self.server_ip = config.get('ip', '192.168.1.66')
        self.username = config.get('usuario', 'user')
        self.password = config.get('senha', 'senha')
        self.target_folder = config.get('ftp_pasta', '/dev_hdd0/packages')
        self.prefix = config.get('prefixo', 'Download')
        self.extension = config.get('extensao', '.pkg')
        self.ftp = ftplib.FTP()

    def connect(self):
        try:
            self.ftp.connect(self.server_ip)
            self.ftp.login(self.username, self.password)
            print("Connected to FTP server")
        except ftplib.all_errors as e:
            print(f"Failed to connect: {e}")
            return False
        return True

    def rename_files(self):
        if not self.connect():
            return

        try:
            self.ftp.cwd(self.target_folder)
            files = self.ftp.nlst()
            renamed_files = []
            size_count = {}

            for file in files:
                if file.endswith(self.extension):
                    size = self.ftp.size(file)
                    size_str = self.get_size_char(size)
                    count = size_count.get(size_str, 0) + 1
                    size_count[size_str] = count
                    new_name = f"{self.prefix}_{count}_{size_str}{self.extension}"
                    renamed_files.append((file, new_name))

                    self.ftp.rename(file, new_name)

            self.save_renamed_files(renamed_files)
        except ftplib.all_errors as e:
            print(f"FTP error: {e}")
        finally:
            self.ftp.quit()

    def get_size_char(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.0f}{unit}"
            size /= 1024
        return f"{size:.0f}PB"

    def save_renamed_files(self, renamed_files):
        local_file_path = 'renamed_files.txt'
        with open(local_file_path, 'w') as file:
            for old_name, new_name in renamed_files:
                file.write(f"{old_name} --> {new_name}\n")

        # Upload the file to the FTP server
        with open(local_file_path, 'rb') as file:
            self.ftp.storbinary(f'STOR {self.target_folder}/renamed_files.txt', file)

        # Remove the local file
        os.remove(local_file_path)

if __name__ == '__main__':
    organizer = FTPOrganizer('data/config/ftp_config.json')
    organizer.rename_files()