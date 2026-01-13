"""
Logging estruturado para o Viral Bot
Suporta formato JSON e texto simples
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Formatter que gera logs em JSON."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adicionar exceção se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Adicionar campos extras
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Formatter colorido para terminal."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str = "viral_bot",
    level: str = "INFO",
    format_type: str = "colored",
    log_file: str = None
) -> logging.Logger:
    """
    Configura e retorna um logger.
    
    Args:
        name: Nome do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: 'json', 'colored' ou 'simple'
        log_file: Caminho para arquivo de log (opcional)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Limpar handlers existentes
    logger.handlers.clear()
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    
    if format_type == "json":
        console_handler.setFormatter(JSONFormatter())
    elif format_type == "colored":
        console_handler.setFormatter(ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        ))
    else:
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        ))
    
    logger.addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    return logger


# Logger global padrão
default_logger = setup_logger()


def get_logger(name: str = None) -> logging.Logger:
    """Retorna o logger padrão ou um específico."""
    if name:
        return setup_logger(name)
    return default_logger


# Funções de conveniência
def log_info(message: str, **kwargs):
    default_logger.info(message, extra={'extra_data': kwargs} if kwargs else {})

def log_error(message: str, **kwargs):
    default_logger.error(message, extra={'extra_data': kwargs} if kwargs else {})

def log_warning(message: str, **kwargs):
    default_logger.warning(message, extra={'extra_data': kwargs} if kwargs else {})

def log_debug(message: str, **kwargs):
    default_logger.debug(message, extra={'extra_data': kwargs} if kwargs else {})
