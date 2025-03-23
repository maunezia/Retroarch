import sqlite3
from my_ftp_man import FTPManager
import csv

class RetroDBModifier:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        """Estabelece conexão com o banco de dados."""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection:
            self.connection.close()

    def fetch_all_tables_and_fields(self):
        """Retorna todas as tabelas e campos do banco de dados."""
        self.connect()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        schema = {}
        for table in tables:
            table_name = table[0]
            self.cursor.execute(f"PRAGMA table_info({table_name});")
            fields = self.cursor.fetchall()
            schema[table_name] = [field[1] for field in fields]
        self.close()
        return schema

    def fetch_table_data(self, table_name):
        """Retorna todos os dados de uma tabela específica."""
        self.connect()
        self.cursor.execute(f"SELECT * FROM {table_name};")
        rows = self.cursor.fetchall()
        self.close()
        return rows

    def update_game_name(self, game_id, new_name):
        """Atualiza o nome de um jogo na tabela games."""
        self.connect()
        self.cursor.execute("UPDATE games SET name = ? WHERE id = ?", (new_name, game_id))
        self.connection.commit()
        self.close()

# Exemplo de uso:
if __name__ == "__main__":
    db_modifier = RetroDBModifier(r"C:\Users\Amozin\Python\Retroarch\data\downloads\FBNE00123\USRDIR\retro.db")
    # Coletar todas as tabelas e campos
    # Diretório contendo os arquivos
    local_dir = r"D:\Games\roms\snes"
    ftp_rom_path = r"/dev_hdd0/ROMS/snes"
    ftp_img_path = r"/dev_hdd0/game/FBNE00123/USRDIR/cores/titles"
    ftp_db_path = r"/dev_hdd0/game/FBNE00123/USRDIR/retro.db"

    # Obter todas as tabelas e campos
    schema = db_modifier.fetch_all_tables_and_fields()
    ftp = FTPManager()
    # Conectar ao banco de dados
    db_modifier.connect()

    # Verificar se a tabela games_available existe no banco
    if "games_available" in schema:
        # Listar todos os arquivos no diretório
        # Caminho do FTP para SNES
        files = ftp.list_files(ftp_rom_path)
        ftp_snes_path = ftp_rom_path
        # Primeiro, carregar os dados do XML dat
        xml_games = []  # Lista para armazenar os jogos do XML
        # Aqui você deve implementar o carregamento do XML e popular a lista xml_games
        # Cada item da lista deve ser um dicionário com os campos: name, description, year, manufacturer, rom_name, size
        # Primeira passada: procurar por match e popular games_available
        for file in files:
            file_path = ftp_snes_path + "/" + file
            if not ftp.file_exists(file_path):
                print(f"File not found: {file_path}")
                continue
            rom_name = file.rsplit('.', 1)[0]  # Nome da ROM sem extensão
            # Verificar se o arquivo já está no banco
            db_modifier.cursor.execute("SELECT id FROM games WHERE system = ? AND subsystem = ? AND name = ?", ("snes", "snes", rom_name))
            game_data = db_modifier.cursor.fetchone()

            if game_data:
                game_id, parent = game_data
                # Adicionar ao banco caso não esteja lá

                db_modifier.cursor.execute(
                    "INSERT INTO games_available (path, filesize, game_id) VALUES (?, ?, ?)",
                    (file_path, ftp.get_size(file_path), game_id, parent),
                )
            else:
                # Adicionar à lista de não encontrados
                xml_games.append({
                    "rom_name": rom_name,
                    "path": file_path,
                    "size": ftp.get_size(file_path),
                })
        # Segunda passada: exportar os jogos não encontrados para not_found.csv
        not_found_path = ".snes_not_found.csv"
        with open(not_found_path, mode="w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["rom_name", "path", "size"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(xml_games)
        # Salvar alterações e fechar conexão
        db_modifier.connection.commit()
        db_modifier.close()
    else:
        print("Tabela 'games_available' não encontrada no banco de dados.")