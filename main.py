"""
VIRAL BOT v3.0 - Gerador Automático de Vídeos Virais para TikTok/Instagram
🔍 BUSCA AVANÇADA de vídeos em alta no TikTok ANTES de criar
📊 Modela roteiros baseados nos trends
🎬 Gera vídeos DINÂMICOS com Ken Burns e música

100% Gratuito | Múltiplos nichos disponíveis
"""

import asyncio
import os
import sys
import shutil
from datetime import datetime
from typing import List, Dict

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# External imports
from tqdm import tqdm

# Imports locais
from logger import get_logger
from content_modeler import ContentModeler, generate_modeled_content
from tts_engine import generate_audio
from image_generator import generate_all_images_for_video
from video_engine import create_video_from_images_and_audio
from trend_researcher import research_before_creating, TrendResearcher

# Configurar Logger
logger = get_logger()

# Fallback para content.py se modeler falhar
try:
    from content import VIDEOS as FALLBACK_VIDEOS
except ImportError:
    FALLBACK_VIDEOS = []

# Configurações
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
ASSETS_DIR = os.path.join(OUTPUT_DIR, "assets")


def setup():
    """Cria diretórios necessários e valida ambiente."""
    logger.info("🛠️ Configurando ambiente...")
    
    # Criar diretórios
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "cache"), exist_ok=True)
    
    # Validações
    try:
        import moviepy.editor
    except ImportError:
        logger.error("❌ ERRO CRÍTICO: 'moviepy' não está instalado.")
        sys.exit(1)
        
    try:
        import edge_tts
    except ImportError:
        logger.error("❌ ERRO CRÍTICO: 'edge_tts' não está instalado.")
        sys.exit(1)

    # Verificar FFmpeg (Sistema ou ImageIO)
    ffmpeg_available = False
    
    if shutil.which("ffmpeg"):
        ffmpeg_available = True
    else:
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            logger.info(f"✅ FFmpeg configurado via imageio-ffmpeg: {ffmpeg_exe}")
            ffmpeg_available = True
            
            # Opcional: Configurar para MoviePy explicitamente se necessário
            # mas geralmente o MoviePy detecta via imageio automaticamente
        except ImportError:
            pass

    if not ffmpeg_available:
        logger.error("❌ ERRO CRÍTICO: FFmpeg não encontrado no PATH nem via imageio-ffmpeg!")
        raise Exception("FFmpeg não instalado! Instale-o e adicione ao PATH ou instale imageio-ffmpeg.")
    
    logger.info(f"✅ Diretórios e dependências verificados. (FFmpeg: {'OK' if ffmpeg_available else 'FAIL'})")


def get_narration_text(video: Dict) -> str:
    """Extrai texto de narração de um vídeo."""
    lines = [video.get("hook", "")]
    
    for tool in video.get("tools", []):
        lines.append(f"{tool['name']}. {tool['desc']}.")
    
    lines.append(video.get("cta", ""))
    
    return " ".join(lines)


async def generate_single_video(video: Dict) -> str:
    """
    Gera um único vídeo completo.
    
    Returns:
        Caminho do vídeo gerado
    """
    video_id = video["id"]
    niche_slug = video.get("niche", "default").replace(" ", "_").lower()[:20]
    video_path = os.path.join(OUTPUT_DIR, f"{niche_slug}_{video_id}_final.mp4")
    
    # Cache Check
    if os.path.exists(video_path):
        logger.info(f"⏭️ Vídeo {video_id} já existe! Pulando geração.")
        return video_path

    logger.info(f"\n{'='*60}")
    logger.info(f"🎬 VÍDEO {video_id}: {video['title']}")
    logger.info(f"{ '='*60}")
    
    # 1. Gerar texto de narração
    script = get_narration_text(video)
    logger.info(f"📜 Roteiro preparado ({len(script)} caracteres)")
    
    # 2. Gerar áudio
    audio_path = os.path.join(OUTPUT_DIR, f"audio_{niche_slug}_{video_id}.mp3")
    if not os.path.exists(audio_path):
        logger.info(f"🔊 Gerando áudio...")
        await generate_audio(script, audio_path, voice="masculina", rate="+15%")
    else:
        logger.info(f"⏭️ Áudio já existe. Usando cache.")
    
    # 3. Gerar imagens
    logger.info(f"🖼️ Gerando imagens...")
    images = generate_all_images_for_video(video, ASSETS_DIR)
    logger.info(f"   → {len(images)} imagens prontas")
    
    # 4. Montar vídeo
    logger.info(f"🎥 Montando vídeo final...")
    create_video_from_images_and_audio(images, audio_path, video_path)
    
    return video_path


