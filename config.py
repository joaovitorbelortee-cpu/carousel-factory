import os

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_DIR = os.path.join(OUTPUT_DIR, "logs")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")

# Configurações de Vídeo - LANDSCAPE 1920x1080
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

# Configurações de TTS
TTS_VOICE = "pt-BR-FranciscaNeural"
TTS_RATE = "+15%"
VOICE_SPEED = TTS_RATE

# Configurações de Conteúdo
DEFAULT_TOPIC = "Pack de Ferramentas de IA"
NUM_VIDEOS = 5

# Configurações de Áudio
MUSIC_VOLUME = 0.15  # Volume da música de fundo (0.0 a 1.0)
VOICE_VOLUME = 1.0   # Volume da narração