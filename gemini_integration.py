"""
Gerador de Conteudo para Carrosseis - Integrado com Google Gemini 3 Flash + Nano Banana
Usa Gemini 3 Flash para raciocínio e Nano Banana para geração de imagens
"""

import os
import random
import base64
from typing import List, Dict
import requests

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("google-generativeai não instalado ou configurado. IA desativada.")

# Modelos do Gemini Ecosystem
GEMINI_MODELS = {
    "reasoning": "gemini-3.0-flash",  # Para raciocínio e geração de texto
    "image_generation": "nano-banana",  # Para geração de imagens (Gemini 2.5 Flash Image)
    "image_pro": "nano-banana-pro"  # Para imagens profissionais (Gemini 3 Pro Image Preview)
}

# Templates baseados no modelocarrosel.md (MANTIDO IGUAL)
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
        "descricao": "Lembrete agressivo que desafia a zona de conforto",
        "estrutura": "Afirmacao direta + verdade incomoda",
        "exemplos": [
            "LEMBRANDO: Ninguem precisa de voce. Voce nao e insubstituivel.",
            "LEMBRANDO: Seu primo ta ficando rico. E voce?",
            "LEMBRANDO: Voce nao ta cansado. So ta fraco."
        ]
    }
}

# Temas por nicho
TEMAS_POR_NICHO = {
    "Desenvolvimento Pessoal": [
        "Mentalidade de Vencedor",
        "Disciplina Inabalável",
        "Foco Extremo",
        "Produtividade Máxima",
        "Autoconhecimento Profundo"
    ],
    "Empreendedorismo": [
        "Mindset de Milionário",
        "Vendas de Alta Performance",
        "Liderança de Impacto",
        "Networking Estratégico",
        "Gestão Eficiente"
    ],
    "Finanças": [
        "Liberdade Financeira",
        "Investimentos Inteligentes",
        "Mentalidade de Abundância",
        "Renda Passiva",
        "Educação Financeira"
    ],
    "Relacionamentos": [
        "Comunicação Assertiva",
        "Inteligência Emocional",
        "Relacionamentos Saudáveis",
        "Limites Pessoais",
        "Autoestima e Valor"
    ],
    "Saúde e Fitness": [
        "Disciplina Física",
        "Mentalidade Fitness",
        "Hábitos de Campeão",
        "Saúde Mental",
        "Energia e Vitalidade"
    ]
}

def get_temas_para_nicho(nicho: str) -> List[str]:
    """Retorna lista de temas para o nicho selecionado"""
    return TEMAS_POR_NICHO.get(nicho, TEMAS_POR_NICHO["Desenvolvimento Pessoal"])


def gerar_copy_template(formato: str, tema: str, nicho: str = "Geral") -> List[Dict]:
    """Gera copy usando templates pré-definidos (fallback quando IA não disponível)"""
    template = FORMATOS_MESTRES.get(formato, FORMATOS_MESTRES["diagnostico"])
    
    slides = [
        {
            "slide_number": 1,
            "title": f"🔥 {tema.upper()}",
            "content": f"{template['descricao']}",
            "visual_suggestion": "Imagem poderosa com fundo escuro e texto dourado"
        },
        {
            "slide_number": 2,
            "title": "A VERDADE",
            "content": random.choice(template["exemplos"]),
            "visual_suggestion": "Contraste forte preto e dourado"
        },
        {
            "slide_number": 3,
            "title": "O PROBLEMA",
            "content": f"A maioria ignora {tema.lower()}. Por isso continua fracassando.",
            "visual_suggestion": "Imagem de fracasso vs sucesso"
        },
        {
            "slide_number": 4,
            "title": "A SOLUÇÃO",
            "content": f"Quem domina {tema.lower()} domina o jogo.",
            "visual_suggestion": "Imagem de vitória e conquista"
        },
        {
            "slide_number": 5,
            "title": "⚡ AÇÃO",
            "content": "Salve este post. Compartilhe. Execute AGORA.",
            "visual_suggestion": "Call to action com elementos vibrantes"
        }
    ]
    
    return slides


