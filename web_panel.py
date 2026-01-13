"""
Carousel Factory v6.0 - Firebase Edition
Fabrica de Carrosseis Virais com IA + Autenticacao Firebase
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory, send_file, redirect, url_for
import os
import sys
import io
import zipfile
import firebase_admin
from firebase_admin import credentials, auth
from datetime import datetime
from dotenv import load_dotenv

# Carregar variaveis de ambiente
load_dotenv()

# Configurar Imports
sys.path.insert(0, os.path.dirname(__file__))
from gemini_integration import generate_carousel_content, get_temas_para_nicho, TEMAS_POR_NICHO
from carousel_generator import generate_carousel
from logger import get_logger

logger = get_logger()
app = Flask(__name__)

# --- CONFIGURACAO FIREBASE ADMIN ---
# Para rodar local ou deploy, precisa das credenciais.
# Se nao tiver credenciais, o app roda mas a auth de backend falha (modo inseguro opcional para testes)
try:
    cred = credentials.Certificate("firebase-adminsdk.json") if os.path.exists("firebase-adminsdk.json") else None
    if cred:
        firebase_admin.initialize_app(cred)
    else:
        # Tenta inicializar sem credenciais explicitas (para Google Cloud/Render)
        firebase_admin.initialize_app()
    FIREBASE_ENABLED = True
except Exception as e:
    logger.warning(f"Firebase Admin nÃ£o inicializado: {e}. O backend nao validara tokens.")
    FIREBASE_ENABLED = False

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
CAROUSEL_DIR = os.path.join(OUTPUT_DIR, "carousels")
os.makedirs(CAROUSEL_DIR, exist_ok=True)

# --- HTML TEMPLATE COM FIREBASE AUTH ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carousel Factory v6 | Business Level</title>
    <!-- Firebase JS SDK -->
    <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-auth-compat.js"></script>
    <!-- UI Config -->
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root { --accent: #F59E0B; --bg: #050505; --card: #111; }
        body { background: var(--bg); color: #fff; font-family: 'Inter', sans-serif; }
        h1, h2, h3, .font-display { font-family: 'Space Grotesk', sans-serif; }
        .glass { background: rgba(255,255,255,0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
        .bento-card { background: var(--card); border-radius: 20px; border: 1px solid #222; transition: 0.3s; }
        .bento-card:hover { border-color: var(--accent); box-shadow: 0 0 20px rgba(245,158,11,0.1); }
        .auth-container { max-width: 400px; margin: 100px auto; text-align: center; }
        .hidden { display: none !important; }
    </style>
</head>
<body class="min-h-screen flex flex-col">

    <!-- LOGIN SCREEN -->
    <div id="login-screen" class="auth-container">
        <h1 class="text-4xl font-bold mb-2 font-display">CAROUSEL<span class="text-yellow-500">FACTORY</span></h1>
        <p class="text-gray-500 mb-8">Unauthorized Access Prohibited</p>
        
        <div class="bento-card p-8">
            <input type="email" id="email" placeholder="Email" class="w-full glass p-3 rounded mb-3 text-white">
            <input type="password" id="password" placeholder="Senha" class="w-full glass p-3 rounded mb-4 text-white">
            <button onclick="login()" class="w-full bg-yellow-500 text-black font-bold p-3 rounded hover:bg-yellow-400 transition">
                ENTRAR NO SISTEMA
            </button>
            <p id="login-error" class="text-red-500 mt-4 text-sm"></p>
        </div>
        
        <div class="mt-8 text-xs text-gray-600">
            <p>Configuracao necessaria no firebaseConfig</p>
        </div>
    </div>

    <!-- MAIN APP (Protected) -->
    <div id="app-screen" class="hidden container mx-auto p-6">
        <header class="flex justify-between items-center mb-10">
            <div>
                <h1 class="text-2xl font-bold font-display">CAROUSEL<span class="text-yellow-500">FACTORY</span></h1>
                <div class="flex items-center gap-2 mt-1">
                    <span class="w-2 h-2 rounded-full bg-green-500"></span>
                    <span class="text-xs text-gray-400 uppercase tracking-widest">System Online</span>
                </div>
            </div>
            <div class="flex items-center gap-4">
                <span id="user-email" class="text-sm text-gray-400"></span>
                <button onclick="logout()" class="text-xs border border-red-900 text-red-500 px-3 py-1 rounded hover:bg-red-900/20">SAIR</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
            
            <!-- CREATE PANEL -->
            <div class="md:col-span-4 bento-card p-6 h-fit">
                <h2 class="text-xl font-bold mb-6 font-display flex items-center gap-2">
                    <span class="text-yellow-500">⚡</span> GERADOR I.A.
                </h2>
                
                <div class="space-y-4">
                    <div>
                        <label class="text-xs uppercase text-gray-500 block mb-2">Nicho de Atuacao</label>
                        <select id="nicho" class="w-full glass p-3 rounded text-white bg-transparent">
                            {% for nicho in nichos %}
                            <option value="{{ nicho }}" class="bg-black">{{ nicho|title }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div>
                        <label class="text-xs uppercase text-gray-500 block mb-2">Tema (Opcional)</label>
                        <input type="text" id="topic" placeholder="Deixe vazio para auto-gerar..." class="w-full glass p-3 rounded text-white">
                    </div>
                    
                    <button onclick="generate()" id="btn-gen" class="w-full bg-gradient-to-r from-yellow-600 to-yellow-500 text-black font-bold p-4 rounded-xl hover:scale-[1.02] transition-transform">
                        GERAR CARROSSEL VIRAL
                    </button>
                </div>
                
                <div id="status-box" class="hidden mt-6 p-4 rounded bg-white/5 border border-white/10">
                    <div class="flex items-center gap-3">
                        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-500"></div>
                        <span id="status-msg" class="text-sm text-gray-300">Processando...</span>
                    </div>
                </div>
            </div>

            <!-- GALLERY -->
            <div class="md:col-span-8">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-xl font-bold font-display">GALERIA RECENTE</h2>
                    <button onclick="loadGallery()" class="text-yellow-500 text-sm hover:underline">Atualizar</button>
                </div>
                
                <div id="gallery-grid" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <!-- Cards inseridos via JS -->
                </div>
            </div>
        </div>
    </div>

    <script>
        // CONFIGURACAO FIREBASE - PREENCHA COM SEUS DADOS
        const firebaseConfig = {
            apiKey: "{{ firebase_config.apiKey }}",
            authDomain: "{{ firebase_config.projectId }}.firebaseapp.com",
            projectId: "{{ firebase_config.projectId }}",
            storageBucket: "{{ firebase_config.projectId }}.appspot.com",
            messagingSenderId: "SENDER_ID",
            appId: "APP_ID"
        };

        // Initialize Firebase
        if (firebaseConfig.apiKey) {
            firebase.initializeApp(firebaseConfig);
        } else {
            console.error("Firebase Config ausente");
        }

        // Auth State Listener
        firebase.auth().onAuthStateChanged((user) => {
            if (user) {
                document.getElementById('login-screen').classList.add('hidden');
                document.getElementById('app-screen').classList.remove('hidden');
                document.getElementById('user-email').innerText = user.email;
                loadGallery();
            } else {
                document.getElementById('login-screen').classList.remove('hidden');
                document.getElementById('app-screen').classList.add('hidden');
            }
        });

        async function login() {
            const email = document.getElementById('email').value;
            const pass = document.getElementById('password').value;
            try {
                await firebase.auth().signInWithEmailAndPassword(email, pass);
            } catch (error) {
                document.getElementById('login-error').innerText = error.message;
            }
        }

        function logout() {
            firebase.auth().signOut();
        }

        async function generate() {
            const user = firebase.auth().currentUser;
            if (!user) return;

            const nicho = document.getElementById('nicho').value;
            const topic = document.getElementById('topic').value;
            
            const btn = document.getElementById('btn-gen');
            const statusBox = document.getElementById('status-box');
            btn.disabled = true;
            statusBox.classList.remove('hidden');
            
            try {
                const token = await user.getIdToken();
                
                const res = await fetch('/generate_carousel', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + token
                    },
                    body: JSON.stringify({ nicho, topic, count: 5 })
                });
                
                const data = await res.json();
                if (data.success) {
                    document.getElementById('status-msg').innerText = "Sucesso! Atualizando galeria...";
                    setTimeout(loadGallery, 1500);
                } else {
                    document.getElementById('status-msg').innerText = "Erro: " + data.message;
                    document.getElementById('status-msg').classList.add('text-red-500');
                }
            } catch (e) {
                console.error(e);
            } finally {
                btn.disabled = false;
            }
        }

        async function loadGallery() {
            const user = firebase.auth().currentUser;
            if (!user) return;
            
            const token = await user.getIdToken();
            const res = await fetch('/list_carousels', {
                headers: { 'Authorization': 'Bearer ' + token }
            });
            const data = await res.json();
            
            const grid = document.getElementById('gallery-grid');
            grid.innerHTML = '';
            
            data.carousels.forEach(c => {
                const cover = `/carousel/${c.folder}/${c.files[0]}`;
                const div = document.createElement('div');
                div.className = 'bento-card overflow-hidden group relative';
                div.innerHTML = `
                    <div class="h-48 overflow-hidden">
                        <img src="${cover}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                    </div>
                    <div class="p-4">
                        <h3 class="font-bold text-sm text-gray-300 truncate">${c.folder}</h3>
                        <div class="flex justify-between items-center mt-3">
                            <span class="text-xs text-gray-500">${c.files.length} slides</span>
                            <a href="/download_carousel/${c.folder}" class="text-xs bg-white text-black px-3 py-1 rounded font-bold hover:bg-yellow-500 transition">BAIXAR ZIP</a>
                        </div>
                    </div>
                `;
                grid.appendChild(div);
            });
        }
    </script>
</body>
</html>
'''

# --- MIDDLEWARE AUTH ---
def verify_firebase_token():
    if not FIREBASE_ENABLED:
        return True # Ignora auth se firebase nao estiver configurado (DEV ONLY)
        
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        request.user = decoded_token
        return True
    except Exception as e:
        logger.error(f"Erro Token: {e}")
        return False

# --- ROUTES ---

@app.route('/')
def index():
    # Passar config do backend para o frontend
    fb_config = {
        "apiKey": os.getenv("FIREBASE_API_KEY", ""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", "")
    }
    return render_template_string(HTML_TEMPLATE, nichos=list(TEMAS_POR_NICHO.keys()), firebase_config=fb_config)

@app.route('/generate_carousel', methods=['POST'])
def handle_generate():
    if not verify_firebase_token() and FIREBASE_ENABLED:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    data = request.json
    topic = data.get('topic', '')
    nicho = data.get('nicho', 'mentalidade')
    count = int(data.get('count', 5))
    
    try:
        # Se nao tiver tema, pega um automatico do nicho
        if not topic:
            temas = get_temas_para_nicho(nicho, 1)
            topic = temas[0] if temas else "Disciplina e Foco"
        
        logger.info(f"[GERAR] Nicho={nicho}, Tema={topic}")
        
        # Gera o conteudo (copys)
        slides = generate_carousel_content(topic, nicho, count)
        
        if not slides:
            return jsonify({"success": False, "message": "Falha ao gerar conteudo."})
        
        # Nome do carrossel
        name = f"{nicho}_{topic[:15]}_{datetime.now().strftime('%H%M')}".replace(' ', '_')
        
        # Gera as imagens
        paths = generate_carousel(slides, "caverna", name)
        
        return jsonify({"success": True, "folder": name, "slides": len(paths)})
    except Exception as e:
        logger.error(f"[ERRO] {e}")
        return jsonify({"success": False, "message": str(e)})

@app.route('/list_carousels')
def list_carousels():
    if not verify_firebase_token() and FIREBASE_ENABLED:
       # Se falhar auth, retornamos vazio ou erro. 
       # Para facilitar testes locais sem token, se FIREBASE_ENABLED for False, passamos.
       if FIREBASE_ENABLED:
           return jsonify({"carousels": []}), 401

    carousels = []
    if os.path.exists(CAROUSEL_DIR):
        for folder in sorted(os.listdir(CAROUSEL_DIR), reverse=True):
            folder_path = os.path.join(CAROUSEL_DIR, folder)
            if os.path.isdir(folder_path):
                files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')])
                if files:
                    carousels.append({"folder": folder, "files": files})
    return jsonify({"carousels": carousels})

@app.route('/carousel/<folder>/<filename>')
def serve_image(folder, filename):
    return send_from_directory(os.path.join(CAROUSEL_DIR, folder), filename)

@app.route('/download_carousel/<folder>')
def download_carousel(folder):
    folder_path = os.path.join(CAROUSEL_DIR, folder)
    if not os.path.exists(folder_path):
        return "Not Found", 404
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(os.listdir(folder_path)):
            if file.endswith('.png'):
                file_path = os.path.join(folder_path, file)
                zf.write(file_path, file)
    
    memory_file.seek(0)
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=f'{folder}.zip')

if __name__ == '__main__':
    print("="*60)
    print(" CAROUSEL FACTORY v6.0 - FIREBASE EDITION")
    print("="*60)
    app.run(host='0.0.0.0', port=5000)
