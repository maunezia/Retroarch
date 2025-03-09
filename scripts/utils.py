import os
import pandas as pd
import zipfile
import configparser

class PandasPklFixer:
    def __init__(self, pasta_pkl=r"C:\Users\Amozin\Python\Retroarch\data\pkls"):
        self.pasta_pkl = pasta_pkl
        self.colunas_para_alterar = ['cover', 'wheel', 'screenshot', 'marquee']

    def fix_path(self, path):
        return str(path).replace("E:", "D:")

    def load_roms(self, pkl_path):
        return pd.read_pickle(pkl_path)

    def save_roms(self, df, pkl_path):
        df.to_pickle(pkl_path)

    def rename_columns(self, df):
        mapeamento = {
            "Romname": "rom_name",
            "Nome do Jogo": "game_name",
            "Descrição": "description",
            "Data de Lançamento": "release_date",
            "Desenvolvedor": "developer",
            "Editora": "publisher",
            "Gênero": "genre",
            "Número de Jogadores": "players",
            "Capa": "cover",
            "Wheel": "wheel",
            "Screenshot": "screenshot",
            "Marquee": "marquee",
            "Nome do Arquivo": "file_name"
        }
        return df.rename(columns=mapeamento)

    def fix_pandas_pkl(self):
        for arquivo in os.listdir(self.pasta_pkl):
            if arquivo.endswith('.pkl'):
                pkl_path = os.path.join(self.pasta_pkl, arquivo)
                df = self.load_roms(pkl_path)
                df = self.rename_columns(df)
                for coluna in self.colunas_para_alterar:
                    if coluna in df.columns:
                        df[coluna] = df[coluna].apply(self.fix_path)
                self.save_roms(df, pkl_path)
                print(f"Arquivo atualizado: {arquivo}")

class ZipExtractor:
    def __init__(self, zip_file=None, path_destino="./data/temp"):
        self.zip_file = zip_file
        self.path_destino = path_destino
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.zip_dir = config['Paths']['zip_dir']
        self.path_destino = config['Paths']['extract_dir']

    def extract_zip(self):
        if not self.zip_file:
            print("Nenhum arquivo zip especificado.")
            return

        zip_path = os.path.join(self.zip_dir, self.zip_file)
        if not os.path.exists(zip_path):
            print(f"Arquivo zip : {zip_path} não encontrado.")
            return

        #extract_path = os.path.join(self.path_destino, os.path.splitext(os.path.basename(zip_path))[0])
        extract_path = self.path_destino

        if os.path.exists(extract_path):
            required_dirs = ['covers', 'marquees', 'screenshots', 'textual', 'wheels']
            if all(os.path.exists(os.path.join(extract_path, d)) for d in required_dirs):
                print("Diretório existente.")
                return

        if not os.path.exists(extract_path):
            os.makedirs(extract_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            total_files = len(zip_ref.infolist())
            for i, file in enumerate(zip_ref.infolist(), 1):
                zip_ref.extract(file, extract_path)
                if i % 100 == 0 or i == total_files:
                    print(f"Descompactando arquivos: {i} de {total_files}")
            zip_ref.extractall(extract_path)
        print(f"Arquivo {zip_path} descompactado em {extract_path}")

if __name__ == "__main__":
    pandas_pkl_fixer = PandasPklFixer()
    pandas_pkl_fixer.fix_pandas_pkl()
    #zip_extractor = ZipExtractor(zip_file='media.zip')
    #zip_extractor.extract_zip()
    print("Fim do script.")