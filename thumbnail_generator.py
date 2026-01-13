"""
Thumbnail Generator - Gerador de thumbnails para vídeos (BMad-CORE: Optimize)
Cria thumbnails atraentes para maximizar CTR
"""

import os
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


class ThumbnailGenerator:
    """
    Gerador de thumbnails otimizadas para TikTok/Instagram.
    Cria thumbnails com alto CTR (Click-Through Rate).
    """
    
    # Dimensões padrão
    SIZES = {
        "tiktok": (1080, 1920),
        "instagram_story": (1080, 1920),
        "instagram_feed": (1080, 1080),
        "youtube": (1280, 720),
    }
    
    # Cores vibrantes para thumbnails
    COLORS = {
        "primary": "#FF0050",     # Vermelho TikTok
        "secondary": "#00F2EA",   # Cyan TikTok
        "accent": "#FFE600",      # Amarelo
        "dark": "#121212",        # Fundo escuro
        "white": "#FFFFFF",
        "gradient_start": "#667EEA",
        "gradient_end": "#764BA2",
    }
    
    def __init__(self, output_dir: str = "output/thumbnails"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Obtém fonte para texto."""
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            try:
                return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", size)
            except:
                return ImageFont.load_default()
    
    def create_gradient_background(
        self,
        size: Tuple[int, int],
        color1: str = None,
        color2: str = None
    ) -> Image.Image:
        """Cria fundo com gradiente."""
        width, height = size
        color1 = color1 or self.COLORS["gradient_start"]
        color2 = color2 or self.COLORS["gradient_end"]
        
        # Converter cores hex para RGB
        r1, g1, b1 = tuple(int(color1.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        r2, g2, b2 = tuple(int(color2.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        img = Image.new('RGB', size)
        draw = ImageDraw.Draw(img)
        
        for y in range(height):
            ratio = y / height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return img
    
    def add_text_with_shadow(
        self,
        img: Image.Image,
        text: str,
        position: Tuple[int, int],
        font_size: int = 72,
        color: str = "#FFFFFF",
        shadow_color: str = "#000000",
        shadow_offset: Tuple[int, int] = (4, 4)
    ) -> Image.Image:
        """Adiciona texto com sombra."""
        draw = ImageDraw.Draw(img)
        font = self._get_font(font_size)
        
        # Sombra
        shadow_pos = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
        draw.text(shadow_pos, text, font=font, fill=shadow_color)
        
        # Texto principal
        draw.text(position, text, font=font, fill=color)
        
        return img
    
    def add_emoji_badge(
        self,
        img: Image.Image,
        emoji: str,
        position: Tuple[int, int],
        size: int = 100
    ) -> Image.Image:
        """Adiciona badge com emoji."""
        draw = ImageDraw.Draw(img)
        font = self._get_font(size)
        draw.text(position, emoji, font=font)
        return img
    
    def create_viral_thumbnail(
        self,
        title: str,
        subtitle: str = "",
        platform: str = "tiktok",
        style: str = "gradient",
        output_name: str = None
    ) -> str:
        """
        Cria thumbnail viral.
        
        Args:
            title: Texto principal
            subtitle: Texto secundário
            platform: Plataforma alvo
            style: Estilo visual
            output_name: Nome do arquivo
        
        Returns:
            Caminho da thumbnail
        """
        size = self.SIZES.get(platform, self.SIZES["tiktok"])
        
        # Criar background
        if style == "gradient":
            img = self.create_gradient_background(size)
        elif style == "dark":
            img = Image.new('RGB', size, self.COLORS["dark"])
        else:
            img = self.create_gradient_background(size)
        
        # Adicionar título
        title_y = size[1] // 3
        self.add_text_with_shadow(
            img,
            title.upper(),
            (50, title_y),
            font_size=90,
            color=self.COLORS["white"]
        )
        
        # Adicionar subtítulo
        if subtitle:
            self.add_text_with_shadow(
                img,
                subtitle,
                (50, title_y + 120),
                font_size=60,
                color=self.COLORS["secondary"]
            )
        
        # Adicionar emojis decorativos
        self.add_emoji_badge(img, "🔥", (size[0] - 150, 50), 100)
        self.add_emoji_badge(img, "⚡", (50, size[1] - 200), 80)
        
        # Salvar
        output_name = output_name or f"thumbnail_{platform}.png"
        output_path = os.path.join(self.output_dir, output_name)
        img.save(output_path, "PNG", quality=95)
        
        print(f"✅ Thumbnail criada: {output_path}")
        return output_path
    
    def create_from_video(
        self,
        video_path: str,
        timestamp: float = 2.0,
        output_name: str = None
    ) -> str:
        """
        Cria thumbnail a partir de frame do vídeo.
        
        Args:
            video_path: Caminho do vídeo
            timestamp: Segundo do vídeo para extrair
            output_name: Nome do arquivo
        
        Returns:
            Caminho da thumbnail
        """
        try:
            from moviepy.editor import VideoFileClip
        except ImportError:
            print("❌ MoviePy não instalado")
            return ""
        
        if not os.path.exists(video_path):
            print(f"❌ Vídeo não encontrado: {video_path}")
            return ""
        
        # Extrair frame
        clip = VideoFileClip(video_path)
        frame = clip.get_frame(min(timestamp, clip.duration - 0.1))
        clip.close()
        
        # Converter para PIL
        img = Image.fromarray(frame)
        
        # Aumentar saturação
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.3)
        
        # Aumentar contraste
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # Salvar
        output_name = output_name or f"thumb_{os.path.basename(video_path).replace('.mp4', '.png')}"
        output_path = os.path.join(self.output_dir, output_name)
        img.save(output_path, "PNG", quality=95)
        
        print(f"✅ Thumbnail extraída: {output_path}")
        return output_path
    
    def batch_create(self, videos: list) -> list:
        """Cria thumbnails para todos os vídeos."""
        thumbnails = []
        
        for i, video in enumerate(videos, 1):
            if isinstance(video, dict):
                title = video.get("title", f"Video {i}")
                thumb = self.create_viral_thumbnail(
                    title=title[:30],
                    subtitle=f"Vídeo {i}",
                    output_name=f"thumb_video_{i}.png"
                )
            else:
                thumb = self.create_from_video(
                    video,
                    output_name=f"thumb_{i}.png"
                )
            
            if thumb:
                thumbnails.append(thumb)
        
        return thumbnails


# Instância global
thumbnail_gen = ThumbnailGenerator()


# Teste
if __name__ == "__main__":
    print("🖼️ Testando thumbnail_generator.py...")
    
    # Criar thumbnail de teste
    thumb = thumbnail_gen.create_viral_thumbnail(
        title="5 IAs GRÁTIS",
        subtitle="Que parecem ilegais",
        platform="tiktok",
        output_name="test_thumb.png"
    )
    
    print(f"\n📁 Thumbnail criada: {thumb}")
