import os
import json
import pygame
import textwrap

class GameImageEditor:
    def __init__(self, config, game_data):
        # Carrega configurações gerais
        self.config = config
        frame = config.get("frame", {})
        self.width = frame.get("width", 800)
        self.height = frame.get("height", 800)
        self.bg_color = tuple(frame.get("color", [0, 0, 0]))
        self.font_path = config.get("font", {}).get("path","font.ttf")
        
        # Dados do jogo
        self.game_data = game_data
        
        # Inicializa o pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Editor de Imagens")
        self.clock = pygame.time.Clock()
        
        # Carrega os elementos: imagens, textos, rating e players
        self.elements = {}
        self.load_images()
        self.load_texts()
        self.load_rating()
        self.load_players()
        
        # Ordena os elementos pelo "z"
        self.update_edit_order()
        self.selected_element = self.edit_order[-1]
        
        self.running = True
        self.output = "output_image.png"
    
    def load_images(self):
        # Carrega imagens dinâmicas (logo, cover, wheel, screenshot)
        for key, conf in self.config.get("images", {}).items():
            img_obj = None
            path = conf.get("path", "")
            if os.path.exists(path):
                img_obj = pygame.image.load(path).convert_alpha()
            elif conf.get("default") and os.path.exists(conf.get("default")):
                img_obj = pygame.image.load(conf.get("default")).convert_alpha()
            self.elements[key] = {
                "type": "image",
                "image": img_obj,
                "x": conf.get("x", 0),
                "y": conf.get("y", 0),
                "z": conf.get("z", 0),
                "scale": conf.get("size", 1.0),
                "rotation": conf.get("rotation", 0),
                "area": conf.get("area")  # [width, height] área designada
            }
    
    def load_texts(self):
        # Carrega textos: game_name e game_description
        for key, conf in self.config.get("texts", {}).items():
            content = self.game_data.get(key, "")
            self.elements[key] = {
                "type": "text",
                "text": content,
                "x": conf.get("x", 0),
                "y": conf.get("y", 0),
                "z": conf.get("z", 0),
                "font_size": conf.get("font_size", 20),
                "color": tuple(conf.get("color", [255, 255, 255])),
                "area": conf.get("area")  # [width, height] para quebra de linha
            }
    
    def load_rating(self):
        # Configuração do rating (score em estrelas)
        conf = self.config.get("rating", {})
        score = float(self.game_data.get("rating", 0))

        if score > 10:
            score = round(score / 10, 1)

        if score > 5 and score <= 10:
            score /= 2
        
        if score < 1:
            score = score * 10 / 2

        # Ajusta valores flutuantes para o comportamento desejado
        if score > 0.1 and score % 1 != 0:
            score = int(score) + 0.5
        
        score = min(max(score, 0), 5)

        self.elements["rating"] = {
            "type": "rating",
            "score": score,
            "x": conf.get("x", 80),
            "y": conf.get("y", 495),
            "z": conf.get("z", 5),
            "scale": conf.get("size", 1.0),
            "star_full": conf.get("star_full", "star_full.png"),
            "star_half": conf.get("star_half", "star_half.png"),
            "star_empty": conf.get("star_empty", "star_empty.png")
        }
        # Carrega as imagens das estrelas, se existirem
        for star in ["star_full", "star_half", "star_empty"]:
            path = self.elements["rating"][star]
            if os.path.exists(path):
                self.elements["rating"][star + "_img"] = pygame.image.load(path).convert_alpha()
            else:
                self.elements["rating"][star + "_img"] = None
    
    def load_players(self): 
        # Seleciona ícone de players conforme o número informado (string pode conter dígitos)
        players_str = self.game_data.get("players", "1")
        path_single = self.config.get("players", {}).get("single", "data/images/sp.png")
        path_multi = self.config.get("players", {}).get("multi", "data/images/mp.png")
        count = 1
        if players_str.isdigit():
            count = int(players_str)
        else:
            for c in players_str:
                if c.isdigit() and int(c) > count:
                    count = int(c)
        players_conf = self.config.get("players", {})
        path = players_conf.get("single", path_single) if count <= 1 else players_conf.get("multi", path_multi)
        img_obj = None
        if os.path.exists(path):
            img_obj = pygame.image.load(path).convert_alpha()
        
        # Define posição inicial e ajusta se necessário
        x = players_conf.get("x", 15)
        y = players_conf.get("y", 485)
        if img_obj:
            img_width, img_height = img_obj.get_size()
            if x + img_width > self.width or y + img_height > self.height:
                # Reposiciona para o canto inferior direito
                x = self.width - img_width - 10  # Margem de 10px
                y = self.height - img_height - 10  # Margem de 10px
        
        self.elements["players"] = {
            "type": "image",
            "image": img_obj,
            "x": x,
            "y": y,
            "z": players_conf.get("z", 3),
            "scale": players_conf.get("size", 0.5),
            "rotation": players_conf.get("rotation", 0),
            "single": players_conf.get("single", path_single),
            "multi": players_conf.get("multi", path_single),
            "area": players_conf.get("area", [100, 100])
        }
    
    def update_edit_order(self):
        self.edit_order = sorted([k for k in self.elements.keys() if self.elements[k] is not None],
                                   key=lambda k: self.elements[k]["z"])
    
    def draw_text_wrapped(self, text, font, color, area):
        # Utiliza textwrap para quebrar o texto e desenha dentro da área
        max_width, max_height = area
        # Calcula o número máximo de caracteres por linha com base no tamanho da fonte e na largura da área
        char_width = font.size("A")[0]  # Largura aproximada de um caractere
        max_chars_per_line = max(50, max_width // char_width)  # Garante pelo menos 1 caractere por linha
        wrapper = textwrap.TextWrapper(width=max_chars_per_line)

        lines = wrapper.wrap(text=text)
        rendered_lines = []
        for line in lines:
            rendered_lines.append(font.render(line, True, color))
        return rendered_lines
    
    def update(self, draw_selection=True):
        self.screen.fill(self.bg_color)
        sorted_elements = sorted(self.elements.items(), key=lambda item: item[1]["z"])
        for key, elem in sorted_elements:
            if elem["type"] == "image" and elem.get("image"):
                img = elem["image"]
                # Se houver área definida, redimensiona para caber sem distorção
                if elem.get("area"):
                    area = tuple(elem["area"])
                    img = self.resize_to_fit(img, area)
                if elem["scale"] != 1.0:
                    new_size = (int(img.get_width() * elem["scale"]), int(img.get_height() * elem["scale"]))
                    img = pygame.transform.smoothscale(img, new_size)
                if elem["rotation"]:
                    img = pygame.transform.rotate(img, elem["rotation"])
                self.screen.blit(img, (int(elem["x"]), int(elem["y"])))
                if draw_selection and key == self.selected_element:
                    rect = img.get_rect(topleft=(int(elem["x"]), int(elem["y"])))
                    pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)

            elif elem["type"] == "text":
                font = pygame.font.Font(self.font_path, elem["font_size"])
                if elem.get("area"):
                    rendered = self.draw_text_wrapped(elem["text"], font, elem["color"], tuple(elem["area"]))
                    x = elem["x"]
                    y = elem["y"]
                    for line in rendered:
                        self.screen.blit(line, (x, y))
                        y += line.get_height()
                    if draw_selection and key == self.selected_element:
                        pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(elem["x"], elem["y"], elem["area"][0], elem["area"][1]), 2)
                
                else:
                    text_surf = font.render(elem["text"], True, elem["color"])
                    self.screen.blit(text_surf, (elem["x"], elem["y"]))
                    if draw_selection and key == self.selected_element:
                        rect = text_surf.get_rect(topleft=(elem["x"], elem["y"]))
                        pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)

            elif elem["type"] == "rating":
                self.draw_rating(elem)

            elif elem["type"] == "players" and elem.get("image"):
                img = elem["image"]
                # Se houver área definida, redimensiona para caber sem distorção
                if elem.get("area"):
                    area = tuple(elem["area"])
                    img = self.resize_to_fit(img, area)
                if elem["scale"] != 1.0:
                    new_size = (int(img.get_width() * elem["scale"]), int(img.get_height() * elem["scale"]))
                    img = pygame.transform.smoothscale(img, new_size)
                if elem["rotation"]:
                    img = pygame.transform.rotate(img, elem["rotation"])
                self.screen.blit(img, (int(elem["x"]), int(elem["y"])))
                if draw_selection and key == self.selected_element:
                    rect = img.get_rect(topleft=(int(elem["x"]), int(elem["y"])))
                    pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)
    
        pygame.display.set_caption(f"Editor de Imagens - Selecionado: {self.selected_element}")

    def resize_to_fit(self, image, area):
        # Redimensiona a imagem mantendo proporção para caber em 'area'
        iw, ih = image.get_size()
        aw, ah = area
        scale = min(aw/iw, ah/ih)
        new_size = (int(iw * scale), int(ih * scale))
        return pygame.transform.smoothscale(image, new_size)
    
    def draw_rating(self, elem):
        # Desenha as estrelas de rating
        score = elem["score"]
        full = int(score)
        half = 1 if score - full >= 0.5 else 0
        empty = 5 - full - half
        star_size = int(30 * elem.get("scale", 1.0))
        x = elem["x"]
        y = elem["y"]
        spacing = 5
        for i in range(full):
            star = elem.get("star_full_img")
            if star:
                star = pygame.transform.smoothscale(star, (star_size, star_size))
                self.screen.blit(star, (x + i * (star_size + spacing), y))
        if half:
            star = elem.get("star_half_img")
            if star:
                star = pygame.transform.smoothscale(star, (star_size, star_size))
                self.screen.blit(star, (x + full * (star_size + spacing), y))
        for i in range(empty):
            star = elem.get("star_empty_img")
            if star:
                star = pygame.transform.smoothscale(star, (star_size, star_size))
                self.screen.blit(star, (x + (full + half + i) * (star_size + spacing), y))
        # Desenha retângulo de seleção se for o elemento selecionado
        if self.selected_element == "rating":
            total_width = 5 * (star_size + spacing) - spacing
            rect = pygame.Rect(x, y, total_width, star_size)
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)
    
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                elem = self.elements[self.selected_element]
                # Se CTRL estiver pressionado (sem ALT) para escala, fonte e rotação
                if mods & pygame.KMOD_CTRL and not (mods & pygame.KMOD_ALT):
                    if event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                        if elem["type"] == "image":
                            elem["scale"] += 0.1
                        elif elem["type"] == "text":
                            elem["font_size"] += 1
                    elif event.key == pygame.K_MINUS:
                        if elem["type"] == "image":
                            elem["scale"] = max(0.1, elem["scale"] - 0.1)
                        elif elem["type"] == "text":
                            elem["font_size"] = max(1, elem["font_size"] - 1)

                    elif event.key == pygame.K_r:
                        elem["rotation"] += 5
                    elif event.key == pygame.K_t:
                        elem["rotation"] -= 5
                    elif event.key == pygame.K_s:
                        self.save_json()
                        self.save_image()
                # Se CTRL+ALT estiverem pressionados para alterar o z-index
                elif (mods & pygame.KMOD_CTRL) and (mods & pygame.KMOD_ALT):
                    if event.key == pygame.K_UP:
                        elem["z"] += 1
                        self.update_edit_order()
                    elif event.key == pygame.K_DOWN:
                        elem["z"] = max(0, elem["z"] - 1)
                        self.update_edit_order()
                # Sem modificadores: mover posição com as setas e alternar elemento com TAB
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Botão esquerdo do mouse
                        mouse_x, mouse_y = event.pos
                        for key, elem in reversed(sorted(self.elements.items(), key=lambda item: item[1]["z"])):
                            if elem["type"] == "image" and elem.get("image"):
                                img_rect = elem["image"].get_rect(topleft=(elem["x"], elem["y"]))
                                if img_rect.collidepoint(mouse_x, mouse_y):
                                    self.selected_element = key
                                    self.dragging = True
                                    self.drag_offset_x = mouse_x - elem["x"]
                                    self.drag_offset_y = mouse_y - elem["y"]
                                    break
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Botão esquerdo do mouse
                        self.dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    if getattr(self, "dragging", False):
                        mouse_x, mouse_y = event.pos
                        elem = self.elements[self.selected_element]
                        elem["x"] = mouse_x - self.drag_offset_x
                        elem["y"] = mouse_y - self.drag_offset_y
                else:
                    if event.key == pygame.K_TAB:
                        idx = self.edit_order.index(self.selected_element)
                        self.selected_element = self.edit_order[(idx + 1) % len(self.edit_order)]
                    elif event.key == pygame.K_LEFT:
                        elem["x"] -= 5
                    elif event.key == pygame.K_RIGHT:
                        elem["x"] += 5
                    elif event.key == pygame.K_UP:
                        elem["y"] -= 5
                    elif event.key == pygame.K_DOWN:
                        elem["y"] += 5
        return self.running
    
    def save_json(self):
        # Atualiza a configuração com as posições e atributos atuais dos elementos
        for key, elem in self.elements.items():
            if elem["type"] == "image":
                if key in self.config.get("images", {}):
                    self.config["images"][key].update({
                        "x": elem["x"],
                        "y": elem["y"],
                        "z": elem["z"],
                        "size": elem["scale"],
                        "rotation": elem["rotation"]
                    })

            elif elem["type"] == "text":
                if key in self.config.get("texts", {}):
                    self.config["texts"][key].update({
                        "x": elem["x"],
                        "y": elem["y"],
                        "z": elem["z"],
                        "font_size": elem["font_size"]
                    })
            elif elem["type"] == "rating":
                self.config["rating"].update({
                    "x": elem["x"],
                    "y": elem["y"],
                    "z": elem["z"],
                    "size": elem["scale"] #,"score": elem["score"]
                })
            elif elem["type"] == "players":
                self.config["players"][key].update({
                        "x": elem["x"],
                        "y": elem["y"],
                        "z": elem["z"],
                        "size": elem["scale"],
                        "rotation": elem["rotation"],
                        "single": elem["single"],
                        "multi": elem["multi"],
                        "area": elem["area"]
                    })


        with open("updated_config.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        print("Configuração salva em updated_config.json")
    
    def save_image(self):
        self.update(draw_selection=False)
        pygame.image.save(self.screen, self.output)
        print(f"Imagem salva em {self.output}")
    
    def run(self):
        while self.running:
            self.process_events()
            self.update()
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

if __name__ == "__main__":
    # Exemplo de configuração inicial via JSON
    
    if os.path.exists("updated_config.json"):
        with open("updated_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            # Exemplo de dados do jogo

    game_data = {
        "game_name": "Street Fighter II",
        "game_description": "Street Fighter II foi lançado originalmente para Arcade em 1991 com o subtítulo 'The World Warrior'. Revolucionou os jogos de luta com seus movimentos especiais e personagens icônicos, marcando uma era nos games.",
        "rating": "0.80",
        "players": "1"
    }
    
    editor = GameImageEditor(config, game_data)
    # Para modo interativo, utilize editor.run(). Para salvar diretamente, chame save_image() e save_json().
    mode_interativo = True
    if mode_interativo:
        editor.run()
    else:
        editor.save_image()
        editor.save_json()
