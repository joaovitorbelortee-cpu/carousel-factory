"""
CLI - Interface de Linha de Comando Unificada (BMad-CORE: Automate)
Ponto de entrada único para todas as funcionalidades do Viral Bot
"""

import sys
import asyncio
from typing import Optional


BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║      🎬 VIRAL BOT v3.0 - Gerador de Vídeos Virais 🎬      ║
║                                                           ║
║         TikTok • Instagram • 100% Automático              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""

HELP = """
📋 COMANDOS DISPONÍVEIS:

  generate [n]      Gera [n] vídeos (padrão: 5)
  test              Gera 1 vídeo de teste
  schedule          Gerencia scheduler
  post              Gerencia postagens
  analytics         Mostra métricas
  config            Gerencia configurações
  status            Mostra status do sistema
  help              Mostra esta ajuda

📌 EXEMPLOS:

  python cli.py generate 10     Gera 10 vídeos
  python cli.py test            Testa o sistema
  python cli.py schedule start  Inicia scheduler
  python cli.py analytics       Mostra dashboard
  python cli.py config show     Mostra configurações
"""


def cmd_generate(args: list):
    """Comando para gerar vídeos."""
    num = int(args[0]) if args else 5
    use_trends = "--no-trends" not in args
    
    print(f"\n🎬 Gerando {num} vídeos...")
    print(f"   Trends: {'Sim' if use_trends else 'Não'}\n")
    
    async def run():
        from main import run_full_pipeline
        return await run_full_pipeline(num, use_trends)
    
    videos = asyncio.run(run())
    
    print(f"\n✅ {len(videos)} vídeos gerados!")
    return videos


def cmd_test(args: list):
    """Comando para testar o sistema."""
    print("\n🔬 Executando teste rápido...\n")
    return cmd_generate(["1", "--no-trends"])


def cmd_schedule(args: list):
    """Comando para gerenciar scheduler."""
    from scheduler import main as scheduler_main
    
    if not args:
        args = ["help"]
    
    sys.argv = ["scheduler.py"] + args
    scheduler_main()


def cmd_post(args: list):
    """Comando para gerenciar postagens."""
    from auto_poster import main as poster_main
    
    if not args:
        args = ["help"]
    
    sys.argv = ["auto_poster.py"] + args
    poster_main()


def cmd_analytics(args: list):
    """Comando para mostrar analytics."""
    from analytics import analytics
    analytics.print_dashboard()


def cmd_config(args: list):
    """Comando para gerenciar configurações."""
    from config_manager import config_manager
    
    if not args or args[0] == "show":
        config_manager.print_config()
    elif args[0] == "save":
        config_manager.save()
        print("✅ Configurações salvas!")
    elif len(args) >= 2:
        key = args[0]
        value = args[1]
        config_manager.set(key, value)
        print(f"✅ {key} = {value}")


def cmd_status(args: list):
    """Comando para mostrar status do sistema."""
    import os
    from utils import check_dependencies, format_size
    
    print("\n" + "="*50)
    print("📊 STATUS DO SISTEMA")
    print("="*50)
    
    # Dependências
    deps = check_dependencies()
    print("\n📦 Dependências:")
    for dep, ok in deps.items():
        status = "✅" if ok else "❌"
        print(f"   {status} {dep}")
    
    # Arquivos
    project_dir = os.path.dirname(__file__)
    py_files = [f for f in os.listdir(project_dir) if f.endswith(".py")]
    print(f"\n📁 Arquivos Python: {len(py_files)}")
    
    # Vídeos gerados
    output_dir = os.path.join(project_dir, "output")
    if os.path.exists(output_dir):
        videos = [f for f in os.listdir(output_dir) if f.endswith(".mp4")]
        print(f"🎬 Vídeos gerados: {len(videos)}")
        
        total_size = sum(
            os.path.getsize(os.path.join(output_dir, f))
            for f in videos
        )
        print(f"💾 Tamanho total: {format_size(total_size)}")
    
    print("="*50 + "\n")


def cmd_batch(args: list):
    """Comando para geração em lote."""
    num = int(args[0]) if args else 5
    
    print(f"\n🚀 Iniciando geração em lote de {num} vídeos...")
    
    async def run():
        from batch_generator import quick_batch
        return await quick_batch(num)
    
    return asyncio.run(run())


def cmd_thumbnail(args: list):
    """Comando para gerar thumbnails."""
    from thumbnail_generator import thumbnail_gen
    
    if args and args[0].endswith(".mp4"):
        thumb = thumbnail_gen.create_from_video(args[0])
    else:
        title = " ".join(args) if args else "Video Viral"
        thumb = thumbnail_gen.create_viral_thumbnail(title)
    
    print(f"✅ Thumbnail: {thumb}")


COMMANDS = {
    "generate": cmd_generate,
    "test": cmd_test,
    "schedule": cmd_schedule,
    "post": cmd_post,
    "analytics": cmd_analytics,
    "config": cmd_config,
    "status": cmd_status,
    "batch": cmd_batch,
    "thumbnail": cmd_thumbnail,
    "help": lambda _: print(HELP),
}


def main():
    """Função principal da CLI."""
    print(BANNER)
    
    args = sys.argv[1:] if len(sys.argv) > 1 else ["help"]
    
    command = args[0].lower()
    command_args = args[1:]
    
    if command in COMMANDS:
        try:
            COMMANDS[command](command_args)
        except KeyboardInterrupt:
            print("\n\n⏹️ Operação cancelada pelo usuário")
        except Exception as e:
            print(f"\n❌ Erro: {e}")
    else:
        print(f"❌ Comando desconhecido: {command}")
        print(HELP)


if __name__ == "__main__":
    main()
