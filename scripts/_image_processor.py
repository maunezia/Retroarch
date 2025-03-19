# image_processor.py
"""
Funções para processar e gerar imagens personalizadas dos jogos.
Inclui geração de capas, logos, capturas de tela e imagens com descrições.
"""
import os
import configparser
from PIL import Image, ImageDraw, ImageFont

class GameDescriptionImageGenerator:
    def __init__(self, config_path="imagens.ini"):
        """
        Inicializa o gerador de imagens com base em um arquivo de configuração.

        :param config_path: Caminho para o arquivo de configuração.
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        self.width = int(self.config["IMAGE"]["width"])
        self.height = int(self.config["IMAGE"]["height"])
        self.font_path = self.config["FONT"]["path"]
        self.font_size = int(self.config["FONT"]["size"])
        self.text_color = self.config["FONT"]["color"]
        self.background_color = self.config["IMAGE"]["background_color"]
    
    def generate_image(self, logo, screenshot, wheel, cover, game_info, output_path):
        """
        Gera uma imagem com base nos parâmetros fornecidos.

        :param logo: Caminho para a imagem do logo.
        :param screenshot: Caminho para a imagem da captura de tela.
        :param wheel: Caminho para a imagem da roda.
        :param cover: Caminho para a imagem da capa.
        :param game_info: Dicionário com informações do jogo (título, jogadores, nota, descrição).
        :param output_path: Caminho para salvar a imagem gerada.
        """
        # Criar a imagem base
        img = Image.new("RGB", (self.width, self.height), self.background_color)
        draw = ImageDraw.Draw(img)
        
        # Carregar imagens
        logo_img = Image.open(logo).convert("RGBA")
        screenshot_img = Image.open(screenshot).convert("RGBA")
        wheel_img = Image.open(wheel).convert("RGBA")
        cover_img = Image.open(cover).convert("RGBA")
        
        # Redimensionar e posicionar elementos
        self._paste_image(img, screenshot_img, (int(self.width * 0.65), 0), (int(self.width * 0.35), self.height))
        self._paste_image(img, logo_img, (20, 20), (100, 100))
        self._paste_image(img, cover_img, (int(self.width * 0.65), int(self.height * 0.65)), (200, 300), rotate=-10)
        self._paste_image(img, wheel_img, (int(self.width * 0.80), int(self.height * 0.75)), (150, 150), rotate=90)
        
        # Adicionar texto (título e informações)
        font = ImageFont.truetype(self.font_path, self.font_size)
        draw.text((20, self.height - 150), game_info["title"], fill=self.text_color, font=font)
        draw.text((20, self.height - 120), f"Jogadores: {game_info['players']}", fill=self.text_color, font=font)
        draw.text((20, self.height - 90), f"Nota: {'★' * game_info['rating']}", fill=self.text_color, font=font)
        draw.text((20, self.height - 60), game_info["description"], fill=self.text_color, font=font)
        
        # Salvar a imagem
        img.save(output_path)
        print(f"Imagem salva em {output_path}")

    def _paste_image(self, base_img, img_to_paste, position, size, rotate=0):
        """
        Redimensiona e cola uma imagem em outra.

        :param base_img: Imagem base onde a outra imagem será colada.
        :param img_to_paste: Imagem a ser colada.
        :param position: Posição onde a imagem será colada.
        :param size: Tamanho para redimensionar a imagem.
        :param rotate: Ângulo de rotação da imagem.
        """
        img_resized = img_to_paste.resize(size).rotate(rotate, expand=True)
        base_img.paste(img_resized, position, img_resized)
if __name__ == "__main__":
    config_path = "C:/Users/Amozin/Python/Retroarch/scripts/images.ini"
    generator = GameDescriptionImageGenerator(config_path)
    
    logo_path = "C:/Users/Amozin/Python/Retroarch/data/images/logo.png"
    screenshot_path = "C:/Users/Amozin/Python/Retroarch/data/images/screenshot.png"
    wheel_path = "C:/Users/Amozin/Python/Retroarch/data/images/wheel.png"
    cover_path = "C:/Users/Amozin/Python/Retroarch/data/images/cover.png"
    output_path = "C:/Users/Amozin/Python/Retroarch/data/images/game_description.png"
    
    import xml.etree.ElementTree as ET

    # Parse the XML content
    tree = ET.parse('C:/Users/Amozin/Python/Retroarch/data/images/content.xml')
    root = tree.getroot()

    # Extract game information
    game_info = {
        "title": root.find("name").text,
        "players": root.find("players").text,
        "rating": int((float(root.find("rating").text) * 10 ) / 2),  # Convert rating to a 5-star scale
        "description": root.find("desc").text
    }

    generator.generate_image(logo_path, screenshot_path, wheel_path, cover_path, game_info, output_path)