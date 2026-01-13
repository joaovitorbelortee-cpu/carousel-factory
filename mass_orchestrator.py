import os
import json
from carousel_generator import create_slide, OUTPUT_DIR
from gemini_integration import generate_carousel_content

def generate_full_carousel(topic: str, name: str, cover_image_path: str = None):
    """
    Gera um carrossel completo (5 slides) a partir de um tema.
    """
    print(f"\n🎬 Iniciando carrossel: {topic}")
    
    # 1. Conteúdo via Gemini (Persona Caverna)
    slides_text = generate_carousel_content(topic, 5)
    
    if not slides_text:
        print(f"⚠️ Falha ao obter conteúdo para {topic}")
        return False
    
    # 2. Criar diretório
    carousel_dir = os.path.join(OUTPUT_DIR, "lote_elite", name)
    os.makedirs(carousel_dir, exist_ok=True)
    
    total = len(slides_text)
    
    # 3. Gerar slides
    for i, content in enumerate(slides_text, 1):
        output_path = os.path.join(carousel_dir, f"{i:02d}_slide.png")
        # Imagem apenas no slide 1 (Capa)
        img_to_use = cover_image_path if i == 1 else None
        
        create_slide(
            content, 
            i, 
            total, 
            style="caverna", 
            output_path=output_path, 
            image_path=img_to_use
        )
        print(f"  ✅ Slide {i}/{total} pronto")
        
    print(f"✨ Carrossel '{name}' finalizado com sucesso!")
    return True

if __name__ == "__main__":
    # Este arquivo será orquestrado pelo Antigravity (IA) 
    # fornecendo os caminhos das imagens geradas.
    pass
