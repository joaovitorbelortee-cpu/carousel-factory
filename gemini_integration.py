"""
Gerador de Conteudo para Carrosseis - Usando Templates do modelocarrosel.md
Integrado com Google Gemini API para geracao de copy virais
"""

import os
import random
from typing import List, Dict

# Templates baseados no modelocarrosel.md (THE DARK STOIC BIBLE v6.0)
FORMATOS_MESTRES = {
    "dicionario": {
        "nome": "O DICIONARIO",
        "descricao": "Pegar uma palavra e dar um significado estoico/agressivo",
        "estrutura": "PALAVRA: Nao e X. E Y que faz Z.",
        "exemplos": [
            "PACIENCIA: Nao e esperar. E manter a atitude enquanto espera.",
            "DISCIPLINA: Nao e castigo. E a ponte entre metas e conquistas.",
            "FOCO: Nao e ver uma coisa. E ignorar todas as outras."
        ]
    },
    "diagnostico": {
        "nome": "O DIAGNOSTICO",
        "descricao": "O usuario le para ver se ele tem o virus ou a cura",
        "estrutura": "Lista com sinais ou sintomas",
        "exemplos": [
            "5 SINAIS QUE SUA TESTOSTERONA ESTA BAIXA",
            "7 HABITOS QUE DESTROEM SEU FOCO SILENCIOSAMENTE",
            "3 COMPORTAMENTOS QUE TE MANTEM POBRE"
        ]
    },
    "conflito": {
        "nome": "O CONFLITO",
        "descricao": "Comparacao direta. Rico vs Pobre. Forte vs Fraco.",
        "estrutura": "X faz A. Y faz B.",
        "exemplos": [
            "HOMEM MENINO reclama. HOMEM ADULTO resolve.",
            "POBRE compra passivo. RICO compra ativo.",
            "FRACO espera motivacao. FORTE cria disciplina."
        ]
    },
    "lembrete": {
        "nome": "O LEMBRETE",
        "descricao": "Uma verdade curta para ler em 2 segundos",
        "estrutura": "Frase impactante curta",
        "exemplos": [
            "Pare de contar seus planos para quem nao tem sonhos.",
            "Sua disciplina e sua liberdade.",
            "A dor de hoje e a forca de amanha."
        ]
    },
    "algoritmo": {
        "nome": "O ALGORITMO",
        "descricao": "Processo logico de evolucao em fases",
        "estrutura": "FASE 1: X. FASE 2: Y. FASE 3: Z.",
        "exemplos": [
            "FASE 1: SUMA. FASE 2: FOQUE. FASE 3: VOLTE IRRECONHECIVEL.",
            "PASSO 1: ACEITE A DOR. PASSO 2: ABRACE O PROCESSO. PASSO 3: COLHA OS RESULTADOS."
        ]
    }
}

# Temas virais por nicho (para geracao automatica)
TEMAS_POR_NICHO = {
    "fitness": [
        "Os 5 Exercicios que Destroem Gordura",
        "Sinais que Voce Treina Errado",
        "Disciplina vs Motivacao na Academia",
        "A Mentira das Dietas Magicas",
        "Fraco vs Forte: Mentalidade Fitness"
    ],
    "produtividade": [
        "Os 5 Habitos Matinais das Pessoas de Sucesso",
        "Por Que Voce Procrastina",
        "Foco vs Distracoes: A Batalha Diaria",
        "A Farsa do Multitasking",
        "Algoritmo do Alto Desempenho"
    ],
    "financas": [
        "5 Sinais que Voce Vai Morrer Pobre",
        "Rico vs Pobre: Mentalidade de Dinheiro",
        "A Mentira do Salario Fixo",
        "Investir vs Gastar: O Codigo",
        "Os 4 Passos para Liberdade Financeira"
    ],
    "relacionamentos": [
        "5 Sinais de Homem de Valor",
        "Menino vs Homem: As Diferencas",
        "Por Que Ela Perdeu o Interesse",
        "O Paradoxo da Carencia",
        "Lembrete: Seu Valor Nao Depende de Ninguem"
    ],
    "empreendedorismo": [
        "5 Sinais que Voce Nasceu para Empreender",
        "Funcionario vs Empreendedor",
        "A Mentira do Plano Perfeito",
        "Algoritmo do Primeiro Milhao",
        "Lembrete: Sem Risco, Sem Riqueza"
    ],
    "mentalidade": [
        "5 Pensamentos que Te Mantem Mediocre",
        "Vitima vs Protagonista",
        "A Mentira do Talento Natural",
        "O Algoritmo da Mente Forte",
        "Disciplina: A Verdadeira Definicao"
    ]
}

def get_temas_para_nicho(nicho: str, quantidade: int = 5) -> List[str]:
    """Retorna temas virais para um nicho especifico"""
    nicho_lower = nicho.lower().strip()
    
    # Tenta encontrar o nicho exato
    for key in TEMAS_POR_NICHO:
        if key in nicho_lower or nicho_lower in key:
            return random.sample(TEMAS_POR_NICHO[key], min(quantidade, len(TEMAS_POR_NICHO[key])))
    
    # Se nao encontrar, usa mentalidade como default (mais generico)
    return random.sample(TEMAS_POR_NICHO["mentalidade"], min(quantidade, 5))

