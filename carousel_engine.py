"""
Carousel Engine - LAYOUT REVOLUTION (v7.0)
Suporta Layouts Dinâmicos: Checklist (Diagnóstico) e Versus (Conflito).
"""

from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
import os
import random
import textwrap

# Configurações 4:5
IMG_WIDTH = 1080
IMG_HEIGHT = 1350
SIZE = (IMG_WIDTH, IMG_HEIGHT)

# Cores Caverna v4
THEMES = {
    "empire": {
        "bg_base": (12, 12, 14),
        "text": (240, 240, 240),
        "accent": (197, 160, 89), # Gold
        "geom_color": (25, 25, 30),
        "bar_bg": (40, 40, 40),
        "check_ok": (0, 180, 0),
        "check_no": (180, 0, 0)
    },
    "alert": {
        "bg_base": (8, 5, 5),
        "text": (255, 255, 255),
        "accent": (200, 30, 30), # Red
        "geom_color": (30, 10, 10),
        "bar_bg": (40, 10, 10),
        "check_ok": (200, 200, 200),
        "check_no": (255, 0, 0)
    }
}

def detect_theme(content_data):
    text_blob = str(content_data).lower()
    if any(x in text_blob for x in ["erro", "pare", "morte", "vício", "fraco", "perigo"]):
        return THEMES["alert"]
    return THEMES["empire"]

def get_font(size_key="medium", bold=False, condensada=False):
    sizes = {
        "title": 200, "subtitle": 50, "header": 110,
        "body": 60, "cta": 140, "big_num": 600, "footer": 28, "micro_hook": 35
    }
    size = sizes.get(size_key, 60)
    bebas_path = "assets/fonts/BebasNeue-Regular.ttf"
    if condensada and os.path.exists(bebas_path): return ImageFont.truetype(bebas_path, size)
    
    candidates = ["C:/Windows/Fonts/montserrat.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"]
    for path in candidates:
        if os.path.exists(path): return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def draw_icon(draw, icon_type, xy, size, color):
    """Desenha ícones vetoriais simples (Check ou X)."""
    x, y = xy
    draw.rectangle([x, y, x+size, y+size], outline=color, width=4) # Box
    
    pad = size // 4
    if icon_type == "check":
        # Desenha um V
        points = [(x+pad, y+size/2), (x+size/2, y+size-pad), (x+size-pad, y+pad)]
        draw.line(points, fill=color, width=6)
    elif icon_type == "cross":
        # Desenha um X
        draw.line([(x+pad, y+pad), (x+size-pad, y+size-pad)], fill=color, width=6)
        draw.line([(x+size-pad, y+pad), (x+pad, y+size-pad)], fill=color, width=6)

def draw_checklist_layout(draw, slide, theme):
    """Layout específico para listas de verificação."""
    # Título do Slide
    font_head = get_font("header", condensada=True)
    draw.text((80, 150), slide["title"].upper(), font=font_head, fill=theme["accent"])
    
    # Itens do Checklist (Parsing manual do texto)
    # Assume que o texto vem quebrado por quebras de linha ou pontos
    items = slide["text"].split('.')
    items = [i.strip() for i in items if len(i) > 3]
    
    y = 350
    font_body = get_font("body")
    
    for item in items[:4]: # Máximo 4 itens por slide para não poluir
        # Ícone (Check ou X dependendo do tema)
        icon = "cross" if theme == THEMES["alert"] else "check"
        icon_color = theme["check_no"] if theme == THEMES["alert"] else theme["check_ok"]
        
        draw_icon(draw, icon, (80, y), 50, icon_color)
        
        # Texto
        lines = textwrap.wrap(item, width=30)
        for line in lines:
            draw.text((150, y), line, font=font_body, fill=theme["text"])
            y += 70
        y += 40 # Espaço extra entre itens

