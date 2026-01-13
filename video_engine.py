"""
Video Engine v3.0 - DINÂMICO E VIRAL
Vídeos com transições rápidas, zoom Ken Burns, e música energética
Baseado nas tendências TikTok 2024
"""

import os
import random
from moviepy.editor import (
    ImageClip, AudioFileClip, VideoFileClip, concatenate_videoclips, 
    CompositeVideoClip, ColorClip, CompositeAudioClip, vfx
)
from moviepy.video.fx.all import resize, fadein, fadeout
import numpy as np
from logger import get_logger

logger = get_logger()

# Configurações - LANDSCAPE 1920x1080
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

# Diretórios
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")


def ensure_dirs():
    """Garante que diretórios existem."""
    os.makedirs(MUSIC_DIR, exist_ok=True)
    os.makedirs(BACKGROUNDS_DIR, exist_ok=True)


def get_background_music() -> str:
    """Obtém música de fundo."""
    ensure_dirs()
    
    if os.path.exists(MUSIC_DIR):
        local_music = [f for f in os.listdir(MUSIC_DIR) if f.endswith((".mp3", ".wav"))]
        if local_music:
            return os.path.join(MUSIC_DIR, random.choice(local_music))
    
    logger.info("ℹ️ Sem música de fundo. Adicione arquivos MP3 em assets/music/")
    return None


def apply_ken_burns(clip, duration, zoom_ratio=0.08):
    """
    Aplica efeito Ken Burns com zoom dinâmico.
    
    Args:
        clip: Clip de imagem
        duration: Duração do clip
        zoom_ratio: Quanto zoom aplicar (0.08 = 8%)
    """
    w, h = clip.size
    
    # Direção aleatória do zoom
    zoom_in = random.choice([True, False])
    
    def zoom_effect(get_frame, t):
        progress = t / duration
        
        if zoom_in:
            # Zoom in: começa normal, termina com zoom
            scale = 1 + (zoom_ratio * progress)
        else:
            # Zoom out: começa com zoom, termina normal
            scale = 1 + zoom_ratio - (zoom_ratio * progress)
        
        return get_frame(t)
    
    # Aplicar resize com zoom
    if zoom_in:
        return clip.resize(lambda t: 1 + (zoom_ratio * t / duration))
    else:
        return clip.resize(lambda t: 1 + zoom_ratio - (zoom_ratio * t / duration))


def create_gradient_image(width, height, start_color, end_color):
    """Gera uma imagem de gradiente vertical usando numpy."""
    # Criar array de gradiente vertical
    # start_color e end_color devem ser tuplas (R, G, B)
    r1, g1, b1 = start_color
    r2, g2, b2 = end_color
    
    # Criar gradiente linear
    # Linspace cria arrays de valores de r1 até r2 com tamanho 'height'
    # Depois repetimos isso 'width' vezes para preencher a largura
    # Shape final: (height, width, 3)
    
    base = np.linspace(0, 1, height)
    
    # Criar canais R, G, B interpolados
    r = np.linspace(r1, r2, height).reshape(height, 1)
    g = np.linspace(g1, g2, height).reshape(height, 1)
    b = np.linspace(b1, b2, height).reshape(height, 1)
    
    # Repetir para largura (broadcasting handles this if we setup correctly, but explicit repeat is safe)
    # Na verdade, broadcasting funciona se fizermos (height, 1) + (1, width) mas aqui queremos constante na largura
    r = np.repeat(r, width, axis=1)
    g = np.repeat(g, width, axis=1)
    b = np.repeat(b, width, axis=1)
    
    # Empilhar canais
    gradient = np.dstack((r, g, b)).astype(np.uint8)
    return gradient

def create_dynamic_background(width: int, height: int, duration: float, 
                              context: str = "tech") -> CompositeVideoClip:
    """
    Cria background com gradiente REAL.
    """
    # Cores mais vibrantes e dinâmicas
    context_colors = {
        "tech": [(20, 30, 80), (60, 20, 140)],      # Azul/roxo tech
        "ai": [(30, 10, 60), (20, 80, 160)],        # Roxo/azul AI
        "productivity": [(10, 40, 30), (40, 90, 80)], # Verde produtividade
        "money": [(40, 30, 10), (100, 90, 30)],      # Dourado
        "design": [(60, 20, 40), (120, 50, 90)],    # Rosa/magenta
        "default": [(20, 20, 40), (60, 40, 80)],    # Roxo escuro
    }
    
    colors = context_colors.get(context, context_colors["default"])
    
    # Gerar imagem de gradiente
    try:
        gradient_array = create_gradient_image(width, height, colors[0], colors[1])
        bg = ImageClip(gradient_array, duration=duration)
    except Exception as e:
        logger.warning(f"Erro ao criar gradiente: {e}. Usando cor sólida.")
        bg = ColorClip(size=(width, height), color=colors[0], duration=duration)
    
    return bg


