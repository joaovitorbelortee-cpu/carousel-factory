import os
import time
import json
from datetime import datetime

WATCH_DIR = "."
OUTPUT_DIR = "output"
STATUS_FILE = "agent_status.json"

def get_dir_fingerprint(directory):
    fingerprint = {}
    for root, dirs, files in os.walk(directory):
        if ".git" in root or "__pycache__" in root or ".tmp" in root or ".vercel" in root:
            continue
        for file in files:
            path = os.path.join(root, file)
            try:
                fingerprint[path] = os.path.getmtime(path)
            except:
                pass
    return fingerprint

def monitor():
    print("🚀 Agent Monitor Iniciado...")
    print("Monitorando mudanças a cada 60 segundos...")
    
    last_fingerprint = get_dir_fingerprint(WATCH_DIR)
    
    while True:
        try:
            time.sleep(60)
            current_fingerprint = get_dir_fingerprint(WATCH_DIR)
            
            changes = []
            for path, mtime in current_fingerprint.items():
                if path not in last_fingerprint or mtime > last_fingerprint[path]:
                    changes.append(path)
            
            if changes:
                print(f"🔔 Mudanças detectadas em {len(changes)} arquivos!")
                status = {
                    "last_update": datetime.now().isoformat(),
                    "changed_files": changes,
                    "msg": "O projeto foi modificado. Antigravity está pronto para sugerir melhorias baseadas nessas mudanças."
                }
                with open(STATUS_FILE, "w") as f:
                    json.dump(status, f, indent=4)
                
                last_fingerprint = current_fingerprint
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Sem mudanças. Tudo sob controle.")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro no monitor: {e}")

if __name__ == "__main__":
    monitor()
