"""
Carousel Generator - Gerador de Carrosséis para TikTok/Instagram
Cria 3-5 imagens que formam um conteúdo coeso para postagem em carrossel

Formato: 1080x1350 (ideal para Instagram/TikTok)
"""

from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Dict, Optional
from datetime import datetime
from logger import get_logger

logger = get_logger()

# Configurações
CAROUSEL_SIZE = (1080, 1350)  # Instagram/TikTok optimal

# Detectar ambiente serverless (Vercel)
IS_SERVERLESS = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

if IS_SERVERLESS:
    OUTPUT_DIR = "/tmp/output/carousels"
else:
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output", "carousels")

# Templates de estilo
STYLES = {
    "dark_purple": {"bg": (25, 15, 45), "accent": (180, 100, 255), "text": (255, 255, 255)},
    "dark_blue": {"bg": (15, 25, 45), "accent": (0, 200, 255), "text": (255, 255, 255)},
    "dark_green": {"bg": (15, 35, 25), "accent": (100, 255, 180), "text": (255, 255, 255)},
    "dark_gold": {"bg": (35, 30, 15), "accent": (255, 215, 100), "text": (255, 255, 255)},
    "caverna": {"bg": (0, 0, 0), "accent": (255, 215, 0), "text": (255, 255, 255), "font_bold": True},
}

