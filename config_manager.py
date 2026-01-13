"""
Config Manager - Gerenciamento centralizado de configurações (BMad-CORE: Modularize)
Permite configurações via arquivo .env, JSON ou variáveis de ambiente
"""

import os
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class VideoConfig:
    """Configurações de vídeo."""
    width: int = 1080
    height: int = 1920
    fps: int = 30
    format: str = "mp4"
    codec: str = "libx264"
    bitrate: str = "4M"


@dataclass
class TTSConfig:
    """Configurações de TTS."""
    voice_feminina: str = "pt-BR-FranciscaNeural"
    voice_masculina: str = "pt-BR-AntonioNeural"
    default_voice: str = "masculina"
    rate: str = "+10%"
    pitch: str = "+0Hz"


@dataclass
class ContentConfig:
    """Configurações de conteúdo."""
    nicho: str = "Pack de Ferramentas de IA"
    num_videos: int = 5
    num_tools_per_video: int = 5
    use_trends: bool = True
    hashtags_tiktok: int = 10
    hashtags_instagram: int = 15


@dataclass
class SchedulerConfig:
    """Configurações do scheduler."""
    enabled: bool = True
    generation_time: str = "06:00"
    post_times_tiktok: list = field(default_factory=lambda: ["12:00", "19:00", "21:00"])
    post_times_instagram: list = field(default_factory=lambda: ["11:00", "13:00", "19:00"])


@dataclass
class Config:
    """Configurações globais do Viral Bot."""
    video: VideoConfig = field(default_factory=VideoConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    content: ContentConfig = field(default_factory=ContentConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    
    # Paths
    output_dir: str = "output"
    assets_dir: str = "output/assets"
    cache_dir: str = "cache"
    logs_dir: str = "output/logs"
    
    # Debug
    debug: bool = False
    verbose: bool = True


class ConfigManager:
    """Gerenciador de configurações."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = Config()
        self._load_from_env()
        self._load_from_file()
    
    def _load_from_env(self):
        """Carrega configurações de variáveis de ambiente."""
        # Video
        if os.getenv("VIDEO_WIDTH"):
            self.config.video.width = int(os.getenv("VIDEO_WIDTH"))
        if os.getenv("VIDEO_HEIGHT"):
            self.config.video.height = int(os.getenv("VIDEO_HEIGHT"))
        if os.getenv("VIDEO_FPS"):
            self.config.video.fps = int(os.getenv("VIDEO_FPS"))
        
        # TTS
        if os.getenv("TTS_VOICE"):
            self.config.tts.default_voice = os.getenv("TTS_VOICE")
        if os.getenv("TTS_RATE"):
            self.config.tts.rate = os.getenv("TTS_RATE")
        
        # Content
        if os.getenv("NICHO"):
            self.config.content.nicho = os.getenv("NICHO")
        if os.getenv("NUM_VIDEOS"):
            self.config.content.num_videos = int(os.getenv("NUM_VIDEOS"))
        
        # Debug
        if os.getenv("DEBUG"):
            self.config.debug = os.getenv("DEBUG").lower() == "true"
        if os.getenv("VERBOSE"):
            self.config.verbose = os.getenv("VERBOSE").lower() == "true"
    
    def _load_from_file(self):
        """Carrega configurações de arquivo JSON."""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Video
            if "video" in data:
                for key, value in data["video"].items():
                    if hasattr(self.config.video, key):
                        setattr(self.config.video, key, value)
            
            # TTS
            if "tts" in data:
                for key, value in data["tts"].items():
                    if hasattr(self.config.tts, key):
                        setattr(self.config.tts, key, value)
            
            # Content
            if "content" in data:
                for key, value in data["content"].items():
                    if hasattr(self.config.content, key):
                        setattr(self.config.content, key, value)
            
            # Scheduler
            if "scheduler" in data:
                for key, value in data["scheduler"].items():
                    if hasattr(self.config.scheduler, key):
                        setattr(self.config.scheduler, key, value)
                        
        except Exception as e:
            print(f"⚠️ Erro ao carregar config: {e}")
    
    def save(self):
        """Salva configurações em arquivo JSON."""
        data = {
            "video": {
                "width": self.config.video.width,
                "height": self.config.video.height,
                "fps": self.config.video.fps,
                "format": self.config.video.format,
            },
            "tts": {
                "default_voice": self.config.tts.default_voice,
                "rate": self.config.tts.rate,
            },
            "content": {
                "nicho": self.config.content.nicho,
                "num_videos": self.config.content.num_videos,
                "use_trends": self.config.content.use_trends,
            },
            "scheduler": {
                "enabled": self.config.scheduler.enabled,
                "generation_time": self.config.scheduler.generation_time,
            },
            "debug": self.config.debug,
            "verbose": self.config.verbose,
        }
        
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração por chave."""
        parts = key.split(".")
        obj = self.config
        
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return default
        
        return obj
    
    def set(self, key: str, value: Any):
        """Define valor de configuração."""
        parts = key.split(".")
        obj = self.config
        
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return
        
        if hasattr(obj, parts[-1]):
            setattr(obj, parts[-1], value)
    
    def print_config(self):
        """Imprime configurações atuais."""
        print("\n" + "="*50)
        print("⚙️ CONFIGURAÇÕES ATUAIS")
        print("="*50)
        print(f"📹 Vídeo: {self.config.video.width}x{self.config.video.height} @ {self.config.video.fps}fps")
        print(f"🔊 TTS: {self.config.tts.default_voice} ({self.config.tts.rate})")
        print(f"📋 Nicho: {self.config.content.nicho}")
        print(f"🎬 Vídeos/sessão: {self.config.content.num_videos}")
        print(f"🔍 Usar trends: {'Sim' if self.config.content.use_trends else 'Não'}")
        print(f"⏰ Scheduler: {self.config.scheduler.generation_time}")
        print(f"🐛 Debug: {'Sim' if self.config.debug else 'Não'}")
        print("="*50 + "\n")


# Instância global
config_manager = ConfigManager()


def get_config() -> Config:
    """Retorna configurações globais."""
    return config_manager.config


# Teste
if __name__ == "__main__":
    print("⚙️ Testando config_manager.py...")
    
    config_manager.print_config()
    
    # Testar get/set
    print(f"video.width = {config_manager.get('video.width')}")
    config_manager.set("content.num_videos", 10)
    print(f"content.num_videos = {config_manager.get('content.num_videos')}")
