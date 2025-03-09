import pandas as pd
#Funções para carregar ROMs e DataFrames.
#Exemplo de uso:

def load_pkl_roms(path):
    print('Carregando ROMs...')
    roms = pd.read_pickle(path)
    return roms

