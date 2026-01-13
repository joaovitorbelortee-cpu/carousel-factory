"""
Configurações centralizadas do Viral Bot
Carrega variáveis de ambiente do arquivo .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Configurações centralizadas."""
    
    # Servidor Web
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    # Geração de Vídeo
    DEFAULT_NICHE = os.getenv("DEFAULT_NICHE", "ai_tools")
    DEFAULT_VIDEO_COUNT = int(os.getenv("DEFAULT_VIDEO_COUNT", 5))
    MAX_VIDEO_COUNT = int(os.getenv("MAX_VIDEO_COUNT", 10))
    VIDEO_RESOLUTION = os.getenv("VIDEO_RESOLUTION", "1920x1080")
    
    # TTS
    TTS_VOICE = os.getenv("TTS_VOICE", "pt-BR-AntonioNeural")
    TTS_RATE = os.getenv("TTS_RATE", "+15%")
    
    # Cache
    CACHE_HOURS = int(os.getenv("CACHE_HOURS", 6))
    CACHE_DIR = BASE_DIR / os.getenv("CACHE_DIR", ".tmp/cache")
    
    # Output
    OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "output")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 10))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
    
    @classmethod
    def validate(cls):
        """Valida configurações críticas."""
        errors = []
        
        if cls.MAX_VIDEO_COUNT < 1:
            errors.append("MAX_VIDEO_COUNT deve ser >= 1")
        
        if cls.FLASK_PORT < 1 or cls.FLASK_PORT > 65535:
            errors.append("FLASK_PORT deve estar entre 1 e 65535")
        
        if errors:
            raise ValueError(f"Erros de configuração: {', '.join(errors)}")
        
        return True


# Criar diretórios necessários
Config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Validar ao importar
Config.validate()
