import os
import re
import json
import configparser
import pandas as pd
from pathlib import Path
from data_loader import load_pkl_roms

def fix_path(s):
    return str(Path(s).as_posix())


def normalize_string(s):
    s = re.sub(r'\(.*?\)|\[.*?\]', '', s)  # Remove content within () and []
    s = s.replace(' ', '').lower()  # Remove spaces and convert to lowercase
    return s

class PlaylistCreator:
    def __init__(self, info_dir, config_dir, playlist_dir):
        self.info_dir = info_dir
        self.config_dir = config_dir
        self.playlist_dir = playlist_dir

    def cria_lista(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        system_info = {
            "default_core_path": config.get("Playlists", "default_core_path", fallback=os.path.join("dev_hdd0", "game", "SSNE10000", "USRDIR", "cores", "snes9x_libretro_ps3.SELF")),
            "default_core_name": config.get("Playlists", "default_core_name", fallback="Nintendo - SNES / SFC (Snes9x - Current)"),
            "label_display_mode": config.getint("Playlists", "label_display_mode", fallback=3),
            "right_thumbnail_mode": config.getint("Playlists", "right_thumbnail_mode", fallback=0),
            "left_thumbnail_mode": config.getint("Playlists", "left_thumbnail_mode", fallback=0),
            "sort_mode": config.getint("Playlists", "sort_mode", fallback=0),
            "filter_genre": config.getboolean("DEFAULT", "filter_genre", fallback=False),
            "roms_exten": config.get("DEFAULT", "roms_exten", fallback=".zip"),
            "lista_saida": config.get("DEFAULT", "lista_saida", fallback=None),
            "config_path": config.get("DEFAULT", "config_path", fallback=os.path.join("data", "config")),
            "df_path": config.get("DEFAULT", "df_path", fallback=os.path.join("data", "roms.pkl")),
            "roms_path": config.get("DEFAULT", "roms_path", fallback=os.path.join("data", "roms")),
            "genre": config.get("DEFAULT", "genre", fallback=""),
            "system": config.get("DEFAULT", "system", fallback="fbneo"),
            "crc32": "DETECT",
            "version": "1.4"
        }

        lista = {
            "default_core_path": system_info["default_core_path"],
            "default_core_name": system_info["default_core_name"],
            "label_display_mode": system_info["label_display_mode"],
            "right_thumbnail_mode": system_info["right_thumbnail_mode"],
            "left_thumbnail_mode": system_info["left_thumbnail_mode"],
            "sort_mode": system_info["sort_mode"],
            "items": []
        }
        
        df = load_pkl_roms(system_info["df_path"])
        
        if df is None:
            return

        roms_path = system_info["roms_path"]
        roms_exten = system_info["roms_exten"]
        filter_genre = system_info["filter_genre"]
        genre_filter = system_info["genre"]
        genre_list = [g.strip().lower() for g in genre_filter.split(",")]

        for root, _, files in os.walk(roms_path):
            for file in files:
                if file.endswith(roms_exten):
                    file_lower = file.lower()
                    file_name_no_ext = os.path.splitext(file_lower)[0]
                    match = df[df['rom_name'].str.lower() == file_name_no_ext]
                    if not match.empty:
                        label = match['game_name'].values[0]
                        genre = match['genre'].values[0] if 'genre' in match else ''
                        if not filter_genre or any(g in genre.lower() for g in genre_list):
                            item = {
                                "path": os.path.join(root, file),
                                "label": label,
                                "core_path": system_info["default_core_path"],
                                "core_name": system_info["default_core_name"],
                                "crc32": "DETECT",
                                "db_name": system_info["lista_saida"]
                            }
                            lista["items"].append(item)

        output_path = fix_path( os.path.join(self.playlist_dir, system_info["lista_saida"]))

        with open(output_path, 'w') as f:
            json.dump(lista, f, indent=4)

    def consulta_info_cores(self):
        """
        Consulta informações sobre cores disponíveis no RetroArch.
        """
        info_files = [f for f in os.listdir(self.info_dir) if f.endswith('.info')]
        info_data = {}
        for info_file in info_files:
            with open(os.path.join(self.info_dir, info_file), 'r') as f:
                info_content = f.readlines()
                system_name = None
                core_path = None
                core_name = None
                for line in info_content:
                    if line.startswith('display_name'):
                        system_name = line.split('=')[1].strip().strip('"')
                    elif line.startswith('path'):
                        core_path = line.split('=')[1].strip().strip('"')
                    elif line.startswith('display_version'):
                        core_name = line.split('=')[1].strip().strip('"')
                if system_name and core_path:
                    info_data[system_name] = {
                        "core_path": core_path,
                        "core_name": core_name if core_name else ''
                    }

        for system_name, data in info_data.items():
            config = configparser.ConfigParser()
            config['Playlists'] = {
                'default_core_path': data['core_path'],
                'default_core_name': data['core_name'],
                'label_display_mode': '3',
                'right_thumbnail_mode': '0',
                'left_thumbnail_mode': '0',
                'sort_mode': '0'
            }

            config['DEFAULT'] = {
                'filter_genre': 'False',
                'roms_exten': '.zip',
                'lista_saida': f'{system_name}.lpl',
                'config_path': f'{self.config_dir}/{system_name}.ini',
                'df_path': 'data/roms.pkl',
                'roms_path': 'data/roms',
                'genre': ''
            }

            with open(f'{self.config_dir}/{system_name}.ini', 'w') as configfile:
                config.write(configfile)
    
if __name__ == '__main__':
    config_path = "data/inis/atari2600.ini"
    creator = PlaylistCreator(info_dir="data/info", config_dir="data/config", playlist_dir="data/playlists")
    creator.cria_lista(config_path)