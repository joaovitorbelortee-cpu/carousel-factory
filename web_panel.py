"""
Viral Bot - Painel Web (BENTO GRID EDITION + SETTINGS)
Estilo visual inspirado em Shopify Editions Winter 2026.
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import os
import threading
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Imports do projeto
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Carregar .env
load_dotenv()

app = Flask(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output", "carousel")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# HTML SUPER MODERNO (BENTO GRID STYLE)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAROUSEL KING // EDITIONS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');
        
        :root {
            --bg-color: #050505;
            --card-bg: #111111;
            --border-color: #222222;
            --accent: #D4AF37; /* Ouro */
            --accent-glow: rgba(212, 175, 55, 0.3);
            --text-main: #FFFFFF;
            --text-dim: #888888;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            overflow-x: hidden;
        }

        h1, h2, h3, .display-font {
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: -0.04em;
        }

        /* BENTO GRID SYSTEM */
        .bento-grid {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 16px;
            padding: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }

        .bento-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 24px;
            position: relative;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .bento-card:hover {
            border-color: var(--accent);
            box-shadow: 0 0 30px var(--accent-glow);
            transform: translateY(-2px);
            z-index: 10;
        }

        /* GRID POSITIONS */
        .col-span-12 { grid-column: span 12; }
        .col-span-8 { grid-column: span 8; }
        .col-span-6 { grid-column: span 6; }
        .col-span-4 { grid-column: span 4; }
        .col-span-3 { grid-column: span 3; }
        
        .row-span-2 { grid-row: span 2; }

        /* ELEMENTS */
        .glass-input {
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border-color);
            color: white;
            padding: 16px;
            border-radius: 12px;
            width: 100%;
            font-size: 1.1rem;
            transition: 0.3s;
        }
        .glass-input:focus {
            border-color: var(--accent);
            outline: none;
            background: rgba(255,255,255,0.05);
        }

        .btn-action {
            background: var(--text-main);
            color: var(--bg-color);
            font-weight: 800;
            padding: 16px 32px;
            border-radius: 100px;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: 0.3s;
            text-transform: uppercase;
        }
        .btn-action:hover {
            background: var(--accent);
            transform: scale(1.05);
        }
        .btn-action:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        /* ANIMATED BACKGROUND */
        .noise-bg {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 0;
        }

        /* SCROLLING TEXT */
        .marquee-container {
            overflow: hidden;
            white-space: nowrap;
            position: absolute;
            opacity: 0.1;
            font-size: 8rem;
            font-weight: 800;
            font-family: 'Space Grotesk';
            pointer-events: none;
            user-select: none;
        }
        
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        }
        
        .gallery-img {
            width: 100%;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            transition: 0.3s;
            aspect-ratio: 4/5;
            object-fit: cover;
        }
        .gallery-img:hover {
            transform: scale(1.05);
            border-color: var(--accent);
            z-index: 5;
        }
        
        /* STATUS BAR */
        .progress-bar {
            height: 4px;
            background: var(--accent);
            width: 0%;
            transition: width 0.5s ease;
            position: absolute;
            bottom: 0;
            left: 0;
        }

        /* MOBILE RESPONSIVE */
        @media (max-width: 1024px) {
            .bento-grid { grid-template-columns: 1fr; }
            .col-span-12, .col-span-8, .col-span-6, .col-span-4, .col-span-3 { grid-column: span 1; }
        }
    </style>
</head>
<body>
    <div class="noise-bg"></div>

    <!-- HERO SECTION -->
    <div class="bento-grid">
        
        <!-- HEADER -->
        <div class="bento-card col-span-12 flex justify-between items-center" style="border: none; background: transparent;">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center text-black font-bold text-xl">CK</div>
                <div>
                    <h1 class="text-2xl font-bold">CAROUSEL KING</h1>
                    <p class="text-gray-500 text-sm tracking-widest">EDITIONS 2026 // v7.1</p>
                </div>
            </div>
            <div class="flex gap-4">
                <div class="px-4 py-2 rounded-full border border-gray-800 text-xs uppercase tracking-widest hover:bg-white hover:text-black transition-colors cursor-pointer" onclick="document.getElementById('settingsModal').showModal()">SETTINGS</div>
            </div>
        </div>

        <!-- SETTINGS MODAL -->
        <dialog id="settingsModal" class="bg-transparent backdrop:bg-black/80 p-0 rounded-2xl">
            <div class="bento-card w-[500px] max-w-full">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold">CONFIGURAÇÕES</h2>
                    <button onclick="document.getElementById('settingsModal').close()" class="text-gray-500 hover:text-white">✕</button>
                </div>
                
                <div class="space-y-4">
                    <div>
                        <label class="text-xs uppercase tracking-widest text-gray-500 mb-2 block">Google Gemini API Key</label>
                        <div class="relative">
                            <input type="password" id="apiKeyInput" class="glass-input pr-10" placeholder="Cole sua chave AI Studio aqui...">
                            <button onclick="togglePass()" class="absolute right-3 top-4 text-gray-500 hover:text-white">
                                <i data-lucide="eye" width="16"></i>
                            </button>
                        </div>
                        <p class="text-xs text-gray-600 mt-2">Necessário para gerar os roteiros. <a href="https://aistudio.google.com/app/apikey" target="_blank" class="text-white underline">Obter chave grátis</a></p>
                    </div>
                    
                    <div class="flex gap-4 mt-6">
                        <button onclick="saveSettings()" class="btn-action w-full justify-center">
                            <i data-lucide="save"></i> Salvar e Conectar
                        </button>
                    </div>
                </div>
            </div>
        </dialog>

        <!-- GENERATOR CARD (MAIN) -->
        <div class="bento-card col-span-8 row-span-2 flex flex-col justify-center relative">
            <div class="marquee-container" style="top: -20px; left: 0;">CREATE CREATE CREATE</div>
            
            <div class="relative z-10 max-w-2xl">
                <h2 class="text-5xl md:text-7xl font-bold mb-6 leading-tight">
                    CRIE O <span style="color: var(--accent);">VIRAL</span><br>
                    DO FUTURO.
                </h2>
                
                <div class="space-y-6">
                    <div>
                        <label class="text-xs uppercase tracking-widest text-gray-500 mb-2 block">Tópico do Conteúdo</label>
                        <input type="text" id="topicInput" class="glass-input" placeholder="Ex: A verdade sobre estoicismo...">
                    </div>
                    
                    <div class="flex gap-4">
                        <button class="btn-action" onclick="generate()" id="btnGen">
                            <i data-lucide="zap"></i>
                            Gerar Carrossel
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- STATS CARD -->
        <div class="bento-card col-span-4 flex flex-col justify-between">
            <h3 class="text-gray-500 text-sm uppercase">Engine Status</h3>
            <div class="text-4xl font-bold text-green-500 mt-2">ONLINE</div>
            <div class="mt-8 space-y-2">
                <div class="flex justify-between text-sm border-b border-gray-800 pb-2">
                    <span class="text-gray-500">Gemini Auth</span>
                    <span id="authStatus" class="text-red-500">Verificando...</span>
                </div>
                <div class="flex justify-between text-sm border-b border-gray-800 pb-2">
                    <span class="text-gray-500">Mode</span>
                    <span>Modo Caverna v4</span>
                </div>
                <div class="flex justify-between text-sm border-b border-gray-800 pb-2">
                    <span class="text-gray-500">Visual</span>
                    <span>Brutalist / Glitch</span>
                </div>
            </div>
        </div>

        <!-- RECENT ACTIVITY / LOGS -->
        <div class="bento-card col-span-4 flex flex-col h-64">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-gray-500 text-sm uppercase">Live Logs</h3>
                <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            </div>
            <div id="statusText" class="font-mono text-sm text-gray-400 overflow-y-auto flex-1">
                [SYSTEM] Ready to generate.<br>
                [SYSTEM] Waiting for user input...
            </div>
            <div class="progress-bar" id="progressBar"></div>
        </div>

        <!-- GALLERY PREVIEW -->
        <div class="bento-card col-span-12">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold">GALERIA RECENTE</h2>
                <button onclick="refreshGallery()" class="text-sm text-gray-500 hover:text-white transition">Refresh</button>
            </div>
            
            <div class="gallery-grid" id="galleryGrid">
                <!-- IMAGES WILL BE INJECTED HERE -->
                <div class="text-gray-600 text-center py-10 col-span-full">
                    Nenhum carrossel gerado nesta sessão.
                </div>
            </div>
        </div>

    </div>

    <script>
        // Init Icons
        lucide.createIcons();

        // Animations (GSAP)
        gsap.from(".bento-card", {
            y: 50,
            opacity: 0,
            duration: 0.8,
            stagger: 0.1,
            ease: "power3.out"
        });

        function togglePass() {
            const inp = document.getElementById('apiKeyInput');
            inp.type = inp.type === 'password' ? 'text' : 'password';
        }

        async function saveSettings() {
            const key = document.getElementById('apiKeyInput').value;
            if(!key) return alert("Digite a chave!");
            
            try {
                const res = await fetch('/save_settings', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ key })
                });
                const data = await res.json();
                if(data.success) {
                    alert("Conectado com sucesso!");
                    document.getElementById('settingsModal').close();
                    checkAuth();
                } else {
                    alert("Erro ao salvar.");
                }
            } catch(e) { console.error(e); }
        }

        async function checkAuth() {
            try {
                const res = await fetch('/check_auth');
                const data = await res.json();
                const el = document.getElementById('authStatus');
                if(data.connected) {
                    el.innerText = "CONECTADO";
                    el.className = "text-green-500";
                } else {
                    el.innerText = "DESCONECTADO";
                    el.className = "text-red-500";
                }
            } catch(e) {}
        }

        async function generate() {
            const topic = document.getElementById('topicInput').value;
            if (!topic) {
                alert("Digite um tópico!");
                return;
            }

            const btn = document.getElementById('btnGen');
            const statusDiv = document.getElementById('statusText');
            const bar = document.getElementById('progressBar');
            
            btn.disabled = true;
            btn.innerHTML = `<i data-lucide="loader-2" class="animate-spin"></i> Processando...`;
            lucide.createIcons();
            
            statusDiv.innerHTML += `<br>[USER] Gerando sobre: "${topic}"...`;
            statusDiv.scrollTop = statusDiv.scrollHeight;
            bar.style.width = "20%";

            try {
                const response = await fetch('/generate_carousel', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    statusDiv.innerHTML += `<br>[SUCCESS] ${data.message}`;
                    bar.style.width = "100%";
                    setTimeout(refreshGallery, 1000);
                } else {
                    statusDiv.innerHTML += `<br>[ERROR] ${data.message}`;
                    bar.style.background = "red";
                }
            } catch (err) {
                statusDiv.innerHTML += `<br>[FATAL] ${err.message}`;
            }
            
            statusDiv.scrollTop = statusDiv.scrollHeight;
            btn.disabled = false;
            btn.innerHTML = `<i data-lucide="zap"></i> Gerar Carrossel`;
            lucide.createIcons();
        }
        
        async function refreshGallery() {
            try {
                const response = await fetch('/list_images');
                const data = await response.json();
                const grid = document.getElementById('galleryGrid');
                
                if (data.images && data.images.length > 0) {
                    grid.innerHTML = data.images.map(img => `
                        <div class="relative group">
                            <img src="/image/${img}" class="gallery-img">
                            <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center gap-2">
                                <a href="/image/${img}" download class="p-2 bg-white rounded-full text-black hover:scale-110 transition"><i data-lucide="download" width="16"></i></a>
                                <a href="/image/${img}" target="_blank" class="p-2 bg-white rounded-full text-black hover:scale-110 transition"><i data-lucide="eye" width="16"></i></a>
                            </div>
                        </div>
                    `).join('');
                    lucide.createIcons();
                }
            } catch (e) { console.error(e); }
        }
        
        // Initial load
        refreshGallery();
        checkAuth();
    </script>
</body>
</html>
'''

# --- ROTAS FLASK ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/save_settings', methods=['POST'])
def save_settings():
    data = request.json
    key = data.get('key')
    
    # Ler .env atual
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    
    # Atualizar ou adicionar chave
    key_found = False
    new_lines = []
    for line in lines:
        if line.startswith('GEMINI_API_KEY='):
            new_lines.append(f'GEMINI_API_KEY={key}\n')
            key_found = True
        else:
            new_lines.append(line)
            
    if not key_found:
        new_lines.append(f'\nGEMINI_API_KEY={key}\n')
        
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
        
    # Atualizar variavel de ambiente em tempo real
    os.environ['GEMINI_API_KEY'] = key
    
    return jsonify({"success": True})

@app.route('/check_auth')
def check_auth():
    # Verificar se temos chave válida carregada
    key = os.environ.get('GEMINI_API_KEY')
    has_key = key and "Cole_Sua" not in key and len(key) > 10
    return jsonify({"connected": has_key})

@app.route('/generate_carousel', methods=['POST'])
def generate_carousel_endpoint():
    data = request.json
    topic = data.get('topic')
    
    # Executar em thread separada para não travar
    def run_job():
        # Importar aqui para evitar circular imports
        from main_carousel import generate_carousel_script, generate_carousel_images
        
        try:
            # 1. Gerar Roteiro
            script_data = generate_carousel_script(topic)
            
            # 2. Gerar Imagens
            folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(OUTPUT_DIR, folder_name)
            generate_carousel_images(script_data, output_dir=output_path)
            
        except Exception as e:
            print(f"Erro no background: {e}")

    thread = threading.Thread(target=run_job)
    thread.start()
    
    return jsonify({"success": True, "message": "Job iniciado! Verifique a galeria em instantes."})

@app.route('/list_images')
def list_images():
    # Listar todas as imagens jpg recursivamente em output/carousel
    images = []
    if os.path.exists(OUTPUT_DIR):
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for file in files:
                if file.endswith('.jpg'):
                    # Caminho relativo para servir
                    rel_dir = os.path.relpath(root, OUTPUT_DIR)
                    if rel_dir == ".": rel_dir = ""
                    images.append(os.path.join(rel_dir, file).replace("\", "/"))
    
    # Ordenar por mais recente (mtime) seria ideal, mas vamos inverter a lista simples
    return jsonify({"images": images[::-1]})

@app.route('/image/<path:filename>')
def serve_image(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename))

if __name__ == '__main__':
    print("\n" + "="*60)
    print("CAROUSEL KING - BENTO EDITION")
    print("="*60)
    print(f"\n[+] Acesse: http://localhost:5000")
    
    import webbrowser
    try:
        webbrowser.open("http://localhost:5000")
    except:
        pass
    
    app.run(host='0.0.0.0', port=5000, debug=False)