def draw_versus_layout(draw, slide, theme):
    """Layout Tela Dividida (Esquerda vs Direita)."""
    # Linha Central
    mid = IMG_WIDTH // 2
    draw.line([(mid, 150), (mid, 1100)], fill=theme["text"], width=2)
    
    # Título (Centralizado no Topo)
    font_head = get_font("header", condensada=True)
    w = draw.textbbox((0,0), slide["title"], font=font_head)[2]
    draw.text(((IMG_WIDTH-w)//2, 80), slide["title"].upper(), font=font_head, fill=theme["accent"])
    
    # Parsing: Tenta separar por "vs" ou "|"
    parts = slide["text"].split("vs")
    if len(parts) < 2: parts = slide["text"].split("|")
    if len(parts) < 2: parts = [slide["text"], "???"]
    
    left_text = parts[0].strip()
    right_text = parts[1].strip()
    
    font_body = get_font("body", bold=True)
    
    # Lado Esquerdo (O Fraco/Erro)
    draw.text((mid - 300, 400), "ELES (FRACOS)", font=font_body, fill=(100,100,100))
    left_lines = textwrap.wrap(left_text, width=15)
    y = 500
    for line in left_lines:
        w = draw.textbbox((0,0), line, font=font_body)[2]
        draw.text((mid - w - 40, y), line, font=font_body, fill=(150,150,150)) # Texto apagado
        y += 70
        
    # Lado Direito (O Forte/Você)
    draw.text((mid + 40, 400), "VOCÊ (TOPO)", font=font_body, fill=theme["accent"])
    right_lines = textwrap.wrap(right_text, width=15)
    y = 500
    for line in right_lines:
        draw.text((mid + 40, y), line, font=font_body, fill=theme["text"]) # Texto brilhante
        y += 70

def apply_post_processing(img):
    """Textura + Vignette + Glitch"""
    # Noise
    noise = Image.new('L', SIZE)
    noise.putdata([random.randint(0, 15) for _ in range(IMG_WIDTH * IMG_HEIGHT)])
    base_pixels = img.load()
    noise_pixels = noise.load()
    for x in range(IMG_WIDTH):
        for y in range(IMG_HEIGHT):
            r, g, b = base_pixels[x,y]
            n = noise_pixels[x,y]
            base_pixels[x,y] = (min(255, r+n), min(255, g+n), min(255, b+n))
            
    # Vignette
    overlay = Image.new('RGBA', SIZE, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    for i in range(150):
        alpha = int(180 * (1 - (i/150)))
        draw.rectangle([i, i, IMG_WIDTH-i, IMG_HEIGHT-i], outline=(0,0,0,alpha))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # Glitch
    r, g, b = img.split()
    r = ImageChops.offset(r, -3, 0)
    b = ImageChops.offset(b, 3, 0)
    return Image.merge("RGB", (r, g, b)).crop((3, 0, IMG_WIDTH-3, IMG_HEIGHT)).resize(SIZE)

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    dummy = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    for word in words:
        current_line.append(word)
        line_str = ' '.join(current_line)
        bbox = dummy.textbbox((0, 0), line_str, font=font)
        if bbox[2] - bbox[0] > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line: lines.append(' '.join(current_line))
    return lines

def generate_carousel_images(content_data, output_dir="output/carousel"):
    os.makedirs(output_dir, exist_ok=True)
    images = []
    theme = detect_theme(content_data)
    template_type = content_data.get("template_type", "standard")
    total_slides = len(content_data["slides"])
    
    print(f"🎨 Renderizando com Layout: {template_type.upper()} | Tema: {'ALERTA' if theme==THEMES['alert'] else 'IMPÉRIO'}")
    
    for i, slide in enumerate(content_data["slides"], 1):
        img = Image.new('RGB', SIZE, theme["bg_base"])
        draw = ImageDraw.Draw(img)
        
        # SLIDE CAPA (Padrão para todos)
        if slide["type"] == "cover":
            font_title = get_font("title", condensada=True)
            lines = wrap_text(slide["title"].upper(), font_title, IMG_WIDTH - 60)
            total_h = len(lines) * 165
            start_y = (IMG_HEIGHT - total_h) // 2 - 100
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font_title)
                w = bbox[2] - bbox[0]
                x = (IMG_WIDTH - w) // 2
                draw.text((x+10, start_y+10), line, font=font_title, fill=(0,0,0))
                draw.text((x, start_y), line, font=font_title, fill=theme["text"])
                start_y += 165
            if "subtitle" in slide:
                font_sub = get_font("subtitle", bold=True)
                sub_lines = wrap_text(slide["subtitle"].upper(), font_sub, IMG_WIDTH - 200)
                start_y += 30
                for line in sub_lines:
                    bbox = draw.textbbox((0, 0), line, font=font_sub)
                    w = bbox[2] - bbox[0]
                    x = (IMG_WIDTH - w) // 2
                    # Box Highlight
                    pad=10
                    draw.rectangle([x-pad, start_y+5, x+w+pad, start_y+50+15], fill=theme["accent"])
                    draw.text((x, start_y), line, font=font_sub, fill=(0,0,0))
                    start_y += 70

        # SLIDE CONTEÚDO (LAYOUT DINÂMICO)
        elif slide["type"] == "content":
            # Escolhe o renderizador baseado no template
            if template_type == "checklist":
                draw_checklist_layout(draw, slide, theme)
            elif template_type == "versus":
                draw_versus_layout(draw, slide, theme)
            else:
                # Layout Standard (Padrão)
                font_big = get_font("big_num", condensada=True)
                draw.text((-50, -80), str(i-1), font=font_big, fill=theme["geom_color"])
                
                font_head = get_font("header", condensada=True)
                draw.text((80, 180), slide["title"].upper(), font=font_head, fill=theme["accent"])
                draw.rectangle([80, 290, 150, 310], fill=theme["text"])
                
                font_body = get_font("body")
                body_lines = wrap_text(slide["text"], font_body, IMG_WIDTH - 160)
                y = 380
                for line in body_lines:
                    draw.text((80, y), line, font=font_body, fill=theme["text"])
                    y += 80

        # SLIDE CTA
        elif slide["type"] == "cta":
            font_cta = get_font("cta", condensada=True)
            lines = wrap_text(slide["text"].upper(), font_cta, IMG_WIDTH - 100)
            start_y = (IMG_HEIGHT - (len(lines)*110)) // 2
            m = 60
            draw.rectangle([m, m, IMG_WIDTH-m, IMG_HEIGHT-m], outline=theme["accent"], width=8)
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font_cta)
                w = bbox[2] - bbox[0]
                x = (IMG_WIDTH - w) // 2
                draw.text((x+8, start_y+8), line, font=font_cta, fill=(0,0,0))
                draw.text((x, start_y), line, font=font_cta, fill=theme["text"])
                start_y += 110

        # Footer
        bar_y = IMG_HEIGHT - 25
        draw.rectangle([0, bar_y, IMG_WIDTH, IMG_HEIGHT], fill=theme["bar_bg"])
        progress_w = int((i / total_slides) * IMG_WIDTH)
        draw.rectangle([0, bar_y, progress_w, IMG_HEIGHT], fill=theme["accent"])
        font_f = get_font("footer")
        draw.text((50, IMG_HEIGHT - 65), "@MODOCAVERNA", font=font_f, fill=(100,100,100))
        
        img = apply_post_processing(img)
        filename = os.path.join(output_dir, f"slide_{i}.jpg")
        img.save(filename, quality=100, subsampling=0)
        images.append(filename)
        print(f"👁️ Slide {i} [{template_type.upper()}] gerado: {filename}")
        
    return images

if __name__ == "__main__":
    # Teste de Checklist
    test = {
        "niche": "alert",
        "template_type": "checklist",
        "slides": [
            {"type": "cover", "title": "DIAGNÓSTICO DE FRAQUEZA", "subtitle": "VOCÊ TEM ESSES SINTOMAS?"},
            {"type": "content", "title": "SINTOMAS DE NPC", "text": "Dorme depois das 23h. Viciado em Pornografia. Não treina pernas. Reclama do governo."},
            {"type": "cta", "text": "COMENTE 'CURA'"}
        ]
    }
    generate_carousel_images(test)
