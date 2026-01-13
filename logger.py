import logging
import os
import sys
from datetime import datetime

# Configurar diretório de logs
LOG_DIR = os.path.join(os.path.dirname(__file__), "output", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Nome do arquivo de log com data
log_filename = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_path = os.path.join(LOG_DIR, log_filename)

# Configuração do Logger
logger = logging.getLogger("ViralBot")
logger.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

# File Handler (Salva no arquivo)
file_handler = logging.FileHandler(log_path, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Stream Handler (Mostra no console)
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