"""
Auto Poster - Posta vídeos automaticamente no TikTok e Instagram
Usa Playwright/Selenium para automação de browser

⚠️ AVISO: Use com moderação! Automação excessiva pode resultar em banimento.

Uso:
    python auto_poster.py post video.mp4          # Posta um vídeo
    python auto_poster.py queue                   # Posta fila de vídeos
    python auto_poster.py login tiktok            # Login no TikTok
    python auto_poster.py login instagram         # Login no Instagram
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass

# Tentar importar Playwright
try:
    from playwright.async_api import async_playwright, Browser, Page
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("⚠️ Playwright não instalado. Execute: pip install playwright && playwright install")

# Configurações
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
SESSIONS_DIR = os.path.join(PROJECT_DIR, "sessions")
QUEUE_FILE = os.path.join(OUTPUT_DIR, "post_queue.json")
POSTED_FILE = os.path.join(OUTPUT_DIR, "posted_videos.json")


@dataclass
class VideoPost:
    """Representa um vídeo para postar."""
    video_path: str
    caption: str
    hashtags: List[str]
    platform: str  # "tiktok" ou "instagram"
    scheduled_time: Optional[str] = None
    posted: bool = False
    posted_at: Optional[str] = None


class AutoPoster:
    """
    Automatiza postagem de vídeos no TikTok e Instagram.
    """
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.page = None
        
        # Criar diretórios
        os.makedirs(SESSIONS_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async def init_browser(self, platform: str):
        """Inicializa browser com sessão salva."""
        if not HAS_PLAYWRIGHT:
            raise Exception("Playwright não instalado!")
        
        session_path = os.path.join(SESSIONS_DIR, f"{platform}_session")
        
        playwright = await async_playwright().start()
        
        # Tentar usar sessão existente
        if os.path.exists(session_path):
            print(f"📂 Usando sessão salva de {platform}")
            self.browser = await playwright.chromium.launch_persistent_context(
                session_path,
                headless=self.headless,
                viewport={"width": 1280, "height": 720}
            )
        else:
            print(f"🆕 Criando nova sessão para {platform}")
            self.browser = await playwright.chromium.launch_persistent_context(
                session_path,
                headless=self.headless,
                viewport={"width": 1280, "height": 720}
            )
        
        self.page = await self.browser.new_page()
        return self.page
    
    async def close_browser(self):
        """Fecha o browser."""
        if self.browser:
            await self.browser.close()
    
    # ========== TIKTOK ==========
    
    async def login_tiktok(self):
        """Login manual no TikTok (usuário faz login, sessão é salva)."""
        print("\n🔐 LOGIN TIKTOK")
        print("-"*40)
        
        page = await self.init_browser("tiktok")
        
        await page.goto("https://www.tiktok.com/login")
        
        print("📱 Faça login manualmente no TikTok...")
        print("   (A sessão será salva automaticamente)")
        print("   Pressione ENTER quando terminar...")
        
        input()
        
        # Verificar se está logado
        await page.goto("https://www.tiktok.com/upload")
        await asyncio.sleep(2)
        
        if "upload" in page.url.lower():
            print("✅ Login no TikTok concluído e salvo!")
        else:
            print("⚠️ Verifique se o login foi feito corretamente")
        
        await self.close_browser()
    
    async def post_to_tiktok(self, video: VideoPost) -> bool:
        """
        Posta um vídeo no TikTok.
        
        Returns:
            True se postou com sucesso
        """
        print(f"\n📤 Postando no TikTok: {os.path.basename(video.video_path)}")
        
        try:
            page = await self.init_browser("tiktok")
            
            # Ir para página de upload
            await page.goto("https://www.tiktok.com/upload")
            await asyncio.sleep(3)
            
            # Verificar se está logado
            if "login" in page.url.lower():
                print("❌ Não está logado no TikTok!")
                print("   Execute: python auto_poster.py login tiktok")
                await self.close_browser()
                return False
            
            # Selecionar arquivo
            file_input = await page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files(video.video_path)
                print("   ✅ Vídeo carregado")
            else:
                print("   ❌ Não encontrou input de arquivo")
                await self.close_browser()
                return False
            
            # Aguardar upload
            await asyncio.sleep(10)
            
            # Adicionar caption
            caption_input = await page.query_selector('[data-e2e="caption-input"]')
            if caption_input:
                full_caption = f"{video.caption} {' '.join(video.hashtags)}"
                await caption_input.fill(full_caption)
                print("   ✅ Caption adicionada")
            
            # Clicar em Postar
            post_button = await page.query_selector('[data-e2e="post-button"]')
            if post_button:
                # await post_button.click()  # Descomentar para postar de verdade
                print("   ⚠️ Pronto para postar (descomente para postar)")
            
            await asyncio.sleep(5)
            await self.close_browser()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            await self.close_browser()
            return False
    
    # ========== INSTAGRAM ==========
    
    async def login_instagram(self):
        """Login manual no Instagram."""
        print("\n🔐 LOGIN INSTAGRAM")
        print("-"*40)
        
        page = await self.init_browser("instagram")
        
        await page.goto("https://www.instagram.com/")
        await asyncio.sleep(2)
        
        print("📱 Faça login manualmente no Instagram...")
        print("   (A sessão será salva automaticamente)")
        print("   Pressione ENTER quando terminar...")
        
        input()
        
        print("✅ Sessão do Instagram salva!")
        await self.close_browser()
    
    async def post_to_instagram(self, video: VideoPost) -> bool:
        """
        Posta um vídeo no Instagram (Reels).
        
        Nota: Instagram é mais difícil de automatizar.
        Recomendado usar a versão mobile ou ferramentas como Later.
        """
        print(f"\n📤 Postando no Instagram: {os.path.basename(video.video_path)}")
        print("   ⚠️ Instagram é difícil de automatizar via web")
        print("   💡 Recomendação: Use Later.com ou Buffer para agendar")
        
        return False


# ========== FILA DE POSTAGEM ==========

def load_queue() -> List[Dict]:
    """Carrega fila de postagem."""
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return []


def save_queue(queue: List[Dict]):
    """Salva fila de postagem."""
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)


def add_to_queue(video_path: str, caption: str, hashtags: List[str], platform: str):
    """Adiciona vídeo à fila de postagem."""
    queue = load_queue()
    
    queue.append({
        "video_path": video_path,
        "caption": caption,
        "hashtags": hashtags,
        "platform": platform,
        "added_at": datetime.now().isoformat(),
        "posted": False
    })
    
    save_queue(queue)
    print(f"✅ Adicionado à fila: {os.path.basename(video_path)}")


def auto_add_output_to_queue():
    """Adiciona automaticamente vídeos do output à fila."""
    videos = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".mp4")]
    queue = load_queue()
    queued_videos = [q["video_path"] for q in queue]
    
    count = 0
    for video in videos:
        video_path = os.path.join(OUTPUT_DIR, video)
        if video_path not in queued_videos:
            add_to_queue(
                video_path,
                "🔥 5 IAs que vão mudar sua vida! #IA #Tech",
                ["#FerramentasIA", "#TechTok", "#IAGratis"],
                "tiktok"
            )
            count += 1
    
    print(f"\n📋 {count} novos vídeos adicionados à fila")
    print(f"📊 Total na fila: {len(load_queue())} vídeos")


async def process_queue():
    """Processa fila de postagem."""
    queue = load_queue()
    pending = [q for q in queue if not q.get("posted", False)]
    
    if not pending:
        print("📭 Fila vazia!")
        return
    
    print(f"\n📋 {len(pending)} vídeos pendentes na fila")
    
    poster = AutoPoster(headless=False)
    
    for item in pending:
        video = VideoPost(
            video_path=item["video_path"],
            caption=item["caption"],
            hashtags=item["hashtags"],
            platform=item["platform"]
        )
        
        if item["platform"] == "tiktok":
            success = await poster.post_to_tiktok(video)
        else:
            success = await poster.post_to_instagram(video)
        
        if success:
            item["posted"] = True
            item["posted_at"] = datetime.now().isoformat()
    
    save_queue(queue)


# ========== CLI ==========

def main():
    """Função principal."""
    args = sys.argv[1:] if len(sys.argv) > 1 else ["help"]
    
    command = args[0].lower() if args else "help"
    
    poster = AutoPoster(headless=False)
    
    if command == "login":
        platform = args[1] if len(args) > 1 else "tiktok"
        if platform == "tiktok":
            asyncio.run(poster.login_tiktok())
        else:
            asyncio.run(poster.login_instagram())
    
    elif command == "post":
        if len(args) < 2:
            print("❌ Especifique o arquivo: python auto_poster.py post video.mp4")
            return
        
        video_path = args[1]
        if not os.path.exists(video_path):
            video_path = os.path.join(OUTPUT_DIR, args[1])
        
        video = VideoPost(
            video_path=video_path,
            caption="🔥 Confira essas IAs incríveis!",
            hashtags=["#IA", "#TechTok", "#FerramentasIA"],
            platform="tiktok"
        )
        asyncio.run(poster.post_to_tiktok(video))
    
    elif command == "queue":
        auto_add_output_to_queue()
        asyncio.run(process_queue())
    
    elif command == "add-queue":
        auto_add_output_to_queue()
    
    elif command == "show-queue":
        queue = load_queue()
        print(f"\n📋 FILA DE POSTAGEM ({len(queue)} vídeos)")
        print("-"*50)
        for i, item in enumerate(queue, 1):
            status = "✅" if item.get("posted") else "⏳"
            print(f"{i}. {status} {os.path.basename(item['video_path'])} → {item['platform']}")
    
    else:
        print("""
🤖 AUTO POSTER - TikTok & Instagram

Comandos:
    python auto_poster.py login tiktok      - Login no TikTok
    python auto_poster.py login instagram   - Login no Instagram
    python auto_poster.py post video.mp4    - Posta um vídeo
    python auto_poster.py add-queue         - Adiciona vídeos à fila
    python auto_poster.py show-queue        - Mostra fila
    python auto_poster.py queue             - Processa fila

⚠️ AVISO: Use com moderação para evitar banimento!
        """)


if __name__ == "__main__":
    main()