def add_background_music(video_clip, music_path: str = None, volume: float = 0.18):
    """
    Adiciona música de fundo energética ao vídeo.
    Volume um pouco mais alto para dar mais energia (18%)
    """
    if not music_path or not os.path.exists(music_path):
        logger.info("ℹ️ Sem música de fundo")
        return video_clip
    
    try:
        music = AudioFileClip(music_path)
        
        video_duration = video_clip.duration
        if music.duration < video_duration:
            loops_needed = int(video_duration / music.duration) + 1
            from moviepy.editor import concatenate_audioclips
            music = concatenate_audioclips([music] * loops_needed)
        
        music = music.subclip(0, video_duration)
        music = music.volumex(volume)
        
        original_audio = video_clip.audio
        if original_audio:
            mixed_audio = CompositeAudioClip([original_audio, music])
            video_clip = video_clip.set_audio(mixed_audio)
        else:
            video_clip = video_clip.set_audio(music)
        
        logger.info(f"🎵 Música de fundo ENERGÉTICA adicionada (volume: {volume*100:.0f}%)")
        
    except Exception as e:
        logger.warning(f"Erro ao adicionar música: {e}")
    
    return video_clip


def create_video_from_images_and_audio(
    images: list, 
    audio_path: str, 
    output_path: str,
    transition_duration: float = 0.2,  # Transições mais rápidas
    context: str = "tech",
    add_music: bool = True
) -> str:
    """
    Cria um vídeo DINÂMICO com transições rápidas e zoom Ken Burns.
    
    NOVIDADES v3.0:
    - Zoom Ken Burns em cada imagem
    - Transições rápidas (0.2s)
    - Música mais alta (18%)
    - Efeitos de fade in/out
    """
    logger.info(f"🎬 Montando vídeo DINÂMICO 1920x1080 com {len(images)} imagens...")
    
    # Carregar áudio
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    num_images = len(images)
    duration_per_image = total_duration / num_images
    
    logger.info(f"⏱️ Duração total: {total_duration:.1f}s ({duration_per_image:.1f}s por imagem)")
    logger.info(f"🔄 Aplicando efeito Ken Burns + transições rápidas...")
    
    # Criar background
    background = create_dynamic_background(VIDEO_WIDTH, VIDEO_HEIGHT, total_duration, context)
    
    # Criar clips de imagem com efeitos dinâmicos
    clips = []
    current_time = 0
    
    for i, img_path in enumerate(images):
        if not os.path.exists(img_path):
            logger.warning(f"⚠️ Imagem não encontrada: {img_path}")
            continue
        
        # Criar clip da imagem
        clip = ImageClip(img_path, duration=duration_per_image)
        
        # Aplicar Ken Burns (zoom dinâmico)
        clip = apply_ken_burns(clip, duration_per_image, zoom_ratio=0.06)
        
        # Redimensionar mantendo proporção
        img_ratio = clip.w / clip.h if hasattr(clip, 'w') else 1920/1080
        target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT
        
        if img_ratio > target_ratio:
            new_width = VIDEO_WIDTH
            new_height = int(VIDEO_WIDTH / img_ratio)
        else:
            new_height = VIDEO_HEIGHT
            new_width = int(VIDEO_HEIGHT * img_ratio)
        
        clip = clip.resize((new_width, new_height))
        
        # Centralizar
        x_pos = (VIDEO_WIDTH - new_width) // 2
        y_pos = (VIDEO_HEIGHT - new_height) // 2
        clip = clip.set_position((x_pos, y_pos))
        
        # Adicionar transições rápidas
        if i > 0:  # Fade in (exceto primeiro)
            clip = fadein(clip, transition_duration)
        if i < num_images - 1:  # Fade out (exceto último)
            clip = fadeout(clip, transition_duration)
        
        # Definir tempo de início
        clip = clip.set_start(current_time)
        
        clips.append(clip)
        current_time += duration_per_image
    
    if not clips:
        raise ValueError("Nenhuma imagem válida encontrada!")
    
    # Compor vídeo final
    final_video = CompositeVideoClip([background] + clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
    
    # Adicionar áudio de narração
    final_video = final_video.set_audio(audio)
    
    # Adicionar música de fundo ENERGÉTICA (volume mais alto)
    if add_music:
        music_path = get_background_music()
        final_video = add_background_music(final_video, music_path, volume=0.18)
    
    # Renderizar com qualidade
    logger.info(f"💾 Renderizando vídeo DINÂMICO para: {output_path}")
    final_video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",  # MODO TURBO: Muito mais rápido
        threads=8,           # Usar mais threads
        logger=None
    )
    
    # Limpar
    final_video.close()
    audio.close()
    
    logger.info(f"✅ Vídeo DINÂMICO salvo: {output_path}")
    return output_path


def render_single_video(video_id: int, images: list, audio_path: str, output_dir: str) -> str:
    """Renderiza um único vídeo dinâmico."""
    output_path = os.path.join(output_dir, f"video_{video_id}_final.mp4")
    return create_video_from_images_and_audio(images, audio_path, output_path)
