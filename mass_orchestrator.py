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
    carousel_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(carousel_dir, exist_ok=True)
    
    total = len(slides_text)
    
    # 3. Gerar slides
    for i, content in enumerate(slides_text, 1):
        output_path = os.path.join(carousel_dir, f"{i:02d}_slide.png")
        # Imagem apenas no slide 1 (Capa)
        img_to_use = cover_image_path if i == 1 else None
        
        # Extrair texto do item (pode vir como dict ou str)
        slide_text = content.get("text", "") if isinstance(content, dict) else str(content)
        
        create_slide(
            slide_text, 
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
    from gemini_integration import TEMAS_POR_NICHO
    import time
    
    print("🚀 INICIANDO GERAÇÃO MASSIVA - MODO CAVERNA 🚀")
    print(f"📂 Diretório de Saída: {OUTPUT_DIR}")
    
    total_generated = 0
    errors = 0
    
    # Iterar por todos os nichos e temas
    for nicho, temas in TEMAS_POR_NICHO.items():
        print(f"\n📌 Processando Nicho: {nicho.upper()}")
        
        for tema in temas:
            # Sanitizar nome da pasta
            safe_name = f"{nicho}_{tema[:20]}".replace(" ", "_").replace(":", "").lower()
            
            # Verificar se já existe para não duplicar (opcional, pode querer forçar)
            final_dir = os.path.join(OUTPUT_DIR, safe_name)
            if os.path.exists(final_dir):
                print(f"  ⏭️  Pular {safe_name} (Já existe)")
                continue
            
            # Gerar
            success = generate_full_carousel(tema, safe_name)
            
            if success:
                total_generated += 1
                # Pequena pausa para evitar Rate Limit da API do Gemini se for muito rápido
                time.sleep(2)
            else:
                errors += 1
                
    print("\n" + "="*40)
    print(f"🏁 FIM DO PROCESSO")
    print(f"✅ Gerados: {total_generated}")
    print(f"❌ Erros: {errors}")
    print("="*40)
