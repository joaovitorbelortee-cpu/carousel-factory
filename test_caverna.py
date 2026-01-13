from carousel_generator import generate_carousel, create_slide
from gemini_integration import generate_carousel_content
import os

def run_test():
    topic = "Domínio Próprio"
    print(f"🚀 Inspirando-se no Modo Caverna para: {topic}")
    
    # Conteúdo HARDCODED no estilo @modocaverna para o teste visual
    slides_text = [
        "A FARSA DO AUTOCONTROLE",
        "O sistema quer que você seja escravo dos seus impulsos.",
        "Domínio próprio não é sobre força de vontade.\nÉ sobre hackear a simulação.",
        "Leia: Meditações de Marco Aurélio.\nO código para a liberdade mental.",
        "Comente CAVERNA e receba o link para o despertar."
    ]
    
    if not slides_text:
        print("❌ Falha ao obter conteúdo")
        return

    # 2. Caminho da imagem gerada anteriormente (capa)
    # Procurar a imagem na pasta do cérebro (Brain)
    image_path = "C:/Users/Pichau/.gemini/antigravity/brain/5d2fb517-a6b9-40b7-bca9-2c1e49e38d4e/capa_modo_caverna_teste_1768335722888.png"
    
    # 3. Gerar carrossel
    name = "teste_modo_caverna_v1"
    
    # Vamos rodar manualmente para passar a imagem no slide 1
    import os
    from carousel_generator import OUTPUT_DIR
    carousel_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(carousel_dir, exist_ok=True)
    
    generated = []
    total = len(slides_text)
    
    for i, content in enumerate(slides_text, 1):
        output_path = os.path.join(carousel_dir, f"{i:02d}_slide.png")
        # No slide 1, passamos a imagem de capa
        img_to_use = image_path if i == 1 else None
        create_slide(content, i, total, style="caverna", output_path=output_path, image_path=img_to_use)
        generated.append(output_path)
        print(f"✅ Slide {i}/{total} criado")
    
    print(f"\n🔥 Carrossel MODO CAVERNA pronto em: {carousel_dir}")

if __name__ == "__main__":
    run_test()
