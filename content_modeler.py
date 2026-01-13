"""
Content Modeler - Modela roteiros baseados em vídeos virais do TikTok
Analisa padrões de vídeos em alta e gera roteiros adaptados para o seu nicho
"""

import asyncio
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import config
from logger import get_logger

logger = get_logger()

# Importar scraper
try:
    from tiktok_scraper import TikTokScraper, TikTokVideo, search_trending
except ImportError:
    TikTokVideo = None


@dataclass
class VideoScript:
    """Roteiro completo para um vídeo"""
    id: int
    title: str
    hook: str
    format_type: str  # listicle, pov, before_after, secret, challenge
    sections: List[Dict]  # Lista de seções do vídeo
    cta: str
    hashtags: List[str]
    estimated_duration: int  # segundos
    based_on: Optional[str] = None  # URL do vídeo que inspirou


class ContentModeler:
    """
    Modela conteúdo baseado em vídeos virais.
    Analisa padrões e gera roteiros adaptados para seu nicho.
    """
    
    # Formatos que mais viralizam no TikTok
    VIRAL_FORMATS = {
        "listicle": {
            "name": "Lista de X coisas",
            "hook_templates": [
                "Para de usar só {tool_conhecida} e olha essas {num} {tipo}!",
                "{num} {tipo} que parecem ilegais de tão boas",
                "Essas {num} {tipo} vão mudar sua vida",
                "{tipo} que você PRECISA conhecer hoje",
            ],
            "structure": ["hook", "item1", "item2", "item3", "item4", "item5", "cta"],
            "cta_templates": [
                "Salva esse vídeo e segue pra mais!",
                "Comenta EU QUERO que mando o pack!",
                "Qual foi a sua favorita? Comenta aí!",
            ]
        },
        "pov": {
            "name": "POV Storytelling",
            "hook_templates": [
                "POV: você descobriu {algo_incrivel}",
                "POV: sua vida depois de usar {ferramenta}",
                "POV: você finalmente encontrou {solucao}",
            ],
            "structure": ["hook", "before", "discovery", "after", "cta"],
            "cta_templates": [
                "Segue pra transformar sua vida também!",
                "Comenta QUERO que te ensino!",
            ]
        },
        "before_after": {
            "name": "Antes vs Depois",
            "hook_templates": [
                "Antes eu fazia isso em {tempo_antes}, agora faço em {tempo_depois}",
                "Como era trabalhar ANTES dessas IAs vs DEPOIS",
                "A diferença de quem usa {ferramenta} vs quem não usa",
            ],
            "structure": ["before", "transition", "after", "cta"],
            "cta_templates": [
                "Quer aprender? Link na bio!",
                "Segue pra mais dicas!",
            ]
        },
        "secret": {
            "name": "Segredo/Hack",
            "hook_templates": [
                "O {tipo} que ninguém te conta...",
                "Isso é tipo código de trapaça na vida real",
                "Vou te contar um segredo que vai mudar tudo",
            ],
            "structure": ["hook", "buildup", "reveal", "demo", "cta"],
            "cta_templates": [
                "Segue pra mais segredos!",
                "Salva antes que eu apague!",
            ]
        },
        "challenge": {
            "name": "Teste/Quiz",
            "hook_templates": [
                "Vou mostrar {num} {tipo}, me diz quantas você conhecia",
                "Teste: Você conhece essas {tipo}?",
                "Quantas dessas você já usou?",
            ],
            "structure": ["challenge", "items", "reveal", "cta"],
            "cta_templates": [
                "Comenta quantas você conhecia!",
                "Se acertou menos de 3, me segue agora!",
            ]
        }
    }
    
    # Ferramentas de IA para usar nos roteiros
    AI_TOOLS = {
        "texto": [
            {"name": "ChatGPT", "desc": "Escreve textos, códigos e ideias"},
            {"name": "Claude", "desc": "IA avançada da Anthropic"},
            {"name": "Gemini", "desc": "IA poderosa do Google"},
            {"name": "Perplexity", "desc": "Pesquisa com IA e fontes"},
            {"name": "Copy.ai", "desc": "Escreve copy que vende"},
        ],
        "imagem": [
            {"name": "Leonardo.ai", "desc": "Cria imagens profissionais grátis"},
            {"name": "Midjourney", "desc": "Arte profissional do zero"},
            {"name": "DALL-E 3", "desc": "Imagens realistas da OpenAI"},
            {"name": "Bing Create", "desc": "DALL-E 3 100% grátis"},
            {"name": "Ideogram", "desc": "Gera imagens com texto perfeito"},
            {"name": "Playground AI", "desc": "Imagens ilimitadas de graça"},
        ],
        "video": [
            {"name": "Pika Labs", "desc": "Transforma texto em vídeo"},
            {"name": "Runway ML", "desc": "Edita vídeos com IA"},
            {"name": "Luma Dream Machine", "desc": "Vídeos 3D realistas"},
            {"name": "HeyGen", "desc": "Clona você em vídeo"},
            {"name": "CapCut", "desc": "Edição com IA grátis"},
        ],
        "audio": [
            {"name": "Suno AI", "desc": "Cria músicas completas"},
            {"name": "ElevenLabs", "desc": "Clona qualquer voz"},
            {"name": "Murf.ai", "desc": "Vozes profissionais"},
        ],
        "produtividade": [
            {"name": "Notion AI", "desc": "Organiza tudo automaticamente"},
            {"name": "Gamma", "desc": "Apresentações em segundos"},
            {"name": "Tome", "desc": "Slides com uma frase"},
            {"name": "Remove.bg", "desc": "Remove fundo em 1 clique"},
        ]
    }
    
    def __init__(self, nicho: str = config.DEFAULT_TOPIC):
        self.nicho = nicho
        self.scraper = TikTokScraper() if TikTokVideo else None
    
    async def research_trends(self, hashtags: List[str] = None) -> List[TikTokVideo]:
        """Pesquisa vídeos em alta no TikTok"""
        if not self.scraper:
            logger.warning("⚠️ Scraper não disponível. Usando templates.")
            return []
        
        hashtags = hashtags or ["AITools", "TechTok", "ProductivityHacks"]
        all_videos = []
        
        for tag in hashtags:
            videos = await self.scraper.search_by_hashtag(tag, limit=5)
            all_videos.extend(videos)
        
        # Ordenar por engajamento
        all_videos.sort(key=lambda v: v.engagement_rate(), reverse=True)
        
        return all_videos[:10]  # Top 10
    
    def analyze_viral_patterns(self, videos: List[TikTokVideo]) -> Dict:
        """Analisa padrões dos vídeos virais"""
        patterns = {
            "formats": {},
            "hooks": [],
            "durations": [],
            "hashtags": {},
        }
        
        for video in videos:
            # Detectar formato pelo título/descrição
            desc = video.description.lower()
            
            if any(word in desc for word in ["5 ", "10 ", "lista", "top"]):
                fmt = "listicle"
            elif "pov" in desc:
                fmt = "pov"
            elif "antes" in desc or "depois" in desc or "before" in desc:
                fmt = "before_after"
            elif "segredo" in desc or "secret" in desc or "hack" in desc:
                fmt = "secret"
            elif "teste" in desc or "quiz" in desc or "quantas" in desc:
                fmt = "challenge"
            else:
                fmt = "listicle"  # Default mais viral
            
            patterns["formats"][fmt] = patterns["formats"].get(fmt, 0) + 1
            
            # Coletar hashtags
            for tag in video.hashtags:
                patterns["hashtags"][tag] = patterns["hashtags"].get(tag, 0) + 1
        
        return patterns
    
    def generate_scripts(self, num_videos: int = 5, based_on: List[TikTokVideo] = None) -> List[VideoScript]:
        """
        Gera roteiros modelados baseados nos vídeos virais.
        """
        scripts = []
        
        # Analisar padrões se tiver vídeos de referência
        if based_on:
            patterns = self.analyze_viral_patterns(based_on)
            # Usar formatos mais populares
            popular_formats = sorted(patterns["formats"].items(), key=lambda x: x[1], reverse=True)
            format_order = [f[0] for f in popular_formats]
        else:
            format_order = list(self.VIRAL_FORMATS.keys())
        
        # Gerar roteiros
        for i in range(num_videos):
            format_type = format_order[i % len(format_order)]
            script = self._create_script(i + 1, format_type)
            scripts.append(script)
        
        return scripts
    
    def _create_script(self, video_id: int, format_type: str) -> VideoScript:
        """Cria um roteiro específico baseado no formato"""
        fmt = self.VIRAL_FORMATS[format_type]
        
        # Selecionar ferramentas aleatórias
        all_tools = []
        for category in self.AI_TOOLS.values():
            all_tools.extend(category)
        
        selected_tools = random.sample(all_tools, min(5, len(all_tools)))
        
        # Gerar hook
        hook_template = random.choice(fmt["hook_templates"])
        hook = hook_template.format(
            tool_conhecida="os métodos tradicionais" if self.nicho != "ai_tools" else "o ChatGPT",
            num=str(random.choice([3, 5, 7, 10])),
            tipo=self.nicho,
            algo_incrivel=f"esse segredo sobre {self.nicho}",
            ferramenta=f"essas técnicas de {self.nicho}",
            solucao=f"essa solução para {self.nicho}",
            tempo_antes="5 horas",
            tempo_depois="5 minutos"
        )
        
        # Gerar título
        titles = [
            f"{self.nicho} que parecem ilegais de tão boas #{video_id}",
            f"POV: Você descobriu esse segredo sobre {self.nicho} #{video_id}",
            f"Antes vs Depois de aplicar {self.nicho} #{video_id}",
            f"O que ninguém te conta sobre {self.nicho} #{video_id}",
            f"Teste: Quanto você sabe sobre {self.nicho}? #{video_id}"
        ]
        title = titles[(video_id - 1) % len(titles)]
        
        # Criar seções
        sections = []
        for j, tool in enumerate(selected_tools):
            sections.append({
                "type": "tool",
                "number": j + 1,
                "name": tool["name"],
                "description": tool["desc"]
            })
        
        # CTA
        cta = random.choice(fmt["cta_templates"])
        
        # Hashtags
        hashtags = [
            "#FerramentasIA", "#InteligenciaArtificial", "#PackDeIA",
            "#DicasDeTech", "#IAGratis", "#TechTok", "#Produtividade"
        ]
        
        return VideoScript(
            id=video_id,
            title=title,
            hook=hook,
            format_type=format_type,
            sections=sections,
            cta=cta,
            hashtags=random.sample(hashtags, 5),
            estimated_duration=45
        )
    
    def script_to_narration(self, script: VideoScript) -> str:
        """Converte roteiro em texto de narração"""
        lines = [script.hook]
        
        for section in script.sections:
            if section["type"] == "tool":
                lines.append(
                    f"Número {section['number']}: {section['name']}. "
                    f"{section['description']}."
                )
        
        lines.append(script.cta)
        
        return " ".join(lines)
    
    def script_to_dict(self, script: VideoScript) -> Dict:
        """Converte roteiro para formato do content.py"""
        return {
            "id": script.id,
            "title": script.title,
            "hook": script.hook,
            "tools": [
                {"name": s["name"], "desc": s["description"]}
                for s in script.sections if s["type"] == "tool"
            ],
            "cta": script.cta,
            "hashtags": " ".join(script.hashtags)
        }


