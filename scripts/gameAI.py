import os
import pickle
from my_ftp_man import FTPManager
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import sqlite3
import re


class RetroArchAI:
    def __init__(self, db_path="C:\\Users\\Amozin\\Python\\Retroarch\\data\\downloads\\FBNE00123\\USRDIR\\retro.db", model_path="model.pkl"):
        self.db_path = db_path
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer()
        self.knn = NearestNeighbors(n_neighbors=1, metric="cosine")
        self.data = None

        # Carregar modelo treinado se existir
        if os.path.exists(self.model_path):
            self.load_model()
        else:
            self.train_model()

    def connect_db(self):
        return sqlite3.connect(self.db_path)

    def limpar_nome(self, nome):
        nome = nome.lower()
        nome = re.sub(r"[^a-z0-9 ]", "", nome)  # Remove caracteres especiais
        nome = nome.replace("the ", "").strip()
        return nome

    def train_model(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        
        query = "SELECT ID, rom_name, name FROM games"
        self.data = cursor.execute(query).fetchall()
        conn.close()

        if not self.data:
            print("Nenhum dado encontrado para treinamento.")
            return

        df_roms = [(row[0], self.limpar_nome(row[1]), self.limpar_nome(row[2])) for row in self.data]
        ids, rom_names, game_names = zip(*df_roms)

        X = self.vectorizer.fit_transform(game_names)
        self.knn.fit(X)

        with open(self.model_path, "wb") as f:
            pickle.dump((self.vectorizer, self.knn, ids, game_names), f)
        print("Modelo treinado e salvo.")

    def load_model(self):
        with open(self.model_path, "rb") as f:
            self.vectorizer, self.knn, self.ids, self.game_names = pickle.load(f)
        print("Modelo carregado com sucesso.")

    def encontrar_jogo(self, rom_name):
        nome_rom_limpo = self.limpar_nome(rom_name)
        vetor = self.vectorizer.transform([nome_rom_limpo])
        distancia, indice = self.knn.kneighbors(vetor)

        if 1 - distancia[0][0] >= 0.90:
            return self.ids[indice[0][0]], self.game_names[indice[0][0]]
        return None, None

    def validar_modelo(self, jogos_teste):
        acertos = 0
        total = len(jogos_teste)

        for rom_name, nome_esperado in jogos_teste:
            id_jogo, nome_jogo_predito = self.encontrar_jogo(rom_name)

            if nome_jogo_predito == nome_esperado:
                acertos += 1

            print(f"ROM: {rom_name}")
            print(f"Esperado: {nome_esperado}")
            print(f"Predito: {nome_jogo_predito}")
            print(f"Acurácia: {1 - (acertos / total)}")
            print("-" * 50)

        percentual_acerto = (acertos / total) * 100
        print(f"Percentual de acertos: {percentual_acerto:.2f}%")

# Exemplo de uso
if __name__ == "__main__":
    retro_ai = RetroArchAI()
    lista_ftp = FTPManager().list_files("/dev_hdd0/ROMS/snes")
    jogos_teste = [(rom, rom.split(".")[0]) for rom in lista_ftp]
    print(jogos_teste)
    # Lista de jogos para teste (exemplo)
    #jogos_teste = [("mariopntu1.zip", "Mario Paint"),("supermario.smc", "Super Mario World"),("zelda.zip", "The Legend of Zelda: A Link to the Past")    ]
    retro_ai.validar_modelo(jogos_teste)
    print()

# Exemplo de uso
"""
if __name__ == "__main__":
    ftp_manager = FTPManager()
    db_path = "C:\\Users\\Amozin\\Python\\Retroarch\\data\\downloads\\FBNE00123\\USRDIR\\retro.db"
    ftp_roms_path = "/dev_hdd0/ROMS/snes"
    core_id = 2
    xml_path = "d:/Games/roms/snes/Super Nintendo.dat"
    rom_manager = ROMManagerAI(db_path, ftp_manager, ftp_roms_path, core_id)
    rom_manager.match_and_insert("Super Nintendo", xml_path)
    print("Concluído.")
"""