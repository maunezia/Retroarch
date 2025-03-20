import os
import configparser
import pandas as pd

class GameDataInsights:
    def __init__(self, config_path="config.ini"):
        self.config = self._load_config(config_path)
        # Configura caminhos padrões para os dados a partir do config.ini
        self.roms_path = self.config.get('DATA', 'roms_path', fallback='fbneo.pkl')
        self.games_path = self.config.get('DATA', 'games_path', fallback='games.csv')
        self.roms = None
        self.games_df = None

    def _load_config(self, config_path):
        """
        Carrega as configurações do arquivo config.ini.
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def load_pkl_roms(self, path=None):
        """
        Carrega ROMs a partir de um arquivo pickle.
        """
        if path is None:
            path = self.roms_path
        print('Carregando ROMs...')
        self.roms = pd.read_pickle(path)
        return self.roms

    def load_games_df(self, path=None):
        """
        Carrega os dados dos games em um DataFrame.
        """
        if path is None:
            path = self.games_path
        print('Carregando dados dos games...')
        self.games_df = pd.read_csv(path)
        return self.games_df

    def get_summary_stats(self):
        """
        Retorna estatísticas descritivas dos dados dos games.
        """
        if self.games_df is None:
            self.load_games_df()
        return self.games_df.describe()

    def filter_by_genre(self, genre):
        """
        Filtra os games por gênero.
        """
        if self.games_df is None:
            self.load_games_df()
        return self.games_df[self.games_df['genre'] == genre]

    def top_n_games(self, n=10, sort_by="rating"):
        """
        Retorna os top n games baseados na coluna especificada (ex: rating).
        """
        if self.games_df is None:
            self.load_games_df()
        return self.games_df.sort_values(by=sort_by, ascending=False).head(n)

# Exemplo de uso:
if __name__ == '__main__':
    insights = GameDataInsights("config.ini")
    roms = insights.load_pkl_roms()
    games = insights.load_games_df()
    print("Estatísticas descritivas dos games:")
    print(insights.get_summary_stats())
    print("Top 5 games por rating:")
    print(insights.top_n_games(n=5, sort_by="rating"))
