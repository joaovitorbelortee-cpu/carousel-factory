"""
Scheduler - Agenda geração automática de vídeos
Roda em background e gera vídeos diariamente

Uso:
    python scheduler.py start          # Inicia o scheduler em background
    python scheduler.py run-now        # Executa uma vez agora
    python scheduler.py status         # Mostra status
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict
import sched
import time
import threading

# Caminho do projeto
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
SCHEDULE_FILE = os.path.join(PROJECT_DIR, "schedule_config.json")
LOG_FILE = os.path.join(OUTPUT_DIR, "scheduler.log")


# Configuração padrão
DEFAULT_CONFIG = {
    "enabled": True,
    "videos_per_day": 5,
    "generation_time": "06:00",  # Horário para gerar vídeos
    "use_trends": True,
    "nicho": "ferramentas de IA",
    "last_run": None,
    "total_videos_generated": 0,
}


def log(message: str):
    """Registra log com timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    # Salvar em arquivo
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


def load_config() -> Dict:
    """Carrega configuração do scheduler."""
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict):
    """Salva configuração do scheduler."""
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(config, f, indent=2, default=str)


def get_next_run_time(generation_time: str) -> datetime:
    """Calcula próximo horário de execução."""
    now = datetime.now()
    hour, minute = map(int, generation_time.split(":"))
    
    next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    if next_run <= now:
        next_run += timedelta(days=1)
    
    return next_run


async def generate_videos_task(config: Dict):
    """Tarefa de geração de vídeos."""
    log("🚀 Iniciando geração automática de vídeos...")
    
    try:
        # Importar e executar o main
        from main import run_full_pipeline
        
        videos = await run_full_pipeline(
            num_videos=config["videos_per_day"],
            use_trends=config["use_trends"]
        )
        
        # Atualizar config
        config["last_run"] = datetime.now().isoformat()
        config["total_videos_generated"] += len(videos)
        save_config(config)
        
        log(f"✅ Gerados {len(videos)} vídeos com sucesso!")
        log(f"📁 Salvos em: {OUTPUT_DIR}")
        
        # Listar vídeos gerados
        for video in videos:
            log(f"   → {os.path.basename(video)}")
        
        return videos
        
    except Exception as e:
        log(f"❌ Erro na geração: {e}")
        return []


def run_scheduler_loop(config: Dict):
    """Loop principal do scheduler."""
    log("⏰ Scheduler iniciado!")
    log(f"📅 Configuração: {config['videos_per_day']} vídeos/dia às {config['generation_time']}")
    
    while config.get("enabled", True):
        next_run = get_next_run_time(config["generation_time"])
        wait_seconds = (next_run - datetime.now()).total_seconds()
        
        log(f"⏳ Próxima execução: {next_run.strftime('%Y-%m-%d %H:%M')}")
        log(f"   Aguardando {wait_seconds/3600:.1f} horas...")
        
        # Aguardar até o horário
        time.sleep(max(0, wait_seconds))
        
        # Executar geração
        asyncio.run(generate_videos_task(config))
        
        # Recarregar config para pegar mudanças
        config = load_config()


def run_once():
    """Executa uma vez agora."""
    log("▶️ Executando geração manual...")
    config = load_config()
    asyncio.run(generate_videos_task(config))


def show_status():
    """Mostra status do scheduler."""
    config = load_config()
    
    print("\n" + "="*50)
    print("📊 STATUS DO SCHEDULER")
    print("="*50)
    print(f"✅ Habilitado: {'Sim' if config['enabled'] else 'Não'}")
    print(f"🎬 Vídeos por dia: {config['videos_per_day']}")
    print(f"⏰ Horário de geração: {config['generation_time']}")
    print(f"🔍 Usar trends: {'Sim' if config['use_trends'] else 'Não'}")
    print(f"📅 Última execução: {config['last_run'] or 'Nunca'}")
    print(f"📊 Total gerados: {config['total_videos_generated']}")
    
    next_run = get_next_run_time(config["generation_time"])
    print(f"⏳ Próxima execução: {next_run.strftime('%Y-%m-%d %H:%M')}")
    print("="*50 + "\n")


def configure_scheduler():
    """Configuração interativa do scheduler."""
    config = load_config()
    
    print("\n⚙️ CONFIGURAÇÃO DO SCHEDULER")
    print("-"*40)
    
    # Vídeos por dia
    try:
        num = input(f"Vídeos por dia [{config['videos_per_day']}]: ").strip()
        if num:
            config["videos_per_day"] = int(num)
    except:
        pass
    
    # Horário
    horario = input(f"Horário de geração [{config['generation_time']}]: ").strip()
    if horario:
        config["generation_time"] = horario
    
    # Trends
    trends = input(f"Usar trends? (s/n) [{'s' if config['use_trends'] else 'n'}]: ").strip().lower()
    if trends:
        config["use_trends"] = trends == 's'
    
    save_config(config)
    print("\n✅ Configuração salva!")
    show_status()


def create_windows_task():
    """Cria tarefa agendada no Windows."""
    script_path = os.path.join(PROJECT_DIR, "scheduler.py")
    python_path = sys.executable
    
    # Comando para criar tarefa
    task_name = "ViralBot_DailyGeneration"
    config = load_config()
    schedule_time = config["generation_time"]
    
    cmd = f'''schtasks /create /tn "{task_name}" /tr "\\"{python_path}\\" \\"{script_path}\\" run-now" /sc daily /st {schedule_time} /f'''
    
    print(f"\n📅 Para agendar no Windows, execute como admin:")
    print(f"\n{cmd}\n")
    
    return cmd


def main():
    """Função principal."""
    args = sys.argv[1:] if len(sys.argv) > 1 else ["help"]
    
    command = args[0].lower() if args else "help"
    
    if command == "start":
        config = load_config()
        run_scheduler_loop(config)
    
    elif command == "run-now":
        run_once()
    
    elif command == "status":
        show_status()
    
    elif command == "config":
        configure_scheduler()
    
    elif command == "windows-task":
        create_windows_task()
    
    else:
        print("""
🤖 VIRAL BOT - SCHEDULER

Comandos:
    python scheduler.py start        - Inicia o scheduler (roda infinito)
    python scheduler.py run-now      - Gera vídeos agora
    python scheduler.py status       - Mostra status
    python scheduler.py config       - Configurar scheduler
    python scheduler.py windows-task - Mostra comando p/ agendar no Windows

Exemplos:
    python scheduler.py run-now      # Testar agora
    python scheduler.py config       # Configurar horário
        """)


if __name__ == "__main__":
    main()
