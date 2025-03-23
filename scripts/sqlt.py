import os
import sqlite3
from xml.etree import ElementTree as ET
from my_ftp_man import FTPManager

class ROMManager:
    def __init__(self, db_path, ftp_manager, ftp_roms_path, core_id):
        self.db_path = db_path
        self.ftp_manager = ftp_manager
        self.ftp_roms_path = ftp_roms_path
        self.core_id = core_id

    def clean_name(self, name):
        """Remove content inside parentheses and trim whitespace."""
        return ''.join([c for c in name if c not in "()"]).strip().lower()

    def fetch_ftp_files(self, path):
        """Fetch the list of files from the FTP server."""
        return self.ftp_manager.list_files(path)

    def parse_xml(self, xml_path):
        """Parse the XML file and return a list of games."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        games = []
        for game in root.findall('game'):
            games.append({
                'name': game.find('name').text,
                'description': game.find('description').text,
                'year': game.find('year').text,
                'manufacturer': game.find('manufacturer').text,
                'size': game.find('size').text if game.find('size') is not None else None
            })
        return games

    def match_and_insert(self, system_name, xml_path):
        """Match ROMs with the database and insert missing entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Fetch FTP files
        ftp_files = self.fetch_ftp_files(self.ftp_roms_path)
        ftp_file_names = [os.path.splitext(f)[0] for f in ftp_files]

        # Parse XML
        xml_games = self.parse_xml(xml_path)

        # Match against database
        for rom_name in ftp_file_names:
            cursor.execute("SELECT * FROM games WHERE name = ? AND system = ?", (rom_name, system_name))
            game = cursor.fetchone()

            if not game:
                # Second pass: clean names and match with titles
                clean_rom_name = self.clean_name(rom_name)
                cursor.execute("SELECT * FROM games WHERE title LIKE ?", (f"%{clean_rom_name}%",))
                game = cursor.fetchone()

            if not game:
                # Insert missing game into the database
                for xml_game in xml_games:
                    if self.clean_name(xml_game['name']) == clean_rom_name:
                        game_data = {
                            'system': system_name,
                            'name': xml_game['name'],
                            'title': xml_game['name'],
                            'desc': xml_game['description'],
                            'year': xml_game['year'],
                            'developer': xml_game['manufacturer'],
                            'publisher': xml_game['manufacturer'],
                            'info': '',
                            'genres': '',
                            'players': '',
                            'aspectratio': '',
                            'resolution': '',
                            'order_id': None,
                            'def_core_id': None
                        }
                        cursor.execute("""
                            INSERT INTO games (system, name, title, desc, year, developer, publisher, info, genres, players, aspectratio, resolution, order_id, def_core_id)
                            VALUES (:system, :name, :title, :desc, :year, :developer, :publisher, :info, :genres, :players, :aspectratio, :resolution, :order_id, :def_core_id)
                        """, game_data)
                        conn.commit()
                        game_id = cursor.lastrowid

                        # Insert into games_available
                        cursor.execute("""
                            INSERT INTO games_available (game_id, path, filesize, coreid)
                            VALUES (?, ?, ?, ?)
                        """, (
                            game_id,
                            f"{self.ftp_roms_path}/{rom_name}.zip",
                            xml_game['size'],
                            self.core_id
                        ))
                        conn.commit()
                        break

        conn.close()

# Example usage
if __name__ == "__main__":
    ftp_manager = FTPManager()
    print(ftp_manager.is_connected())
    db_path = r"C:\Users\Amozin\Python\Retroarch\data\downloads\FBNE00123\USRDIR\retro.db"
    ftp_roms_path = "/dev_hdd0/ROMS/snes"
    core_id = 1
    xml_path = "d:/Games/roms/snes/Super Nintendo.dat"
    rom_manager = ROMManager(db_path, ftp_manager, ftp_roms_path, core_id)
    rom_manager.match_and_insert("Super Nintendo", xml_path)