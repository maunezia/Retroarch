import os
import configparser
import pandas as pd

class GameDataAggregator:
    def __init__(self, pkl_directory, config_path="config.ini"):
        self.pkl_directory = pkl_directory
        self.config_path = config_path
        self.roms_filename = "roms.pkl"
        self.roms_path = os.path.join(self.pkl_directory, self.roms_filename)
        self.config = self._load_or_create_config()

    def _load_or_create_config(self):
        """
        Carrega o conteúdo do arquivo config.ini se existir, caso contrário cria um novo.
        Retorna o objeto ConfigParser.
        """
        config = configparser.ConfigParser()
        if os.path.exists(self.config_path):
            config.read(self.config_path)
        else:
            # Cria um arquivo vazio se não existir
            with open(self.config_path, "w") as f:
                config.write(f)
        return config

    def get_existing_filter_columns(self):
        """
        Retorna os valores existentes na seção 'FILTERS' do config.ini, se houver.
        """
        section = "FILTERS"
        if self.config.has_section(section):
            columns = self.config.get(section, "columns", fallback="")
            return [col.strip() for col in columns.split(",") if col.strip()]
        return []

    def aggregate_pkls(self):
        """
        Carrega todos os arquivos .pkl (exceto o roms.pkl) do diretório, concatena em um DataFrame
        e salva como roms.pkl. Também lê os valores atuais do config.ini e, em seguida, grava
        os nomes das colunas em uma seção 'FILTERS'.
        """
        pkl_files = [
            os.path.join(self.pkl_directory, f)
            for f in os.listdir(self.pkl_directory)
            if f.endswith('.pkl') and f != self.roms_filename
        ]

        if not pkl_files:
            print("Nenhum arquivo .pkl encontrado no diretório (exceto roms.pkl).")
            return None

        dataframes = [pd.read_pickle(f) for f in pkl_files]
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df.to_pickle(self.roms_path)
        print(f"Arquivo '{self.roms_filename}' criado com {len(combined_df)} registros.")

        # Obtém os valores atuais antes de salvar os novos
        existing_columns = self.get_existing_filter_columns()
        print(f"Colunas existentes no config.ini: {existing_columns}")
        self._save_columns_to_config(combined_df.columns)
        return combined_df

    def _save_columns_to_config(self, columns):
        """
        Salva os nomes das colunas do DataFrame na seção 'FILTERS' do arquivo config.ini.
        """
        section = "FILTERS"
        if not self.config.has_section(section):
            self.config.add_section(section)
        # Atualiza as colunas com os novos valores (lista separada por vírgulas).
        self.config.set(section, "columns", ",".join(columns))
        with open(self.config_path, "w") as configfile:
            self.config.write(configfile)
        print(f"Colunas salvas na seção '{section}' do arquivo '{self.config_path}'.")

# Exemplo de uso:
if __name__ == '__main__':
    aggregator = GameDataAggregator(pkl_directory="data/pkls", config_path="config.ini")
    aggregator.aggregate_pkls()
