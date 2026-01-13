"""
Utils - Funções utilitárias reutilizáveis (BMad-CORE: Modularize)
"""

import os
import sys
import shutil
import hashlib
from datetime import datetime
from typing import Optional, List
from pathlib import Path


# ============ VALIDAÇÕES ============

def check_dependencies() -> dict:
    """
    Verifica todas as dependências do sistema.
    Retorna dict com status de cada dependência.
    """
    status = {
        "python": True,
        "ffmpeg": False,
        "moviepy": False,
        "edge_tts": False,
        "pillow": False,
    }
    
    # FFmpeg
    status["ffmpeg"] = shutil.which("ffmpeg") is not None
    
    # MoviePy
    try:
        import moviepy.editor
        status["moviepy"] = True
    except ImportError:
        pass
    
    # Edge TTS
    try:
        import edge_tts
        status["edge_tts"] = True
    except ImportError:
        pass
    
    # Pillow
    try:
        from PIL import Image
        status["pillow"] = True
    except ImportError:
        pass
    
    return status


def validate_environment() -> bool:
    """
    Valida se o ambiente está pronto para execução.
    Retorna True se tudo OK, False se houver problemas críticos.
    """
    deps = check_dependencies()
    
    critical = ["moviepy", "edge_tts", "pillow"]
    for dep in critical:
        if not deps.get(dep, False):
            print(f"❌ ERRO: Dependência crítica não encontrada: {dep}")
            return False
    
    if not deps.get("ffmpeg"):
        print("⚠️ AVISO: FFmpeg não encontrado. Alguns recursos podem falhar.")
    
    return True


# ============ CACHE ============

def get_file_hash(filepath: str) -> str:
    """Gera hash MD5 de um arquivo para cache."""
    if not os.path.exists(filepath):
        return ""
    
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    
    return hash_md5.hexdigest()


def cache_exists(filepath: str, content_hash: str = None) -> bool:
    """
    Verifica se arquivo de cache existe e é válido.
    Se content_hash for fornecido, verifica se o conteúdo mudou.
    """
    if not os.path.exists(filepath):
        return False
    
    if content_hash:
        return get_file_hash(filepath) == content_hash
    
    return True


def clean_cache(cache_dir: str, max_age_hours: int = 24):
    """Remove arquivos de cache mais antigos que max_age_hours."""
    if not os.path.exists(cache_dir):
        return
    
    now = datetime.now().timestamp()
    max_age_seconds = max_age_hours * 3600
    
    count = 0
    for item in os.listdir(cache_dir):
        filepath = os.path.join(cache_dir, item)
        if os.path.isfile(filepath):
            file_age = now - os.path.getmtime(filepath)
            if file_age > max_age_seconds:
                os.remove(filepath)
                count += 1
    
    if count > 0:
        print(f"🗑️ Removidos {count} arquivos de cache antigos")


# ============ PATHS ============

def ensure_dir(dirpath: str) -> str:
    """Garante que diretório existe, cria se necessário."""
    os.makedirs(dirpath, exist_ok=True)
    return dirpath


def get_project_root() -> str:
    """Retorna o caminho raiz do projeto."""
    return os.path.dirname(os.path.abspath(__file__))


def get_output_dir() -> str:
    """Retorna o diretório de output."""
    return ensure_dir(os.path.join(get_project_root(), "output"))


def get_assets_dir() -> str:
    """Retorna o diretório de assets."""
    return ensure_dir(os.path.join(get_output_dir(), "assets"))


def get_cache_dir() -> str:
    """Retorna o diretório de cache."""
    return ensure_dir(os.path.join(get_project_root(), "cache"))


def get_logs_dir() -> str:
    """Retorna o diretório de logs."""
    return ensure_dir(os.path.join(get_output_dir(), "logs"))


# ============ FORMATAÇÃO ============

def format_size(bytes_size: int) -> str:
    """Formata tamanho em bytes para formato legível."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def format_duration(seconds: float) -> str:
    """Formata duração em segundos para formato legível."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def sanitize_filename(filename: str) -> str:
    """Remove caracteres inválidos de nomes de arquivos."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


# ============ RETRY LOGIC ============

def retry(func, max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator para retry de funções que podem falhar.
    """
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    print(f"⚠️ Tentativa {attempt + 1} falhou. Retrying...")
                    time.sleep(delay)
        raise last_exception
    
    return wrapper


# ============ STATUS ============

def print_status(message: str, status: str = "info"):
    """Imprime mensagem de status formatada."""
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "progress": "🔄",
    }
    icon = icons.get(status, "•")
    print(f"{icon} {message}")


# Teste
if __name__ == "__main__":
    print("🔧 Testando utils.py...")
    
    deps = check_dependencies()
    print(f"\n📦 Dependências:")
    for dep, ok in deps.items():
        status = "✅" if ok else "❌"
        print(f"  {status} {dep}")
    
    print(f"\n📁 Diretórios:")
    print(f"  Root: {get_project_root()}")
    print(f"  Output: {get_output_dir()}")
    print(f"  Assets: {get_assets_dir()}")
    print(f"  Cache: {get_cache_dir()}")
    
    print(f"\n📊 Formatação:")
    print(f"  1234567 bytes = {format_size(1234567)}")
    print(f"  125 segundos = {format_duration(125)}")
