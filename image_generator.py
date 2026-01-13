"""
Gerador de Imagens/Placas de Texto para os Vídeos
Cria imagens estilo TikTok em 1920x1080 (landscape) com texto grande e cores vibrantes
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
from logger import get_logger

logger = get_logger()

# Configurações visuais
COLORS = {
    "background": (15, 15, 25),      # Preto azulado
    "accent": (138, 43, 226),         # Roxo vibrante
    "text_primary": (255, 255, 255),  # Branco
    "text_secondary": (180, 180, 200), # Cinza claro
    "highlight": (0, 255, 136),       # Verde neon
    "gradient_start": (30, 20, 60),   # Roxo escuro
    "gradient_end": (60, 30, 80),     # Roxo médio
}

# LANDSCAPE 1920x1080
VIDEO_SIZE = (1920, 1080)

# Contextos visuais para backgrounds
CONTEXT_COLORS = {
    "tech": {"bg": (20, 25, 40), "accent": (0, 200, 255)},
    "ai": {"bg": (30, 20, 50), "accent": (180, 100, 255)},
    "productivity": {"bg": (20, 40, 30), "accent": (100, 255, 150)},
    "money": {"bg": (40, 35, 15), "accent": (255, 215, 0)},
    "design": {"bg": (45, 25, 35), "accent": (255, 100, 150)},
}


def create_gradient_background(size: tuple, color_start: tuple, color_end: tuple) -> Image.Image:
    """
    Cria um gradiente vertical de cor_start para cor_end.
    """
    width, height = size
    img = Image.new('RGB', size, color_start)
    
    for y in range(height):
        # Calcular cor interpolada
        ratio = y / height
        r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
        
        # Desenhar linha horizontal
        for x in range(width):
            img.putpixel((x, y), (r, g, b))
    
    return img


def add_visual_elements(img: Image.Image, context: str = "tech") -> Image.Image:
    """
    Adiciona elementos visuais decorativos ao background (linhas, círculos, etc.)
    """
    draw = ImageDraw.Draw(img)
    colors = CONTEXT_COLORS.get(context, CONTEXT_COLORS["tech"])
    accent = colors["accent"]
    
    # Adicionar linhas diagonais sutis
    for i in range(0, img.width, 100):
        # Linhas semi-transparentes (simuladas com cor escura)
        line_color = (accent[0] // 8, accent[1] // 8, accent[2] // 8)
        draw.line([(i, 0), (i + 200, img.height)], fill=line_color, width=1)
    
    # Adicionar círculos decorativos nos cantos
    import random
    random.seed(42)  # Seed fixa para consistência
    for _ in range(5):
        x = random.randint(0, img.width)
        y = random.randint(0, img.height)
        radius = random.randint(50, 200)
        circle_color = (accent[0] // 10, accent[1] // 10, accent[2] // 10)
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=circle_color)
    
    return img


def get_font(size: int, bold: bool = False):
    """
    Tenta carregar uma fonte profissional do sistema.
    Prioriza Segoe UI (Windows) -> Roboto -> Arial.
    """
    # Caminhos comuns de fontes no Windows
    font_candidates = [
        "C:/Windows/Fonts/seguiemj.ttf", # Segoe UI Emoji (tem glifos normais tb)
        "C:/Windows/Fonts/segoeui.ttf",  # Segoe UI Standard
        "C:/Windows/Fonts/segoeuib.ttf", # Segoe UI Bold
        "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
        "C:/Windows/Fonts/arial.ttf",    # Arial
    ]
    
    # Tentar carregar do arquivo
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
                
    # Fallback para nomes (Linux/Mac)
    font_names = ["DejaVuSans-Bold", "LiberationSans-Bold", "Arial"]
    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, size)
        except:
            continue
            
    logger.warning("⚠️ Nenhuma fonte profissional encontrada. Usando padrão.")
    return ImageFont.load_default()


def draw_text_with_box(draw_obj, xy, text, font, text_color, box_color=(0, 0, 0, 100), padding=20):
    """
    Desenha texto com uma caixa de fundo semitransparente (estilo legenda).
    Requer que a imagem base seja RGBA ou que usemos uma camada separada, 
    mas aqui vamos simplificar desenhando o retângulo diretamente se o draw_obj suportar RGBA.
    """
    x, y = xy
    bbox = draw_obj.textbbox((x, y), text, font=font)
    
    # Expandir caixa
    box = (bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding)
    
    # Desenhar retangulo (precisa de overlay para transparência real)
    # Como draw_obj é geralmente de uma imagem RGB, não podemos desenhar alpha direto.
    # Vamos assumir que quem chama gerencia o overlay ou aceita cor sólida.
    # Mas para "Business Level", vamos fazer o overlay manualmente na função principal.
    # ENTÃO: Esta função apenas desenha o texto com sombra simples por enquanto.
    
    # Sombra
    draw_obj.text((x + 4, y + 4), text, font=font, fill=(0, 0, 0))
    # Texto
    draw_obj.text((x, y), text, font=font, fill=text_color)


def add_glassmorphism_box(base_img, rect_coords, color=(0, 0, 0, 100), radius=20):
    """
    Adiciona uma caixa com transparência (Glassmorphism).
    rect_coords: (x1, y1, x2, y2)
    """
    # Criar camada temporária para transparência
    overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Desenhar retângulo arredondado
    draw.rounded_rectangle(rect_coords, radius=radius, fill=color)
    
    # Compor
    base_img = base_img.convert('RGBA')
    out = Image.alpha_composite(base_img, overlay)
    return out.convert('RGB')


def create_title_card(title: str, output_path: str, context: str = "tech") -> str:
    """Cria uma imagem de título para o início do vídeo - LANDSCAPE 1920x1080."""
    colors = CONTEXT_COLORS.get(context, CONTEXT_COLORS["tech"])
    
    # Criar gradiente base
    img = create_gradient_background(VIDEO_SIZE, colors["bg"], 
                                     (colors["bg"][0]+20, colors["bg"][1]+10, colors["bg"][2]+30))
    
    # Adicionar elementos visuais
    img = add_visual_elements(img, context)
    
    draw = ImageDraw.Draw(img)
    font = get_font(90)
    
    # Quebrar texto
    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] < VIDEO_SIZE[0] - 300: # Margem maior
            current_line = test_line
        else:
            if current_line: lines.append(current_line)
            current_line = word
    if current_line: lines.append(current_line)
    
    # Calcular dimensões do bloco de texto
    line_height = 110
    total_height = len(lines) * line_height
    max_width = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        max_width = max(max_width, bbox[2] - bbox[0])
    
    start_y = (VIDEO_SIZE[1] - total_height) // 2
    
    # Adicionar Fundo "Glassmorphism" atrás do texto
    padding = 40
    box_coords = (
        (VIDEO_SIZE[0] - max_width) // 2 - padding,
        start_y - padding,
        (VIDEO_SIZE[0] + max_width) // 2 + padding,
        start_y + total_height + padding
    )
    img = add_glassmorphism_box(img, box_coords, color=(0, 0, 0, 160)) # Fundo escuro semi-transparente
    
    # Redesenhar Draw object na nova imagem
    draw = ImageDraw.Draw(img)
    
    # Desenhar texto
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (VIDEO_SIZE[0] - text_width) // 2
        y = start_y + i * line_height
        
        # Texto com cor de destaque ou branco
        draw.text((x, y), line, font=font, fill=COLORS["text_primary"])
    
    img.save(output_path, quality=95)
    logger.info(f"✅ Imagem título 1920x1080 criada: {output_path}")
    return output_path


def create_tool_card(tool_name: str, tool_desc: str, number: int, 
                     output_path: str, context: str = "tech") -> str:
    """Cria uma imagem para cada ferramenta - LANDSCAPE 1920x1080."""
    colors = CONTEXT_COLORS.get(context, CONTEXT_COLORS["tech"])
    
    img = create_gradient_background(VIDEO_SIZE, colors["bg"],
                                     (colors["bg"][0]+15, colors["bg"][1]+10, colors["bg"][2]+25))
    img = add_visual_elements(img, context)
    
    # Adicionar Box Glassmorphism para o conteúdo
    content_box = (100, 200, 1820, 880)
    img = add_glassmorphism_box(img, content_box, color=(0, 0, 0, 120))
    
    draw = ImageDraw.Draw(img)
    
    # Número grande à esquerda
    font_number = get_font(250)
    number_text = f"#{number}"
    draw.text((150, VIDEO_SIZE[1]//2 - 180), number_text, 
              font=font_number, fill=colors["accent"])
    
    # Nome da ferramenta
    font_name = get_font(110)
    draw.text((550, VIDEO_SIZE[1]//2 - 120), tool_name, 
              font=font_name, fill=COLORS["text_primary"])
    
    # Descrição (com quebra de linha se necessário)
    font_desc = get_font(60)
    
    # Quebrar descrição simples
    desc_words = tool_desc.split()
    desc_lines = []
    curr_d = ""
    for w in desc_words:
        test_d = curr_d + " " + w if curr_d else w
        if draw.textbbox((0,0), test_d, font=font_desc)[2] < 1200:
             curr_d = test_d
        else:
             desc_lines.append(curr_d)
             curr_d = w
    if curr_d: desc_lines.append(curr_d)
    
    desc_y = VIDEO_SIZE[1]//2 + 20
    for line in desc_lines:
        draw.text((550, desc_y), line, font=font_desc, fill=COLORS["text_secondary"])
        desc_y += 70
    
    img.save(output_path, quality=95)
    logger.info(f"✅ Imagem ferramenta 1920x1080 criada: {output_path}")
    return output_path


def create_cta_card(cta_text: str, output_path: str, context: str = "tech") -> str:
    """Cria uma imagem de CTA (Call to Action) para o final - LANDSCAPE 1920x1080."""
    colors = CONTEXT_COLORS.get(context, CONTEXT_COLORS["tech"])
    
    # Background com cor de destaque vibrante
    img = Image.new('RGB', VIDEO_SIZE, colors["accent"])
    
    # Elementos decorativos
    draw = ImageDraw.Draw(img)
    for i in range(0, VIDEO_SIZE[0], 50):
        alpha = 40
        draw.line([(i, 0), (i, VIDEO_SIZE[1])], 
                 fill=(255, 255, 255, alpha), width=1)
    
    # Box Glassmorphism Central
    box_coords = (400, 300, 1520, 780)
    img = add_glassmorphism_box(img, box_coords, color=(0, 0, 0, 180), radius=40)
    
    draw = ImageDraw.Draw(img)
    font = get_font(90)
    
    # Texto
    bbox = draw.textbbox((0,0), cta_text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    
    x = (VIDEO_SIZE[0] - w) // 2
    y = (VIDEO_SIZE[1] - h) // 2
    
    draw.text((x, y), cta_text, font=font, fill=(255, 255, 255))
    
    img.save(output_path, quality=95)
    logger.info(f"✅ Imagem CTA 1920x1080 criada: {output_path}")
    return output_path


def generate_all_images_for_video(video: dict, output_dir: str, context: str = "tech") -> list:
    """
    Gera todas as imagens necessárias para um vídeo em 1920x1080.
    
    Returns:
        Lista de caminhos das imagens na ordem correta.
    """
    video_id = video["id"]
    images = []
    
    # Pasta para este vídeo
    video_assets_dir = os.path.join(output_dir, f"video_{video_id}")
    os.makedirs(video_assets_dir, exist_ok=True)
    
    # Determinar contexto baseado no título
    title_lower = video.get("title", "").lower()
    if "ia" in title_lower or "ai" in title_lower:
        context = "ai"
    elif "produtiv" in title_lower:
        context = "productivity"
    elif "dinheiro" in title_lower or "renda" in title_lower:
        context = "money"
    elif "design" in title_lower:
        context = "design"
    else:
        context = "tech"
    
    # 1. Título/Hook
    title_path = os.path.join(video_assets_dir, "00_title.png")
    create_title_card(video["title"], title_path, context)
    images.append(title_path)
    
    # 2. Ferramentas
    for i, tool in enumerate(video["tools"], 1):
        tool_path = os.path.join(video_assets_dir, f"{i:02d}_tool_{tool['name'].lower().replace(' ', '_').replace('.', '_')}.png")
        create_tool_card(tool["name"], tool["desc"], i, tool_path, context)
        images.append(tool_path)
    
    # 3. CTA
    cta_path = os.path.join(video_assets_dir, "99_cta.png")
    create_cta_card(video["cta"], cta_path, context)
    images.append(cta_path)
    
    logger.info(f"📸 {len(images)} imagens 1920x1080 geradas para vídeo {video_id}")
    
    return images