async def generate_modeled_content(num_videos: int = 5, niche: str = "ai_tools") -> List[Dict]:
    """
    Função principal: pesquisa trends e gera roteiros modelados.
    """
    logger.info(f"🔍 Pesquisando tendências para o nicho: {niche}...")
    
    modeler = ContentModeler(niche=niche)
    
    # Pesquisar trends
    trending_videos = await modeler.research_trends()
    
    if trending_videos:
        logger.info(f"✅ Encontrados {len(trending_videos)} vídeos em alta")
        logger.info("📊 Analisando padrões virais...")
    else:
        logger.info("📋 Usando templates de tendência dinâmica...")
    
    # Gerar roteiros modelados
    logger.info(f"✍️ Gerando {num_videos} roteiros para {niche}...")
    scripts = modeler.generate_scripts(num_videos, trending_videos)
    
    # Converter para formato utilizável
    videos = []
    for script in scripts:
        video_data = modeler.script_to_dict(script)
        videos.append(video_data)
        logger.info(f"   ✅ Roteiro {script.id}: {script.title}")
    
    return videos


# Teste
if __name__ == "__main__":
    async def test():
        videos = await generate_modeled_content(5)
        
        print("\n" + "="*60)
        print("📋 ROTEIROS GERADOS:")
        print("="*60)
        
        for video in videos:
            print(f"\n🎬 Vídeo {video['id']}: {video['title']}")
            print(f"   Hook: {video['hook']}")
            print(f"   Ferramentas: {', '.join([t['name'] for t in video['tools']])}")
            print(f"   CTA: {video['cta']}")
    
    asyncio.run(test())