async def run_full_pipeline(num_videos: int = 5, use_trends: bool = True, niche: str = "ai_tools", progress_callback=None) -> List[str]:
    """
    Pipeline completo v3.0:
    0. BUSCA AVANÇADA de tendências no TikTok
    1. Modela roteiros baseados nos trends
    2. Gera vídeos DINÂMICOS
    
    Args:
        num_videos: Quantidade de vídeos
        use_trends: Se deve buscar trends
        niche: Nicho do conteúdo
        progress_callback: Função async para reportar progresso. Recebe dict.
    """
    print("\n" + "🚀"*30)
    print("     VIRAL BOT v3.0 - INICIANDO")
    print("     Busca Avançada + Modelagem + Geração Dinâmica")
    print("🚀"*30 + "\n")
    
    setup()
    
    # Função auxiliar para chamar callback com segurança
    async def report_progress(current, total, msg):
        if progress_callback:
            try:
                await progress_callback({
                    "current": current,
                    "total": total,
                    "message": msg
                })
            except Exception as e:
                logger.error(f"Erro no callback de progresso: {e}")

    await report_progress(0, num_videos, f"Iniciando pesquisa de trends para '{niche}'...")
    
    # ETAPA 0: BUSCA AVANÇADA DE TENDÊNCIAS (NOVO!)
    trend_recommendations = None
    if use_trends:
        logger.info("🔍 ETAPA 0: BUSCA AVANÇADA DE TENDÊNCIAS")
        logger.info(f"   Nicho: {niche}")
        
        try:
            trend_result = await research_before_creating(niche)
            trend_recommendations = trend_result.get("recommendations", {})
            
            logger.info(f"✅ Tendências encontradas!")
            logger.info(f"   → Duração sugerida: {trend_recommendations.get('suggested_duration', 30)}s")
            logger.info(f"   → Estilo: {trend_recommendations.get('suggested_style', 'listicle')}")
            logger.info(f"   → Hashtags: {', '.join(trend_recommendations.get('suggested_hashtags', [])[:3])}")
        except Exception as e:
            logger.warning(f"⚠️ Erro na busca de trends: {e}")
            logger.info("   Continuando sem dados de tendências...")
    
    # ETAPA 1: Pesquisar trends e gerar roteiros
    await report_progress(0, num_videos, "Modelando roteiros com IA...")
    if use_trends:
        logger.info("📊 ETAPA 1: MODELAGEM DE CONTEÚDO")
        
        try:
            videos = await generate_modeled_content(num_videos, niche=niche)
            logger.info(f"✅ {len(videos)} roteiros modelados gerados!")
        except Exception as e:
            logger.error(f"⚠️ Erro na modelagem: {e}")
            logger.info("📋 Usando roteiros de backup...")
            videos = FALLBACK_VIDEOS[:num_videos]
    else:
        videos = FALLBACK_VIDEOS[:num_videos]
    
    if not videos:
        logger.error("❌ Nenhum roteiro disponível!")
        await report_progress(0, num_videos, "Erro: Nenhum roteiro disponível.")
        return []
    
    # ETAPA 2: Gerar vídeos DINÂMICOS
    logger.info("🎬 ETAPA 2: GERAÇÃO DE VÍDEOS DINÂMICOS")
    
    generated_videos = []
    start_time = datetime.now()
    
    # Progress Bar com TQDM
    pbar = tqdm(videos, desc="Gerando Vídeos", unit="vídeo")
    
    for i, video in enumerate(pbar):
        try:
            video["niche"] = niche # Injetar nicho para nome do arquivo
            msg = f"Gerando Vídeo {i+1}/{len(videos)}: {video.get('title', 'Sem título')}"
            pbar.set_description(f"Gerando Vídeo {video['id']} ({niche})")
            await report_progress(i+1, len(videos), msg)
            
            # Limpar assets temporários para garantir imagens novas
            if os.path.exists(ASSETS_DIR):
                for f in os.listdir(ASSETS_DIR):
                    try: os.remove(os.path.join(ASSETS_DIR, f))
                    except: pass
                    
            video_path = await generate_single_video(video)
            generated_videos.append(video_path)
            logger.info(f"✅ Vídeo {video['id']} concluído!")
        except Exception as e:
            logger.error(f"❌ Erro no vídeo {video['id']}: {e}")
            continue
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # RESUMO FINAL
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMO DA PRODUÇÃO")
    logger.info("="*60)
    logger.info(f"🔍 Trends pesquisados: {'Sim' if use_trends else 'Não'}")
    logger.info(f"✅ Vídeos gerados: {len(generated_videos)}/{num_videos}")
    logger.info(f"⏱️ Tempo total: {duration:.1f} segundos")
    logger.info(f"📂 Pasta de saída: {OUTPUT_DIR}")
    
    if generated_videos:
        print("\n📁 Arquivos gerados:")
        for path in generated_videos:
            if os.path.exists(path):
                size_mb = os.path.getsize(path) / (1024 * 1024)
                print(f"   → {os.path.basename(path)} ({size_mb:.1f} MB)")
    
    return generated_videos


async def main():
    """Função principal."""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Processar argumentos
    num_videos = 5
    use_trends = True
    niche = "ai_tools"
    
    for arg in args:
        if arg.startswith("--num="):
            num_videos = int(arg.split("=")[1])
        elif arg.startswith("--niche="):
            niche = arg.split("=")[1].strip('"').strip("'")
        elif arg == "--no-trends":
            use_trends = False
        elif arg == "--help":
            print("""
VIRAL BOT v3.0 - Gerador de Vídeos Virais

Uso: python main.py [opções]

Opções:
  --num=N       Número de vídeos a gerar (padrão: 5)
  --niche="TOPICO" Nicho para pesquisa e geração (padrão: ai_tools)
  --no-trends   Não pesquisar trends, usar roteiros fixos
  --help        Mostrar esta ajuda
            """)
            return
    
    # Executar pipeline
    videos = await run_full_pipeline(num_videos, use_trends, niche=niche)
    
    if len(videos) == num_videos:
        logger.info("🎉 SUCESSO! Todos os vídeos foram gerados!")
        print("\n📤 Pronto para upload no TikTok e Instagram!")
    else:
        logger.warning(f"⚠️ Gerados {len(videos)}/{num_videos} vídeos")


if __name__ == "__main__":
    asyncio.run(main())
