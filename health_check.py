"""
Health Check para o Viral Bot
Endpoint para monitoramento de status do sistema
"""

import os
import sys
import psutil
from datetime import datetime


def get_health_status() -> dict:
    """
    Retorna status de saúde do sistema.
    
    Returns:
        Dict com métricas de saúde
    """
    process = psutil.Process()
    
    # Verificar módulos
    modules_ok = True
    required_modules = ['flask', 'moviepy', 'edge_tts', 'PIL']
    missing_modules = []
    
    for mod in required_modules:
        try:
            __import__(mod)
        except ImportError:
            modules_ok = False
            missing_modules.append(mod)
    
    # Verificar diretórios
    base_dir = os.path.dirname(__file__)
    output_dir = os.path.join(base_dir, "output")
    cache_dir = os.path.join(base_dir, ".tmp", "cache")
    
    dirs_ok = all([
        os.path.exists(output_dir),
        os.path.exists(cache_dir) or True  # Cache opcional
    ])
    
    # Contar vídeos
    video_count = 0
    if os.path.exists(output_dir):
        video_count = len([f for f in os.listdir(output_dir) if f.endswith('.mp4')])
    
    return {
        "status": "healthy" if modules_ok and dirs_ok else "degraded",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": round(psutil.boot_time(), 2),
        "system": {
            "python_version": sys.version.split()[0],
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": round(process.memory_percent(), 2),
            "disk_usage_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
        },
        "modules": {
            "all_loaded": modules_ok,
            "missing": missing_modules
        },
        "directories": {
            "output_exists": os.path.exists(output_dir),
            "cache_exists": os.path.exists(cache_dir)
        },
        "videos": {
            "total_generated": video_count
        }
    }


def check_dependencies() -> dict:
    """Verifica todas as dependências do projeto."""
    dependencies = {
        "flask": False,
        "moviepy": False,
        "edge_tts": False,
        "PIL": False,
        "tqdm": False,
        "python-dotenv": False,
    }
    
    for dep in dependencies.keys():
        try:
            if dep == "python-dotenv":
                __import__("dotenv")
            else:
                __import__(dep)
            dependencies[dep] = True
        except ImportError:
            pass
    
    return dependencies


if __name__ == "__main__":
    import json
    print(json.dumps(get_health_status(), indent=2))
