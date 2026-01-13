"""
Niches Database - Base de dados de nichos para diversificação (BMad-CORE: Evolve)
Permite rotação automática de nichos para maior alcance
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import random


@dataclass
class Niche:
    """Representa um nicho de conteúdo."""
    id: str
    name: str
    description: str
    hooks: List[str]
    tools: List[Dict[str, str]]
    hashtags: List[str]
    target_audience: str
    engagement_potential: str  # alta, média, baixa


# Base de dados de nichos
NICHES_DB: Dict[str, Niche] = {
    "ai_tools": Niche(
        id="ai_tools",
        name="Ferramentas de IA",
        description="Pack de ferramentas de Inteligência Artificial gratuitas",
        hooks=[
            "5 IAs que parecem ilegais de tão boas",
            "Essas IAs vão mudar sua vida",
            "Você não vai acreditar no que essa IA faz",
            "Para de usar só ChatGPT e olha essas!",
        ],
        tools=[
            {"name": "Leonardo.ai", "desc": "Cria imagens profissionais grátis"},
            {"name": "Suno AI", "desc": "Cria músicas completas do zero"},
            {"name": "ElevenLabs", "desc": "Clona qualquer voz com IA"},
            {"name": "Runway ML", "desc": "Edita vídeos com IA"},
            {"name": "Gamma", "desc": "Apresentações em segundos"},
            {"name": "Claude", "desc": "IA avançada da Anthropic"},
            {"name": "Perplexity", "desc": "Pesquisa com IA e fontes"},
            {"name": "Ideogram", "desc": "Gera imagens com texto perfeito"},
        ],
        hashtags=["#FerramentasIA", "#IAGratis", "#TechTok", "#Produtividade", "#ChatGPT"],
        target_audience="Profissionais, estudantes, criadores de conteúdo",
        engagement_potential="alta",
    ),
    
    "productivity": Niche(
        id="productivity",
        name="Produtividade",
        description="Hacks e ferramentas para aumentar produtividade",
        hooks=[
            "Essas 5 ferramentas mudaram minha rotina",
            "Como faço em 1 hora o que antes levava 1 dia",
            "Você está perdendo tempo se não usa isso",
            "Produtividade 10x com essas dicas",
        ],
        tools=[
            {"name": "Notion", "desc": "Organiza tudo em um lugar"},
            {"name": "Todoist", "desc": "Gerencia tarefas sem esforço"},
            {"name": "Calendly", "desc": "Agenda reuniões automaticamente"},
            {"name": "Loom", "desc": "Grava tela em segundos"},
            {"name": "Grammarly", "desc": "Corrige textos automaticamente"},
        ],
        hashtags=["#Produtividade", "#GestãoDoTempo", "#Organização", "#TrabalhoRemoto"],
        target_audience="Profissionais, empreendedores",
        engagement_potential="alta",
    ),
    
    "money_online": Niche(
        id="money_online",
        name="Renda Extra Online",
        description="Formas de ganhar dinheiro na internet",
        hooks=[
            "5 formas de ganhar dinheiro dormindo",
            "Como fiz R$5.000 em uma semana",
            "Renda extra que funciona de verdade",
            "Você pode fazer isso hoje mesmo",
        ],
        tools=[
            {"name": "Hotmart", "desc": "Venda produtos digitais"},
            {"name": "Fiverr", "desc": "Ofereça serviços freelancer"},
            {"name": "Canva", "desc": "Crie designs profissionais"},
            {"name": "ChatGPT", "desc": "Automatize trabalhos"},
            {"name": "Midjourney", "desc": "Crie arte para vender"},
        ],
        hashtags=["#RendaExtra", "#DinheiroOnline", "#Freelancer", "#Empreendedorismo"],
        target_audience="Pessoas buscando renda extra",
        engagement_potential="muito_alta",
    ),
    
    "design": Niche(
        id="design",
        name="Design sem ser Designer",
        description="Ferramentas para criar designs profissionais",
        hooks=[
            "Crie designs profissionais sem saber nada",
            "Essas ferramentas substituem o Photoshop",
            "Você não precisa de designer",
            "Design profissional em 5 minutos",
        ],
        tools=[
            {"name": "Canva", "desc": "Design fácil e profissional"},
            {"name": "Figma", "desc": "Colabore em designs"},
            {"name": "Remove.bg", "desc": "Remove fundo em 1 clique"},
            {"name": "Photopea", "desc": "Photoshop online grátis"},
            {"name": "Coolors", "desc": "Paletas de cores"},
        ],
        hashtags=["#Design", "#Canva", "#DesignGrafico", "#Criatividade"],
        target_audience="Criadores de conteúdo, empreendedores",
        engagement_potential="média",
    ),
    
    "video_editing": Niche(
        id="video_editing",
        name="Edição de Vídeo",
        description="Ferramentas para editar vídeos facilmente",
        hooks=[
            "Edite vídeos como profissional sem curso",
            "Essas ferramentas são melhor que Premiere",
            "Efeitos virais em 2 minutos",
            "Edição de vídeo gratuita e fácil",
        ],
        tools=[
            {"name": "CapCut", "desc": "Edição completa grátis"},
            {"name": "DaVinci Resolve", "desc": "Hollywood na sua casa"},
            {"name": "Runway", "desc": "Efeitos com IA"},
            {"name": "Canva Video", "desc": "Vídeos em minutos"},
            {"name": "KineMaster", "desc": "Edição no celular"},
        ],
        hashtags=["#EdicaoDeVideo", "#CapCut", "#VideoVirial", "#ContentCreator"],
        target_audience="Criadores de conteúdo, YouTubers",
        engagement_potential="alta",
    ),
}


class NicheManager:
    """Gerenciador de nichos para rotação de conteúdo."""
    
    def __init__(self):
        self.current_niche_id = "ai_tools"
        self.used_hooks = []
    
    def get_niche(self, niche_id: str = None) -> Niche:
        """Retorna um nicho específico ou o atual."""
        niche_id = niche_id or self.current_niche_id
        return NICHES_DB.get(niche_id, NICHES_DB["ai_tools"])
    
    def get_all_niches(self) -> List[Niche]:
        """Retorna todos os nichos."""
        return list(NICHES_DB.values())
    
    def set_niche(self, niche_id: str):
        """Define o nicho atual."""
        if niche_id in NICHES_DB:
            self.current_niche_id = niche_id
            self.used_hooks = []
    
    def get_random_hook(self) -> str:
        """Retorna um hook aleatório do nicho atual."""
        niche = self.get_niche()
        available = [h for h in niche.hooks if h not in self.used_hooks]
        
        if not available:
            self.used_hooks = []
            available = niche.hooks
        
        hook = random.choice(available)
        self.used_hooks.append(hook)
        return hook
    
    def get_random_tools(self, count: int = 5) -> List[Dict]:
        """Retorna ferramentas aleatórias do nicho atual."""
        niche = self.get_niche()
        return random.sample(niche.tools, min(count, len(niche.tools)))
    
    def rotate_niche(self):
        """Rotaciona para o próximo nicho."""
        niches = list(NICHES_DB.keys())
        current_idx = niches.index(self.current_niche_id)
        next_idx = (current_idx + 1) % len(niches)
        self.current_niche_id = niches[next_idx]
        self.used_hooks = []
        return self.get_niche()
    
    def get_random_niche(self) -> Niche:
        """Retorna um nicho aleatório."""
        niche_id = random.choice(list(NICHES_DB.keys()))
        self.current_niche_id = niche_id
        return self.get_niche()
    
    def print_niches(self):
        """Imprime todos os nichos disponíveis."""
        print("\n📋 NICHOS DISPONÍVEIS:")
        print("-"*50)
        for niche in self.get_all_niches():
            current = " ← ATUAL" if niche.id == self.current_niche_id else ""
            print(f"  {niche.id}: {niche.name} ({niche.engagement_potential}){current}")


# Instância global
niche_manager = NicheManager()


# Teste
if __name__ == "__main__":
    print("📋 Testando niches_database.py...")
    
    niche_manager.print_niches()
    
    print(f"\n🎯 Nicho atual: {niche_manager.get_niche().name}")
    print(f"📣 Hook: {niche_manager.get_random_hook()}")
    print(f"🔧 Tools: {[t['name'] for t in niche_manager.get_random_tools(3)]}")
    
    print("\n🔄 Rotacionando nicho...")
    new_niche = niche_manager.rotate_niche()
    print(f"🎯 Novo nicho: {new_niche.name}")
