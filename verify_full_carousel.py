import os
from carousel_generator import generate_carousel

# Paths das imagens geradas (caminhos absolutos do brain)
BRAIN_DIR = r"C:\Users\Pichau\.gemini\antigravity\brain\5d2fb517-a6b9-40b7-bca9-2c1e49e38d4e"

slides_data = [
    {
        "text": "A FARSA DO TALENTO",
        "image_path": os.path.join(BRAIN_DIR, "caverna_capa_disciplina_1768337808364.png")
    },
    {
        "text": "O sistema quer que você dependa da motivação. Ela é uma droga instável.",
        "image_path": os.path.join(BRAIN_DIR, "caverna_slide2_disciplina_1768337822748.png")
    },
    {
        "text": "Disciplina é o código que sobrepõe os seus impulsos. É a liberdade real.",
        "image_path": os.path.join(BRAIN_DIR, "caverna_slide3_disciplina_1768337838913.png")
    },
    {
        "text": "Leia: Meditações de Marco Aurélio. Domine sua mente e a Matrix cairá.",
        "image_path": os.path.join(BRAIN_DIR, "caverna_slide4_disciplina_1768337854339.png")
    },
    {
        "text": "Comente 'CAVERNA' para iniciar sua saída da simulação.",
        "image_path": os.path.join(BRAIN_DIR, "caverna_slide5_cta_1768337890526.png")
    }
]

# Gerar o carrossel
result_paths = generate_carousel(slides_data, theme="caverna", name="MODO_CAVERNA_DISCIPLINA_PRO")

print("\n🚀 Carrossel de Verificação Gerado!")
for p in result_paths:
    print(f"  - {p}")
