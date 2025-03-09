- 👋 Hi, I’m @maunezia I'm a game streamer based in Vancouver
- 👀 primarily playing Apex Legends and exploring various genres like action RPGs, racing, and strategy games.
- 🌱 I’m passionate about retro games and love discussing classic titles for hours.
- 💞️ My goal is to become a top-tier streamer and eventually open a game store.
- 📫 twitch.tv/maunezia 
- 😄 Pronouns: Call Torta, Se liga na play, Rusha e Morre
- ⚡ Fun fact: My streaming are the mojority in Brazillian Portuguese, but are some cases that I interact with the english speakers.

💻 Projects & Development
I’m currently developing a custom project for RetroArch to organize and showcase my ROM collection. The project includes:
Generating personalized covers and dynamic wallpapers for each playlist.
Creating playlists categorized by consoles, handhelds, and arcades (with subgenres like beat 'em up, fighting, adventure, and adult games).
Analyzing game images and utilizing Pandas DataFrames to manage game information.
Automating the generation of descriptions, ratings, and genre visuals.
Interacting with a PS3 via FTP to test playlists and assets in real-time.
Consolidating fragmented scripts into a single, maintainable project.
This project will be continuously improved and is hosted on GitHub to ensure long-term development and version control.

🔧 Skills & Tools:
Python (automation, data processing, image manipulation)
Pandas, Pillow, and FTP integration
Git & GitHub for version control
Content creation and community building through Twitch and social media
🚀 Future Goals:
Expand my game streaming audience.
Develop a vibrant gaming community in Vancouver.
Improve the RetroArch project with enhanced visuals and user-friendly features.

# RetroArch Project

Este projeto organiza ROMs, gera playlists e imagens personalizadas para RetroArch.

## Estrutura

- **Banco de dados de ROMs (pkl)**: Armazena informações detalhadas sobre cada ROM em um formato de arquivo pickle.
- **Playlists organizadas por sistema e categoria**: Criação automática de playlists para diferentes sistemas e categorias de jogos.
- **Imagens personalizadas**: Geração de capas, logos, capturas de tela e outras imagens personalizadas para cada ROM.
- **Wallpapers dinâmicos para RetroArch**: Criação de wallpapers dinâmicos para uso no RetroArch.

## Estrutura de Diretórios

```
Retroarch/
├── README.md
├── main.py
├── requirements.txt
├── data/
│   ├── roms.pkl
│   ├── playlists/
│   └── images/
│       ├── covers/
│       ├── logos/
│       └── screenshots/
├── config/
│   ├── settings.ini
│   └── systems/
├── scripts/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── ftp_uploader.py
│   ├── generate_playlists.py
│   ├── create_images.py
│   ├── image_processor.py
│   ├── playlist_creator.py
│   ├── update_database.py
│   ├── utils.py
│   └── wallpaper_generator.py
```

## Como usar

1. Execute `main.py` para iniciar o processo.
2. As pastas e arquivos necessários serão criados automaticamente.
3. Preencha as pastas com seus dados e reexecute o script para gerar conteúdo.

## Panorama do Projeto

O projeto RetroArch visa facilitar a organização e personalização de ROMs para o emulador RetroArch. Ele automatiza a criação de playlists e a geração de imagens personalizadas, proporcionando uma experiência visualmente agradável e organizada para os usuários.

### Funcionalidades

- **Organização de ROMs**: Criação de um banco de dados em formato pickle (.pkl) para armazenar informações sobre as ROMs.
- **Geração de Playlists**: Criação automática de playlists organizadas por sistema e categoria.
- **Imagens Personalizadas**: Geração de capas, logos, capturas de tela e outras imagens personalizadas para cada ROM.
- **Wallpapers Dinâmicos**: Criação de wallpapers dinâmicos para uso no RetroArch.
- **Configuração Personalizável**: Leitura de arquivos INI para configurar caminhos, extensões de ROMs, filtros de gênero e outras opções.
- **Suporte a Múltiplos Sistemas**: Suporte para diferentes sistemas de ROMs, permitindo a criação de playlists específicas para cada console.

### TODO

- [ ] Implementar suporte para novos sistemas de ROMs.
- [ ] Adicionar mais opções de personalização de imagens.
- [ ] Melhorar a interface de usuário para configuração do script.
- [ ] Criar documentação detalhada para desenvolvedores contribuírem com o projeto.
- [ ] Otimizar o desempenho do script para grandes coleções de ROMs.

### Informações Adicionais

Para contribuir com o projeto, por favor, siga as diretrizes de contribuição disponíveis no repositório. Se encontrar algum problema ou tiver sugestões, abra uma issue no GitHub.

**Requisitos**:
- Python 3.x
- Bibliotecas adicionais listadas em `requirements.txt`

**Licença**:
Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.