import os
import configparser
from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET

def open_and_convert(image_path):
    return Image.open(image_path).convert("RGBA")

def resize_proportionally(img, target_size, scale):
    target_size = (int(target_size[0] * scale), int(target_size[1] * scale))
    img.thumbnail(target_size, Image.Resampling.LANCZOS)
    return img

def paste_image(base_img, img_to_paste, position, size, rotate=0, scale=1):
    img_to_paste = resize_proportionally(img_to_paste, size, scale)
    img_rotated = img_to_paste.rotate(rotate, expand=True)
    base_img.paste(img_rotated, position, img_rotated if img_rotated.mode == 'RGBA' else None)

def add_text(draw, text, position, font, color):
    draw.text(position, text, fill=color, font=font)

class GameDescriptionImageGenerator:
    def __init__(self, config_path="imagens.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        self.width = int(self.config["IMAGE"]["width"])
        self.height = int(self.config["IMAGE"]["height"])
        self.font_path = self.config["FONT"]["path"]
        self.font_size = int(self.config["FONT"]["size"])
        self.text_color = self.config["FONT"]["color"]
        self.background_color = self.config["IMAGE"]["background_color"]
    
    def generate_image(self, logo, screenshot, wheel, cover, game_info, output_path):
        img = Image.new("RGB", (self.width, self.height), self.background_color)
        draw = ImageDraw.Draw(img)
        
        logo_img = open_and_convert(logo)
        screenshot_img = open_and_convert(screenshot)
        wheel_img = open_and_convert(wheel)
        cover_img = open_and_convert(cover)
        
        screenshot_size = (self.width // 2, self.height // 2)
        paste_image(img, screenshot_img, self._get_position("screenshot"), screenshot_size, rotate=self._get_rotation("screenshot"), scale=self._get_scale("screenshot"))
        paste_image(img, logo_img, self._get_position("logo"), (150, 150), rotate=self._get_rotation("logo"), scale=self._get_scale("logo"))
        paste_image(img, cover_img, self._get_position("cover"), (200, 300), rotate=self._get_rotation("cover"), scale=self._get_scale("cover"))
        paste_image(img, wheel_img, self._get_position("wheel"), (150, 150), rotate=self._get_rotation("wheel"), scale=self._get_scale("wheel"))
        
        font = ImageFont.truetype(self.font_path, self.font_size)
        text_y = self.height - 340
        add_text(draw, game_info["title"], (20, text_y), font, self.text_color)
        add_text(draw, f"Jogadores: {game_info['players']}", (20, text_y + 30), font, self.text_color)
        add_text(draw, f"Nota: {'★' * game_info['rating']}", (20, text_y + 60), font, self.text_color)
        add_text(draw, game_info["description"], (20, text_y + 90), font, self.text_color)
        
        img.save(output_path)
        print(f"Imagem salva em {output_path}")

    def _get_rotation(self, image_type):
        return int(self.config["ROTATION"].get(image_type, 0))
    
    def _get_scale(self, image_type):
        return float(self.config["SIZE"].get(image_type, 1))
    
    def _get_position(self, image_type):
        position = self.config["POSITION"].get(image_type, "0,0").split(",")
        return (int(float(position[0]) * self.width), int(float(position[1]) * self.height))

if __name__ == "__main__":
    config_path = "C:/Users/Amozin/Python/Retroarch/scripts/images.ini"
    generator = GameDescriptionImageGenerator(config_path)
    
    logo_path = "C:/Users/Amozin/Python/Retroarch/data/images/logo.png"
    screenshot_path = "C:/Users/Amozin/Python/Retroarch/data/images/screenshot.png"
    wheel_path = "C:/Users/Amozin/Python/Retroarch/data/images/wheel.png"
    cover_path = "C:/Users/Amozin/Python/Retroarch/data/images/cover.png"
    output_path = "C:/Users/Amozin/Python/Retroarch/data/images/game_description.png"
    
    tree = ET.parse('C:/Users/Amozin/Python/Retroarch/data/images/content.xml')
    root = tree.getroot()
    
    game_info = {
        "title": root.find("name").text,
        "players": root.find("players").text,
        "rating": int((float(root.find("rating").text) * 10 ) / 2),
        "description": root.find("desc").text
    }
    
    generator.generate_image(logo_path, screenshot_path, wheel_path, cover_path, game_info, output_path)