def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Carrega fonte com prioridade para assets locais, depois sistema."""
    
    # 1. Tentar fonte bundled (Ideal para Vercel)
    local_font = os.path.join(os.path.dirname(__file__), "assets", "fonts", "BebasNeue-Regular.ttf")
    if os.path.exists(local_font):
        try:
            return ImageFont.truetype(local_font, size)
        except Exception as e:
            logger.warning(f"Erro ao carregar fonte local: {e}")

    # 2. Fontes do Sistema (Fallback)
    font_paths = [
        # Windows
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        # Linux (Vercel/AWS)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    
    # 3. Fallback final
    return ImageFont.load_default()

def create_gradient_bg(size: tuple, color_start: tuple, color_end: tuple) -> Image.Image:
    """Cria background com gradiente vertical."""
    img = Image.new('RGB', size, color_start)
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
        for x in range(size[0]):
            img.putpixel((x, y), (r, g, b))
    return img

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> List[str]:
    """Quebra texto em linhas que cabem na largura máxima."""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] < max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    return lines

def create_slide(
    text: str,
    slide_number: int,
    total_slides: int,
    style: str = "dark_purple",
    output_path: str = None,
    image_path: str = None
) -> str:
    """Cria um slide individual do carrossel."""
    
    colors = STYLES.get(style, STYLES["dark_purple"])
    font_bold_needed = colors.get("font_bold", False)
    
    # Criar gradiente ou fundo sólido
    if style == "caverna":
        img = Image.new('RGB', CAROUSEL_SIZE, colors["bg"])
    else:
        bg_end = tuple(min(c + 20, 255) for c in colors["bg"])
        img = create_gradient_bg(CAROUSEL_SIZE, colors["bg"], bg_end)
        
    draw = ImageDraw.Draw(img)
    
    # Se for Modo Caverna, o layout é diferente
    if style == "caverna":
        # Área da imagem (topo - 60% da tela)
        img_height = int(CAROUSEL_SIZE[1] * 0.6)
        if image_path and os.path.exists(image_path):
            try:
                overlay_img = Image.open(image_path).convert("RGB")
                # Redimensionar preenchendo (crop center)
                img_ratio = CAROUSEL_SIZE[0] / img_height
                overlay_ratio = overlay_img.width / overlay_img.height
                
                if overlay_ratio > img_ratio: # Imagem mais larga
                    new_h = img_height
                    new_w = int(new_h * overlay_ratio)
                    overlay_img = overlay_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    left = (new_w - CAROUSEL_SIZE[0]) // 2
                    overlay_img = overlay_img.crop((left, 0, left + CAROUSEL_SIZE[0], img_height))
                else: # Imagem mais alta
                    new_w = CAROUSEL_SIZE[0]
                    new_h = int(new_w / overlay_ratio)
                    overlay_img = overlay_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    top = (new_h - img_height) // 2
                    overlay_img = overlay_img.crop((0, top, CAROUSEL_SIZE[0], top + img_height))
                
                img.paste(overlay_img, (0, 0))
            except Exception as e:
                logger.error(f"Erro ao carregar imagem {image_path}: {e}")
                draw.rectangle([0, 0, CAROUSEL_SIZE[0], img_height], fill=(20, 20, 20))
        else:
            # Fallback visual se não houver imagem: degradê sombrio
            for y in range(img_height):
                intensity = int(30 * (1 - y/img_height))
                draw.line([(0, y), (CAROUSEL_SIZE[0], y)], fill=(intensity, intensity, intensity))

        # Texto na parte de baixo (40% da tela)
        font_main = get_font(85 if slide_number == 1 else 65, bold=font_bold_needed)
        margin = 80
        max_width = CAROUSEL_SIZE[0] - (margin * 2)
        
        # Se for Slide 1, texto em CAIXA ALTA
        display_text = text.upper() if slide_number == 1 else text
        lines = wrap_text(display_text, font_main, max_width, draw)
        
        line_height = 100 if slide_number == 1 else 80
        total_text_height = len(lines) * line_height
        
        # Centralizar texto no espaço restante
        remaining_center_y = img_height + (CAROUSEL_SIZE[1] - img_height) // 2
        curr_y = remaining_center_y - total_text_height // 2
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_main)
            tw = bbox[2] - bbox[0]
            curr_x = (CAROUSEL_SIZE[0] - tw) // 2
            
            # Cor: Destaque no slide 1, branco nos outros
            fill_color = colors["accent"] if slide_number == 1 else colors["text"]
            draw.text((curr_x, curr_y), line, font=font_main, fill=fill_color)
            curr_y += line_height
            
    else:
        # Layout Clássico
        font_main = get_font(72, bold=font_bold_needed)
        margin = 100
        max_width = CAROUSEL_SIZE[0] - (margin * 2)
        lines = wrap_text(text.upper(), font_main, max_width, draw)
        
        line_height = 100
        total_height = len(lines) * line_height
        start_y = (CAROUSEL_SIZE[1] - total_height) // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font_main)
            tw = bbox[2] - bbox[0]
            x = (CAROUSEL_SIZE[0] - tw) // 2
            y = start_y + i * line_height
            draw.text((x, y), line, font=font_main, fill=colors["text"])

    # Elementos comuns (Indicador e Barra)
    font_small = get_font(30)
    indicator = f"{slide_number}/{total_slides}"
    draw.text((CAROUSEL_SIZE[0] - 120, 50), indicator, font=font_small, fill=(150, 150, 150))
    
    # Barra de progresso no fundo
    progress_w = int((slide_number / total_slides) * (CAROUSEL_SIZE[0] - 200))
    draw.line([(100, CAROUSEL_SIZE[1] - 80), (100 + progress_w, CAROUSEL_SIZE[1] - 80)], 
              fill=colors["accent"], width=8)

    # Salvar
    if output_path is None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"slide_{slide_number}.png")
    
    img.save(output_path, quality=95)
    return output_path

def generate_carousel(
    slides_data: List[Dict],
    theme: str = "caverna",
    name: str = None
) -> List[str]:
    """
    Gera um carrossel completo.
    slides_data: Lista de {"text": "...", "image_path": "..." (opcional)}
    """
    if name is None:
        name = datetime.now().strftime("carousel_%Y%m%d_%H%M%S")
    
    carousel_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(carousel_dir, exist_ok=True)
    
    total = len(slides_data)
    generated = []
    
    for i, slide in enumerate(slides_data, 1):
        output_path = os.path.join(carousel_dir, f"{i:02d}_slide.png")
        create_slide(
            text=slide["text"],
            slide_number=i,
            total_slides=total,
            style=theme,
            output_path=output_path,
            image_path=slide.get("image_path")
        )
        generated.append(output_path)
        logger.info(f"✅ Slide {i}/{total} criado: {output_path}")
    
    return generated

if __name__ == "__main__":
    test_data = [
        {"text": "A Matrix está te observando."},
        {"text": "Eles querem que você seja medíocre."},
        {"text": "Acorde hoje ou permaneça escravo."},
        {"text": "Comente 'FOGO' para o código."}
    ]
    generate_carousel(test_data, "caverna", "teste_final_v1")
