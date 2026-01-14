"""
Carousel Factory v6.0 - Firebase Edition
Fabrica de Carrosseis Virais com IA + Autenticacao Firebase
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory, send_file, redirect, url_for, session
import os
import sys
import io
import zipfile
import threading
import json
from datetime import datetime
from dotenv import load_dotenv

# Configurar Pastas e Logger antes de tudo
sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger
logger = get_logger()

from gemini_integration import generate_carousel_content, get_temas_para_nicho, TEMAS_POR_NICHO
from carousel_generator import generate_carousel

try:
    import firebase_admin
    from firebase_admin import credentials, auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("firebase-admin não instalado. Funcionalidades Firebase desativadas.")

# Carregar variaveis de ambiente
load_dotenv()

app = Flask(__name__)

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"RUNTIME ERROR: {str(e)}", exc_info=True)
    return jsonify({
        "success": False, 
        "message": "Erro Interno no Servidor (Business Level Debug)",
        "error": str(e)
    }), 500

# --- CONFIGURACAO FIREBASE ADMIN ---
if FIREBASE_AVAILABLE:
    try:
        cred = credentials.Certificate("firebase-adminsdk.json") if os.path.exists("firebase-adminsdk.json") else None
        if cred:
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
        FIREBASE_ENABLED = True
    except Exception as e:
        logger.warning(f"Firebase Admin não inicializado: {e}. O backend nao validara tokens.")
        FIREBASE_ENABLED = False
else:
    FIREBASE_ENABLED = False
# Detectar ambiente serverless (Vercel)
IS_SERVERLESS = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

if IS_SERVERLESS:
    OUTPUT_DIR = "/tmp/output"
    CAROUSEL_DIR = "/tmp/output/carousels"
else:
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
    CAROUSEL_DIR = os.path.join(OUTPUT_DIR, "carousels")

try:
    os.makedirs(CAROUSEL_DIR, exist_ok=True)
except Exception as e:
    logger.warning(f"Não foi possível criar diretório de output: {e}")

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
            <button onclick="login()" class="w-full bg-yellow-500 text-black font-bold p-3 rounded hover:bg-yellow-400 transition mb-3">
                ENTRAR (FIREBASE)
            </button>
            <div class="relative flex py-2 items-center">
                <div class="flex-grow border-t border-gray-700"></div>
                <span class="flex-shrink-0 mx-4 text-gray-500 text-xs">OU</span>
                <div class="flex-grow border-t border-gray-700"></div>
            </div>
            <a href="/google_login" class="w-full bg-white text-black font-bold p-3 rounded hover:bg-gray-200 transition flex justify-center items-center gap-2">
                <svg class="w-4 h-4" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.11c-.22-.66-.35-1.36-.35-2.11s.13-1.45.35-2.11V7.05H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.95l3.66-2.84z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.05l3.66 2.84c.87-2.6 3.3-4.51 6.16-4.51z" fill="#EA4335"/></svg>
                ENTRAR COM GOOGLE
            </a>
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
            console.log("Firebase Auth nao configurado. Modo apenas Gemini OAuth disponivel se configurado.");
        }

        // Verificacao de OAuth do Backend (Injetado pelo Flask)
        const GOOGLE_LOGGED_IN = {{ 'true' if logged_in_google else 'false' }};

        // Auth State Listener
        firebase.auth().onAuthStateChanged((user) => {
            if (user) {
                showApp(user.email);
            } else if (GOOGLE_LOGGED_IN) {
                showApp("Google OAuth User");
            } else {
                showLogin();
            }
        });

        function showApp(email) {
            document.getElementById('login-screen').classList.add('hidden');
            document.getElementById('app-screen').classList.remove('hidden');
            document.getElementById('user-email').innerText = email;
            loadGallery();
        }

        function showLogin() {
            document.getElementById('login-screen').classList.remove('hidden');
            document.getElementById('app-screen').classList.add('hidden');
        }

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
    return render_template_string(HTML_TEMPLATE, 
                                nichos=list(TEMAS_POR_NICHO.keys()), 
                                firebase_config=fb_config,
                                logged_in_google=bool(get_google_credentials()))

# --- OAUTH CONFIG & ROUTES ---
# Permite HTTP apenas para testes locais. Em prod (Vercel), deve usar HTTPS.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' 

# Configurações OAuth (Pega do ENV ou usa placeholder para não quebrar na inicializacao)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI') # Ex: https://seu-app.vercel.app/oauth2callback

app.secret_key = os.getenv('SECRET_KEY', 'super_secret_key_change_me')

@app.route('/google_login')
def google_login():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return "Erro: GOOGLE_CLIENT_ID e SECRET não configurados no servidor."
        
    # Cria o fluxo OAuth
    # Escopos necessarios para o Gemini (Generative Language API)
    scopes = ["https://www.googleapis.com/auth/generative-language.retriever", "https://www.googleapis.com/auth/cloud-platform"]
    
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=scopes,
        redirect_uri=url_for('oauth2callback', _external=True) # Tenta gerar automatico
    )
    
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    if not state:
        return "Erro: Estado da sessao perdido. Tente novamente."
        
    try:
        from google_auth_oauthlib.flow import Flow
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=["https://www.googleapis.com/auth/generative-language.retriever", "https://www.googleapis.com/auth/cloud-platform"],
            state=state,
            redirect_uri=url_for('oauth2callback', _external=True)
        )
        
        # HTTPS obrigatorio no Vercel para callback
        authorization_response = request.url
        if request.headers.get('X-Forwarded-Proto') == 'https':
            authorization_response = authorization_response.replace('http:', 'https:')

        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        # Salva credenciais na sessao (simplificado - ideal seria banco)
        session['google_credentials'] = credentials_to_dict(credentials)
        
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Erro OAuth: {e}")
        return f"Erro na autenticação: {e}"

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_google_credentials():
    if 'google_credentials' in session:
        from google.oauth2.credentials import Credentials
        return Credentials(**session['google_credentials'])
    return None

@app.route('/generate_carousel', methods=['POST'])
def handle_generate():
    if not verify_firebase_token() and FIREBASE_ENABLED:
        return jsonify({"success": False, "message": "Unauthorized (Firebase)"}), 401
    
    # Tenta obter credenciais OAuth do usuario logado na sessao
    oauth_creds = get_google_credentials()
    
    data = request.json
    topic = data.get('topic', '')
    nicho = data.get('nicho', 'mentalidade')
    count = int(data.get('count', 5))
    
    try:
        if not topic:
            temas = get_temas_para_nicho(nicho, 1)
            topic = temas[0] if temas else "Disciplina e Foco"
        
        logger.info(f"[GERAR] Nicho={nicho}, Tema={topic}, Auth={ 'OAuth' if oauth_creds else 'API Key'}")

        # Detectar ambiente Vercel (Serverless) - Nao usar threads
        is_vercel = os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME')
        
        if is_vercel:
            # Sincrono
            slides = generate_carousel_content(topic, nicho, count, credentials=oauth_creds)
            if not slides: return jsonify({"success": False, "message": "Falha na geracao."})
            name = f"{nicho}_{topic[:15]}_{datetime.now().strftime('%H%M')}".replace(' ', '_')
            paths = generate_carousel(slides, "caverna", name)
            return jsonify({"success": True, "folder": name, "slides": len(paths)})
        else:
            # Assincrono (Local) - Nota: Threads nao tem acesso a session flask.
            # Localmente, melhor passar as credenciais/key explicitamente se for thread, 
            # mas simplificando: Localmente usa API KEY do env geralmente.
            # Se quiser OAuth local, precisaria passar o obj credentials pra thread.
            
            def run_job(creds_snapshot):
                try:
                    slides = generate_carousel_content(topic, nicho, count, credentials=creds_snapshot)
                    if slides:
                        name = f"{nicho}_{topic[:15]}_{datetime.now().strftime('%H%M')}".replace(' ', '_')
                        generate_carousel(slides, "caverna", name)
                except Exception as e:
                    print(f"Erro bg: {e}")

            thread = threading.Thread(target=run_job, args=(oauth_creds,))
            thread.start()
            return jsonify({"success": True, "message": "Job iniciado!"})

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