def generate_carousel_content(topic: str, nicho: str = "Geral", num_slides: int = 5, credentials=None) -> List[Dict]:
    """
    Gera conteudo usando Gemini 3 Flash com credenciais OAuth ou API Key
    """
    if not GENAI_AVAILABLE:
        print("genai não disponível, retornando template fallback.")
        return gerar_copy_template("diagnostico", topic, nicho)
    
    try:
        model = None
        # Configura Gemini com as credenciais passadas (OAuth)
        if credentials:
            # Configura usando as credenciais do usuario (Gemini Auth)
            genai.configure(credentials=credentials)
            model = genai.GenerativeModel(GEMINI_MODELS["reasoning"])
            
        # Fallback: Configura com API Key do ambiente
        elif os.getenv("GEMINI_API_KEY"):
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(GEMINI_MODELS["reasoning"])
            
        if not model:
            raise Exception("Sem credenciais disponíveis para o Gemini")

        # Prompt otimizado para Gemini 3 Flash
        prompt = f"""
        Você é um especialista em marketing viral para Instagram no nicho de {nicho}.
        
        MISSÃO: Criar um carrossel de {num_slides} slides sobre "{topic}" usando a voz do Modo Caverna - 
        autoritário, provocador, direto, sem desculpas.
        
        REGRAS:
        - Tom: Mentoria agressiva, verdades duras, sem mimimi
        - Linguagem: Direta, impactante, memorável
        - Estrutura: Hook poderoso → Problema → Solução → Ação
        
        FORMATO JSON (retorne APENAS o JSON, sem markdown):
        [
            {{
                "slide_number": 1,
                "title": "TÍTULO PODEROSO",
                "content": "Conteúdo provocador e direto",
                "visual_suggestion": "Sugestão visual para geração de imagem"
            }}
        ]
        """

        response = model.generate_content(prompt)
        
        # Parse do JSON
        import json
        try:
            # Limpa a resposta e faz parse
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            slides = json.loads(text.strip())
            return slides
        except json.JSONDecodeError:
            print("Erro no parse JSON, usando template")
            return gerar_copy_template("diagnostico", topic, nicho)
            
    except Exception as e:
        print(f"Erro ao gerar conteúdo com Gemini 3 Flash: {e}")
        return gerar_copy_template("diagnostico", topic, nicho)


def generate_image_with_nano_banana(prompt: str, style: str = "cinematic", api_key: str = None) -> bytes:
    """
    Gera imagem usando Nano Banana (Gemini 2.5 Flash Image)
    
    Args:
        prompt: Descrição da imagem a ser gerada
        style: Estilo da imagem (cinematic, minimalist, bold, etc)
        api_key: API key do Gemini (opcional, usa GEMINI_API_KEY se não fornecida)
    
    Returns:
        bytes: Imagem gerada em formato PNG
    """
    if not GENAI_AVAILABLE:
        raise Exception("google-generativeai não disponível")
    
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY não configurada")
    
    try:
        genai.configure(api_key=api_key)
        
        # Usa o modelo Nano Banana para geração de imagem
        # Nota: Requer acesso ao Gemini 2.5 Flash Image
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Prompt otimizado para carrosséis virais
        enhanced_prompt = f"""
        Crie uma imagem {style} para um carrossel viral do Instagram:
        
        {prompt}
        
        Estilo: 
        - Fundo preto ou escuro dramático
        - Elementos dourados/luxuosos
        - Alto contraste
        - Sem texto na imagem
        - Aspecto ratio: 1080x1350 (formato carrossel Instagram)
        - Qualidade profissional
        """
        
        response = model.generate_content(
            enhanced_prompt,
            generation_config={
                "response_modalities": ["image"]
            }
        )
        
        # Extrai a imagem da resposta
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    return base64.b64decode(part.inline_data.data)
        
        raise Exception("Nenhuma imagem gerada")
        
    except Exception as e:
        print(f"Erro ao gerar imagem com Nano Banana: {e}")
        raise


def generate_carousel_with_ai_images(topic: str, nicho: str = "Geral", num_slides: int = 5, 
                                      credentials=None, use_ai_images: bool = True) -> Dict:
    """
    Gera carrossel completo com texto (Gemini 3 Flash) e imagens (Nano Banana)
    
    Returns:
        Dict com slides e imagens geradas por IA
    """
    # Gera o conteúdo textual
    slides = generate_carousel_content(topic, nicho, num_slides, credentials)
    
    result = {
        "slides": slides,
        "images": [],
        "model_used": GEMINI_MODELS["reasoning"]
    }
    
    # Gera imagens com Nano Banana se habilitado
    if use_ai_images and GENAI_AVAILABLE:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            for slide in slides:
                try:
                    visual_prompt = slide.get("visual_suggestion", f"Imagem para slide sobre {topic}")
                    image_bytes = generate_image_with_nano_banana(visual_prompt, "cinematic", api_key)
                    result["images"].append({
                        "slide_number": slide["slide_number"],
                        "image_data": base64.b64encode(image_bytes).decode('utf-8')
                    })
                except Exception as e:
                    print(f"Erro ao gerar imagem para slide {slide['slide_number']}: {e}")
                    result["images"].append({
                        "slide_number": slide["slide_number"],
                        "image_data": None,
                        "error": str(e)
                    })
    
    return result


# Funções de compatibilidade (mantidas para não quebrar código existente)
def gerar_conteudo_carrossel(tema: str, nicho: str = "Desenvolvimento Pessoal", num_slides: int = 5) -> list:
    """Wrapper de compatibilidade"""
    return generate_carousel_content(tema, nicho, num_slides)
