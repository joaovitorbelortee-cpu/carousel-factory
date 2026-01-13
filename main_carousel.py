"""
👑 CAROUSEL KING - Gerador Automático de Carrosséis
Integração: Gemini API (Cérebro) + Carousel Engine (Visual)
"""

import os
import json
import time
from dotenv import load_dotenv

# Importar módulos locais
from gemini_content import generate_carousel_script
from carousel_engine import generate_carousel_images

# Carregar variaveis de ambiente
load_dotenv()

def main():
    print("\n" + "👑"*20)
    print("     CAROUSEL KING v1.0")
    print("     Gemini + Visual Engine")
    print("👑"*20 + "\n")
    
    # 1. Verificar API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or "Cole_Sua" in api_key:
        print("⚠️  ATENÇÃO: Você precisa configurar a GEMINI_API_KEY no arquivo .env!")
        print("    1. Crie um arquivo chamado '.env' na pasta viral-bot")
        print("    2. Adicione: GEMINI_API_KEY=sua_chave_do_google_aistudio")
        print("    (Você pode pegar uma chave grátis em: aistudio.google.com)\n")
        
        key_input = input("Ou cole sua API KEY agora (Enter para sair): ").strip()
        if not key_input:
            return
        os.environ["GEMINI_API_KEY"] = key_input

    # 2. Loop Principal
    while True:
        print("\n" + "-"*40)
        topic = input("📝 Sobre o que é o carrossel? (ex: 'Dicas de Python', 'Marketing Digital'): ")
        
        if not topic:
            break
            
        print(f"\n🧠 [1/3] Gemini pensando sobre '{topic}'...")
        try:
            # Definir tema visual baseado no tópico (simples heurística)
            theme = "dark"
            if "dinheiro" in topic.lower() or "venda" in topic.lower(): theme = "money"
            if "ia" in topic.lower() or "tech" in topic.lower(): theme = "ai"
            
            # Gerar Roteiro
            script_data = generate_carousel_script(topic, niche_theme=theme)
            print("✅ Roteiro gerado com sucesso!")
            
            # Mostrar preview
            print(f"   Título: {script_data['slides'][0]['title']}")
            print(f"   Slides: {len(script_data['slides'])}")
            
            # Gerar Imagens
            print(f"\n🎨 [2/3] Renderizando imagens (Tema: {theme})...")
            folder_name = topic.lower().replace(" ", "_")[:20]
            output_path = os.path.join("output", "carousels", folder_name)
            
            images = generate_carousel_images(script_data, output_dir=output_path)
            
            print(f"\n✅ [3/3] SUCESSO! 5 Imagens geradas em:")
            print(f"   📂 {output_path}")
            
            # Opção de postar (placeholder)
            print("\n🚀 Próximo passo: Upload automático (Em breve)")
            
        except Exception as e:
            print(f"❌ Erro fatal: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
