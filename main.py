# main.py
#Script principal para orquestrar o projeto RetroArch.
#Executa todas as etapas necessárias para organizar ROMs, gerar imagens, playlists e wallpapers.
from scripts import DataLoader, ImageProcessor, PlaylistCreator, WallpaperGenerator, FTPUploader

def main():
    # Carregar dados
    data_loader = DataLoader('data/pkl/dataset.pkl')
    data = data_loader.load_data()
    
    # Processar imagens
    image_processor = ImageProcessor(data, 'data/images/')
    image_processor.process_images()
    
    # Gerar playlists
    playlist_creator = PlaylistCreator(data, 'data/playlists/')
    playlist_creator.create_playlists()
    
    # Gerar wallpapers
    wallpaper_generator = WallpaperGenerator(data, 'data/images/wallpapers/')
    wallpaper_generator.generate_wallpapers()
    
    # Fazer upload via FTP
    ftp_uploader = FTPUploader('ftp_host', 'username', 'password')
    ftp_uploader.upload_files('data/playlists/', '/remote/playlists/')
    ftp_uploader.upload_files('data/images/', '/remote/images/')
    
    # Alterar configurações do retroarch.cfg
    # Você pode criar um módulo separado para isso, por exemplo, 'config_modifier.py'

if __name__ == "__main__":
    main()
    print('Processo concluído.')
