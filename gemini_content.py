"""
Gemini Content Engine - O Cérebro do Carousel King
Gera roteiros estruturados para carrosséis usando Google Gemini API.
"""

import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Tentar carregar do .env
load_dotenv()

# CONFIGURAÇÃO DA API KEY
# Se não estiver no .env, vai pedir input ou dar erro
API_KEY = os.getenv("GEMINI_API_KEY")

def configure_gemini(api_key):
    genai.configure(api_key=api_key)

def generate_carousel_script(topic, niche_theme="money"):
    """
    Gera um roteiro de carrossel JSON estruturado.
    """
    if not API_KEY:
        raise ValueError("❌ ERRO: GEMINI_API_KEY não encontrada! Configure no arquivo .env ou no painel.")

    configure_gemini(API_KEY)
    
    # Modelo rápido (Flash é mais rápido que Pro, se disponível, senão Pro)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    ATUE COMO: Um General Estoico Moderno. Frio, calculista e brutalmente honesto.
    MISSÃO: Escrever a copy (texto) para um carrossel de Instagram sobre: "{topic}".
    
    TÉCNICA DE REFRAÇÃO (REFRAMING) OBRIGATÓRIA:
    - Não dê dicas. REDEFINA A REALIDADE.
    - Ex: Em vez de "Como acordar cedo", diga "Dormir tarde é desrespeito aos seus ancestrais".
    
    ESCOLHA O FORMATO IDEAL (TEMPLATE):
    - "dictionary": Se o tema for definir um conceito (ex: "O que é Sucesso").
    - "checklist": Se for uma lista de sintomas ou sinais (ex: "5 Sinais de Fraqueza").
    - "versus": Se for uma comparação (ex: "Rico vs Pobre").
    - "steps": Se for um processo passo-a-passo (ex: "Fase 1, 2, 3").
    - "standard": Para outros casos.
    
    ESTRUTURA JSON (Retorne APENAS isso):
    {{
        "niche": "{niche_theme}",
        "template_type": "standard",  // Escolha entre: standard, dictionary, checklist, versus, steps
        "slides": [
            {{ 
                "type": "cover", 
                "title": "TÍTULO AGRESSIVO EM CAIXA ALTA (MÁX 6 PALAVRAS)", 
                "subtitle": "SUBTÍTULO CURTO (MÁX 5 PALAVRAS)" 
            }},
            {{ "type": "content", "title": "1. [A VERDADE]", "text": "Reenquadramento brutal da realidade (Max 20 palavras)." }},
            {{ "type": "content", "title": "2. [O INIMIGO]", "text": "Quem está lucrando com sua fraqueza? (Max 20 palavras)." }},
            {{ "type": "content", "title": "3. [A ORDEM]", "text": "O que fazer agora. Sem massagem." }},
            {{ 
                "type": "cta", 
                "text": "FRASE FINAL DE IMPACTO + ORDEM DE COMENTÁRIO." 
            }}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Limpar markdown se houver
        if text.startswith("```json"):
            text = text[7:-3]
        
        data = json.loads(text)
        return data
    except Exception as e:
        print(f"❌ Erro no Gemini: {e}")
        # Fallback de emergência para não travar
        return {
            "niche": niche_theme,
            "slides": [
                {"type": "cover", "title": f"Dicas sobre {topic}", "subtitle": "Confira agora"},
                {"type": "content", "title": "Erro na IA", "text": "Não conseguimos gerar o texto. Verifique sua API Key."},
                {"type": "cta", "text": "Tente novamente"}
            ]
        }

if __name__ == "__main__":
    # Teste (vai falhar se não tiver key)
    try:
        script = generate_carousel_script("Como ganhar dinheiro com IA")
        print(json.dumps(script, indent=2))
    except Exception as e:
        print(e)
