"""
Roteiros dos 5 vídeos virais sobre Pack de Ferramentas de IA
Nicho: Pack de Ferramentas de IA para TikTok/Instagram
"""

VIDEOS = [
    {
        "id": 1,
        "title": "5 IAs que parecem ilegais de tão boas",
        "hook": "Para de usar só ChatGPT e olha essas IAs!",
        "tools": [
            {"name": "Leonardo.ai", "desc": "Cria imagens profissionais grátis"},
            {"name": "Gamma.app", "desc": "Faz apresentações em segundos"},
            {"name": "ElevenLabs", "desc": "Clona qualquer voz com IA"},
            {"name": "Runway ML", "desc": "Edita vídeos com inteligência artificial"},
            {"name": "Perplexity", "desc": "Pesquisa na internet com fontes reais"},
        ],
        "cta": "Salva esse vídeo e segue pra mais!",
        "hashtags": "#FerramentasIA #InteligenciaArtificial #PackDeIA #DicasDeTech #IAGratis"
    },
    {
        "id": 2,
        "title": "POV: Você descobriu esse pack de IAs",
        "hook": "POV: sua vida depois de descobrir essas ferramentas",
        "tools": [
            {"name": "ChatGPT", "desc": "Escreve textos, códigos e ideias"},
            {"name": "Midjourney", "desc": "Cria arte profissional do zero"},
            {"name": "CapCut", "desc": "Edita vídeos com IA de graça"},
            {"name": "Canva AI", "desc": "Design automático inteligente"},
            {"name": "Remove.bg", "desc": "Remove fundo de fotos em 1 clique"},
        ],
        "cta": "Comenta EU QUERO que mando o pack completo!",
        "hashtags": "#IA #Produtividade #TechTok #Automacao #FerramentasGratis"
    },
    {
        "id": 3,
        "title": "Antes vs Depois dessas IAs",
        "hook": "Antes eu fazia isso em 5 horas, agora faço em 5 minutos",
        "tools": [
            {"name": "Notion AI", "desc": "Organiza sua vida automaticamente"},
            {"name": "Tome", "desc": "Cria slides com uma frase"},
            {"name": "Descript", "desc": "Edita vídeo editando texto"},
            {"name": "Copy.ai", "desc": "Escreve copy que vende"},
            {"name": "Synthesia", "desc": "Cria vídeos com avatares de IA"},
        ],
        "cta": "Link do pack na bio!",
        "hashtags": "#AntesDepois #Produtividade #IA #Automacao #DicasDeIA"
    },
    {
        "id": 4,
        "title": "Teste: Quantas IAs você conhece?",
        "hook": "Vou mostrar 5 IAs, me diz quantas você conhecia",
        "tools": [
            {"name": "Claude", "desc": "Rival do ChatGPT da Anthropic"},
            {"name": "Gemini", "desc": "IA do Google super poderosa"},
            {"name": "Suno AI", "desc": "Cria músicas completas com IA"},
            {"name": "Pika Labs", "desc": "Transforma texto em vídeo"},
            {"name": "HeyGen", "desc": "Clona você em vídeo"},
        ],
        "cta": "Comenta quantas você conhecia!",
        "hashtags": "#Teste #IA #Quiz #TechTok #FerramentasIA"
    },
    {
        "id": 5,
        "title": "O pack de IAs que ninguém conta",
        "hook": "Essas IAs vão te fazer ganhar dinheiro dormindo",
        "tools": [
            {"name": "Luma Dream Machine", "desc": "Vídeos 3D realistas grátis"},
            {"name": "Ideogram", "desc": "Gera imagens com texto perfeito"},
            {"name": "Playground AI", "desc": "Imagens ilimitadas de graça"},
            {"name": "Murf.ai", "desc": "Vozes profissionais para vídeos"},
            {"name": "Bing Create", "desc": "DALL-E 3 100% grátis"},
        ],
        "cta": "Segue pra não perder o próximo!",
        "hashtags": "#Segredo #IA #GanharDinheiro #PackDeIA #DicasSecretas"
    }
]

def get_full_script(video: dict) -> str:
    """Gera o texto completo de narração para um vídeo."""
    lines = [video["hook"]]
    
    for i, tool in enumerate(video["tools"], 1):
        lines.append(f"Número {i}: {tool['name']}. {tool['desc']}.")
    
    lines.append(video["cta"])
    
    return " ".join(lines)

def get_video_by_id(video_id: int) -> dict:
    """Retorna um vídeo específico pelo ID."""
    for video in VIDEOS:
        if video["id"] == video_id:
            return video
    return None