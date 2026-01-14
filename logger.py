import logging
import os
import sys
from datetime import datetime

# Detectar ambiente serverless (Vercel)
IS_SERVERLESS = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

# Configurar diretório de logs (apenas se não for serverless)
if not IS_SERVERLESS:
    LOG_DIR = os.path.join(os.path.dirname(__file__), "output", "logs")
    os.makedirs(LOG_DIR, exist_ok=True)
    log_filename = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = os.path.join(LOG_DIR, log_filename)
else:
    log_path = None

# Configuração do Logger
logger = logging.getLogger("ViralBot")
logger.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

# File Handler (Salva no arquivo) - apenas localmente
if log_path:
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Stream Handler (Mostra no console/logs da plataforma)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def get_logger():
    return logger

# Teste
if __name__ == "__main__":
    logger.info("Sistema de logs iniciado com sucesso")
    logger.warning("Isso é um aviso")
    logger.error("Isso é um erro")