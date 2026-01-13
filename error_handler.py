"""
Error Handler - Tratamento centralizado de erros (BMad-CORE: Refine)
"""

import sys
import traceback
from datetime import datetime
from typing import Callable, Any, Optional
from functools import wraps

try:
    from logger import get_logger
    logger = get_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ViralBotError(Exception):
    """Exceção base do Viral Bot."""
    pass


class DependencyError(ViralBotError):
    """Erro de dependência não encontrada."""
    pass


class AudioGenerationError(ViralBotError):
    """Erro na geração de áudio."""
    pass


class ImageGenerationError(ViralBotError):
    """Erro na geração de imagens."""
    pass


class VideoGenerationError(ViralBotError):
    """Erro na geração de vídeo."""
    pass


class NetworkError(ViralBotError):
    """Erro de rede/API."""
    pass


class CacheError(ViralBotError):
    """Erro de cache."""
    pass


def handle_error(error: Exception, context: str = "") -> str:
    """
    Trata um erro de forma centralizada.
    Loga o erro e retorna mensagem amigável.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Determinar tipo de erro
    if isinstance(error, DependencyError):
        error_type = "DEPENDÊNCIA"
    elif isinstance(error, AudioGenerationError):
        error_type = "ÁUDIO"
    elif isinstance(error, ImageGenerationError):
        error_type = "IMAGEM"
    elif isinstance(error, VideoGenerationError):
        error_type = "VÍDEO"
    elif isinstance(error, NetworkError):
        error_type = "REDE"
    elif isinstance(error, CacheError):
        error_type = "CACHE"
    else:
        error_type = "GERAL"
    
    # Montar mensagem
    msg = f"[{timestamp}] ERRO {error_type}"
    if context:
        msg += f" em {context}"
    msg += f": {str(error)}"
    
    # Logar
    logger.error(msg)
    
    # Salvar em arquivo de log
    try:
        log_file = "output/logs/errors.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
            f.write(traceback.format_exc() + "\n\n")
    except:
        pass
    
    return msg


def safe_execute(func: Callable, *args, default: Any = None, context: str = "", **kwargs) -> Any:
    """
    Executa uma função de forma segura, tratando erros.
    Retorna default em caso de erro.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_error(e, context or func.__name__)
        return default


def error_handler(context: str = "", reraise: bool = False, default: Any = None):
    """
    Decorator para tratamento de erros.
    
    Args:
        context: Contexto para mensagem de erro
        reraise: Se deve relançar a exceção após tratar
        default: Valor padrão a retornar em caso de erro
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handle_error(e, context or func.__name__)
                if reraise:
                    raise
                return default
        return wrapper
    return decorator


def async_error_handler(context: str = "", reraise: bool = False, default: Any = None):
    """
    Decorator para tratamento de erros em funções async.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                handle_error(e, context or func.__name__)
                if reraise:
                    raise
                return default
        return wrapper
    return decorator


def retry_on_error(max_retries: int = 3, delay: float = 1.0, 
                   exceptions: tuple = (Exception,)):
    """
    Decorator para retry automático em caso de erro.
    
    Args:
        max_retries: Número máximo de tentativas
        delay: Tempo de espera entre tentativas (segundos)
        exceptions: Tupla de exceções que devem disparar retry
    """
    import time
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Tentativa {attempt + 1}/{max_retries} falhou: {e}")
                        time.sleep(delay)
                    else:
                        handle_error(e, f"{func.__name__} (após {max_retries} tentativas)")
            raise last_error
        return wrapper
    return decorator


def graceful_shutdown(error: Optional[Exception] = None, message: str = ""):
    """
    Encerra o programa de forma graciosa.
    """
    if error:
        handle_error(error, "shutdown")
        logger.error(f"Encerrando devido a erro: {error}")
    
    if message:
        logger.info(message)
    
    logger.info("Sistema encerrado.")
    sys.exit(1 if error else 0)


# Teste
if __name__ == "__main__":
    print("🔧 Testando error_handler.py...")
    
    @error_handler(context="teste", default="fallback")
    def func_com_erro():
        raise ValueError("Erro de teste!")
    
    result = func_com_erro()
    print(f"Resultado com erro: {result}")
    
    @retry_on_error(max_retries=3, delay=0.1)
    def func_com_retry():
        import random
        if random.random() < 0.7:
            raise ConnectionError("Falha de conexão")
        return "sucesso!"
    
    try:
        result = func_com_retry()
        print(f"Resultado com retry: {result}")
    except Exception as e:
        print(f"Falhou após retries: {e}")
