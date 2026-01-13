"""
Viral Hooks - Hooks que viralizam no TikTok/Instagram
Baseado em análise de vídeos com milhões de views
"""

# Hooks com alta conversão (testados em vídeos virais)
VIRAL_HOOKS = {
    "curiosidade": [
        "Você não vai acreditar no que essa IA faz...",
        "Isso vai mudar sua vida em 30 segundos",
        "Eu descobri algo que ninguém está falando",
        "Para tudo e presta atenção nisso",
        "Se você não conhece isso, está perdendo tempo",
    ],
    "urgencia": [
        "URGENTE: Essas IAs vão ser pagas em breve",
        "Salva esse vídeo antes que eu apague",
        "Você tem que ver isso AGORA",
        "Última chance de usar de graça",
        "Poucos sabem disso, aproveita enquanto dá",
    ],
    "choque": [
        "Isso deveria ser proibido de tão bom",
        "Essas IAs parecem ilegais de tão boas",
        "Como isso é grátis?! Não faz sentido",
        "Eu fiquei em choque quando descobri isso",
        "Isso vai substituir 90% dos trabalhos",
    ],
    "prova_social": [
        "Todo mundo tá usando menos você",
        "Mais de 1 milhão de pessoas já usam isso",
        "Os maiores criadores usam essas ferramentas",
        "Bilionários usam isso todo dia",
        "A elite da tecnologia não quer que você saiba",
    ],
    "transformacao": [
        "Antes eu era igual você, até descobrir isso",
        "De 0 a 10k em 30 dias com essa IA",
        "Isso transformou minha forma de trabalhar",
        "POV: sua vida depois de conhecer essas IAs",
        "Antes vs Depois de usar essas ferramentas",
    ],
}

# CTAs que geram engajamento
VIRAL_CTAS = [
    "Salva esse vídeo e segue pra mais!",
    "Comenta EU QUERO que mando o pack completo!",
    "Segue agora ou você vai esquecer!",
    "Ativa o sininho pra não perder nenhuma dica!",
    "Manda pra alguém que precisa ver isso!",
    "Comenta qual foi a sua favorita!",
    "Se chegou até aqui, comenta 🔥",
    "Qual você vai testar primeiro? Comenta aí!",
]

# Hashtags otimizadas para alcance
HASHTAGS_TIKTOK = [
    "#FerramentasIA",
    "#InteligenciaArtificial", 
    "#ChatGPT",
    "#IAGratis",
    "#TechTok",
    "#DicasDeTech",
    "#Produtividade",
    "#ferramentasgratis",
    "#ai",
    "#artificialintelligence",
    "#aitools",
    "#techtips",
    "#viral",
    "#fyp",
    "#foryou",
]

HASHTAGS_INSTAGRAM = [
    "#inteligenciaartificial",
    "#tecnologia",
    "#inovacao",
    "#ferramentasdigitais",
    "#produtividade",
    "#marketingdigital",
    "#empreendedorismo",
    "#dicasdetech",
    "#iaparacriadores",
    "#automatizacao",
]

# Estruturas de vídeo que mais viralizam
VIRAL_STRUCTURES = {
    "listicle_5": {
        "name": "Lista de 5 coisas",
        "duration": "45-60s",
        "structure": [
            {"type": "hook", "duration": 3},
            {"type": "item1", "duration": 8},
            {"type": "item2", "duration": 8},
            {"type": "item3", "duration": 8},
            {"type": "item4", "duration": 8},
            {"type": "item5", "duration": 8},
            {"type": "cta", "duration": 5},
        ],
        "engagement": "alto"
    },
    "pov": {
        "name": "POV Narrativo",
        "duration": "30-45s",
        "structure": [
            {"type": "hook_pov", "duration": 5},
            {"type": "before", "duration": 10},
            {"type": "transformation", "duration": 15},
            {"type": "after", "duration": 10},
            {"type": "cta", "duration": 5},
        ],
        "engagement": "muito_alto"
    },
    "secret_reveal": {
        "name": "Revelação de Segredo",
        "duration": "40-50s",
        "structure": [
            {"type": "hook_secret", "duration": 5},
            {"type": "buildup", "duration": 10},
            {"type": "reveal", "duration": 20},
            {"type": "demo", "duration": 10},
            {"type": "cta", "duration": 5},
        ],
        "engagement": "alto"
    },
}

# Horários de pico por plataforma (Brasil)
BEST_POST_TIMES = {
    "tiktok": {
        "weekday": ["12:00", "18:00", "21:00"],
        "weekend": ["10:00", "14:00", "20:00"],
    },
    "instagram": {
        "weekday": ["11:00", "13:00", "19:00", "21:00"],
        "weekend": ["11:00", "17:00", "20:00"],
    },
}


def get_random_hook(category: str = None) -> str:
    """Retorna um hook viral aleatório."""
    import random
    
    if category and category in VIRAL_HOOKS:
        return random.choice(VIRAL_HOOKS[category])
    
    # Categoria aleatória
    all_hooks = []
    for hooks in VIRAL_HOOKS.values():
        all_hooks.extend(hooks)
    
    return random.choice(all_hooks)


def get_random_cta() -> str:
    """Retorna um CTA viral aleatório."""
    import random
    return random.choice(VIRAL_CTAS)


def get_hashtags(platform: str = "tiktok", limit: int = 10) -> list:
    """Retorna hashtags otimizadas para a plataforma."""
    import random
    
    if platform == "instagram":
        tags = HASHTAGS_INSTAGRAM.copy()
    else:
        tags = HASHTAGS_TIKTOK.copy()
    
    random.shuffle(tags)
    return tags[:limit]


def get_best_post_time(platform: str = "tiktok") -> str:
    """Retorna o próximo melhor horário para postar."""
    from datetime import datetime
    
    now = datetime.now()
    is_weekend = now.weekday() >= 5
    
    times = BEST_POST_TIMES[platform]["weekend" if is_weekend else "weekday"]
    
    # Encontrar próximo horário
    for time_str in times:
        hour, minute = map(int, time_str.split(":"))
        if now.hour < hour or (now.hour == hour and now.minute < minute):
            return time_str
    
    # Se passou todos os horários, retorna o primeiro de amanhã
    return times[0]


# Teste
if __name__ == "__main__":
    print("🔥 HOOKS VIRAIS:")
    for category in VIRAL_HOOKS:
        print(f"\n{category.upper()}:")
        for hook in VIRAL_HOOKS[category][:2]:
            print(f"  → {hook}")
    
    print("\n📣 CTAs:")
    for cta in VIRAL_CTAS[:3]:
        print(f"  → {cta}")
    
    print(f"\n⏰ Melhor horário TikTok: {get_best_post_time('tiktok')}")
    print(f"⏰ Melhor horário Instagram: {get_best_post_time('instagram')}")