def gerar_copy_template(formato: str, tema: str, nicho: str) -> List[Dict]:
    """Gera copys usando os templates do modelocarrosel.md"""
    
    template = FORMATOS_MESTRES.get(formato, FORMATOS_MESTRES["lembrete"])
    
    # Gera slides baseado no formato
    slides = []
    
    if formato == "dicionario":
        # Slide 1: Palavra em destaque
        slides.append({
            "text": tema.upper().split()[0] if tema else "DISCIPLINA",
            "image_prompt": f"dark cinematic {nicho} concept, dramatic lighting, moody atmosphere"
        })
        # Slides 2-4: Definicoes
        definicoes = [
            f"Nao e o que voce pensa. E o que voce EXECUTA.",
            f"A maioria define errado. Poucos entendem o PODER.",
            f"Enquanto outros buscam conforto, voce busca CONQUISTA."
        ]
        for i, defi in enumerate(definicoes):
            slides.append({
                "text": defi,
                "image_prompt": f"stoic warrior statue, dark background, golden accents, philosophical"
            })
        # Slide final: Call to Action
        slides.append({
            "text": f"Siga para mais conteudo de {nicho.capitalize()}.",
            "image_prompt": f"minimalist dark poster, {nicho} theme, premium aesthetic"
        })
        
    elif formato == "diagnostico":
        # Slide 1: Titulo do diagnostico
        slides.append({
            "text": tema.upper(),
            "image_prompt": f"warning sign, red accents, dark background, dramatic"
        })
        # Slides 2-4: Sinais
        sinais = [
            "SINAL 1: Voce acorda sem energia.",
            "SINAL 2: Procrastina as tarefas importantes.",
            "SINAL 3: Evita desconforto a todo custo.",
            "SINAL 4: Compara sua vida com os outros."
        ]
        for sinal in sinais[:3]:
            slides.append({
                "text": sinal,
                "image_prompt": f"dark medical aesthetic, x-ray style, moody lighting"
            })
        slides.append({
            "text": "Se identificou? Comece a mudar HOJE.",
            "image_prompt": f"transformation concept, before after, powerful imagery"
        })
        
    elif formato == "conflito":
        # Slide 1: Titulo VS
        slides.append({
            "text": tema.upper(),
            "image_prompt": f"versus battle, dark arena, dramatic lighting, conflict"
        })
        # Slides 2-4: Comparacoes
        comparacoes = [
            ("O FRACO reclama.", "O FORTE resolve."),
            ("O FRACO espera.", "O FORTE age."),
            ("O FRACO desiste.", "O FORTE persiste.")
        ]
        for fraco, forte in comparacoes:
            slides.append({
                "text": f"{fraco} {forte}",
                "image_prompt": f"contrast concept, light vs dark, powerful imagery"
            })
        slides.append({
            "text": "De que lado voce esta?",
            "image_prompt": f"choice crossroads, dramatic lighting, philosophical"
        })
        
    elif formato == "algoritmo":
        # Slide 1: Titulo
        slides.append({
            "text": tema.upper(),
            "image_prompt": f"algorithm flowchart, futuristic, dark tech aesthetic"
        })
        # Slides 2-4: Fases
        fases = [
            "FASE 1: ACEITE ONDE VOCE ESTA.",
            "FASE 2: DEFINA ONDE QUER CHEGAR.",
            "FASE 3: EXECUTE SEM DESCULPAS.",
            "FASE 4: COLHA OS RESULTADOS."
        ]
        for fase in fases[:3]:
            slides.append({
                "text": fase,
                "image_prompt": f"step by step, progress bars, achievement, dark tech"
            })
        slides.append({
            "text": "Siga o processo. Confie no sistema.",
            "image_prompt": f"success achievement, summit, victory, dark aesthetic"
        })
        
    else:  # lembrete
        # Slides com frases de impacto
        lembretes = [
            tema.upper() if tema else "LEMBRETE DIARIO",
            "Sua disciplina e sua liberdade.",
            "A dor de hoje e a forca de amanha.",
            "Ninguem vem te salvar. Salve-se.",
            "Aja como se ninguem estivesse olhando."
        ]
        for i, lembrete in enumerate(lembretes[:5]):
            slides.append({
                "text": lembrete,
                "image_prompt": f"minimalist quote poster, dark background, golden text aesthetic"
            })
    
    return slides

def generate_carousel_content(topic: str, nicho: str = "Geral", num_slides: int = 5) -> List[Dict]:
    """
    Gera conteudo para carrossel usando templates do modelocarrosel.md
    Retorna lista de dicionarios com 'text' e 'image_prompt'
    """
    
    # Escolhe um formato aleatorio dos 5 mestres
    formatos = list(FORMATOS_MESTRES.keys())
    formato_escolhido = random.choice(formatos)
    
    print(f"[COPY] Formato: {FORMATOS_MESTRES[formato_escolhido]['nome']}")
    print(f"[COPY] Nicho: {nicho}, Tema: {topic}")
    
    # Gera as copys
    slides = gerar_copy_template(formato_escolhido, topic, nicho)
    
    # Ajusta quantidade de slides
    if len(slides) < num_slides:
        # Adiciona slides extras
        extras = [
            {"text": "COMPARTILHE COM QUEM PRECISA OUVIR ISSO.", "image_prompt": "share icon, dark social media aesthetic"},
            {"text": f"SIGA PARA MAIS {nicho.upper()}.", "image_prompt": f"follow button, {nicho} aesthetic, dark theme"}
        ]
        slides.extend(extras[:num_slides - len(slides)])
    elif len(slides) > num_slides:
        slides = slides[:num_slides]
    
    return slides

# Teste local
if __name__ == "__main__":
    slides = generate_carousel_content("Os 5 Habitos da Disciplina", "Produtividade", 5)
    for i, slide in enumerate(slides, 1):
        print(f"\n--- Slide {i} ---")
        print(f"Texto: {slide['text']}")
        print(f"Prompt: {slide['image_prompt']}")
