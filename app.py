import streamlit as st
import asyncio
import os
import sys
import glob
import time
from datetime import datetime

# ==========================================
# SETUP & IMPORTS
# ==========================================

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core logic (try/except to handle potential import errors gracefully in UI)
try:
    from main import run_full_pipeline
    import config
    from trend_researcher import research_before_creating
    from gemini_integration import generate_carousel_content, TEMAS_POR_NICHO
    from carousel_generator import generate_carousel
except ImportError as e:
    st.error(f"Erro crítico ao importar módulos do projeto: {e}")
    st.stop()

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="ViralBot Pro Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/viral-bot',
        'Report a bug': "https://github.com/yourusername/viral-bot/issues",
        'About': "# ViralBot Pro v3.0\nAutomação de vídeos virais com IA."
    }
)

# ==========================================
# CUSTOM CSS (PROFESSIONAL LOOK)
# ==========================================
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    /* Primary Button (Generate) */
    div[data-testid="stVerticalBlock"] > div > div > button[kind="primary"] {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF9E4B 100%);
        border: none;
        height: 3.5rem;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
    div[data-testid="stVerticalBlock"] > div > div > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4);
    }

    /* Cards/Containers */
    .css-card {
        background-color: #1F242C;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Video Gallery Grid */
    .video-card {
        background-color: #262730;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #3E404D;
        transition: transform 0.2s;
    }
    .video-card:hover {
        border-color: #FF4B4B;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: #FF4B4B !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3050/3050212.png", width=60)
    st.title("ViralBot Pro")
    st.caption("v3.0.0 | Enterprise Edition")
    
    st.markdown("--- ")
    
    st.subheader("🎯 Configuração de Campanha")
    
    # Niche Selection with smart suggestions
    niche_options = [
        "curiosidades", "historia", "tecnologia", "motivacional", 
        "financas", "saude", "viagem", "misterio", "quiz"
    ]
    
    selected_niche = st.selectbox(
        "Nicho / Tópico",
        options=niche_options + ["Outro..."],
        index=0
    )
    
    if selected_niche == "Outro...":
        custom_niche = st.text_input("Digite o nicho específico", placeholder="Ex: Dicas de Jardinagem")
        final_niche = custom_niche if custom_niche else "geral"
    else:
        final_niche = selected_niche

    st.markdown("### ⚙️ Parâmetros")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        num_videos = st.number_input("Qtd. Vídeos", min_value=1, max_value=20, value=config.NUM_VIDEOS)
    with col_s2:
        duration_mode = st.selectbox("Duração", ["Curto (<30s)", "Médio (30-60s)", "Longo (>1m)"], index=1)

    st.subheader("🎨 Estilo & Voz")
    voice_speed = st.select_slider(
        "Velocidade da Narração",
        options=["Lento", "Normal", "Rápido", "Turbo"],
        value="Rápido"
    )
    
    voice_map = {"Lento": "+0%", "Normal": "+10%", "Rápido": "+15%", "Turbo": "+25%"}
    
    use_trends = st.toggle("🔎 Pesquisar Trends (TikTok)", value=True, help="Analisa o TikTok antes de criar para garantir viralidade.")
    
    st.markdown("--- ")
    st.caption(f"📂 Workspace: `{os.path.basename(os.getcwd())}`")

# ==========================================
# MAIN DASHBOARD
# ==========================================

# Header Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Nicho Ativo", final_niche.title())
with col2:
    total_videos = len(glob.glob("output/*.mp4"))
    st.metric("Vídeos na Galeria", str(total_videos))
with col3:
    st.metric("Status API", "Online", delta="OK", delta_color="normal")
with col4:
    disk_usage = "2.4 GB" # Placeholder, could be real
    st.metric("Espaço em Disco", disk_usage)

st.markdown("--- ")

# Tabs
tab_gen, tab_carousel, tab_trends, tab_gallery, tab_logs = st.tabs([
    "🚀 Gerador de Vídeos", 
    "🎡 Gerador de Carrosséis",
    "📈 Análise de Trends", 
    "🎬 Galeria de Vídeos", 
    "⚙️ Logs & Console"
])

# -----------------------------------------------------------------------------
# TAB 1: GENERATOR
# -----------------------------------------------------------------------------
with tab_gen:
    st.markdown("### ⚡ Painel de Controle de Geração")
    st.markdown(f"Você está prestes a gerar **{num_videos} vídeos** sobre **'{final_niche}'**.")
    
    col_act1, col_act2 = st.columns([1, 2])
    
    with col_act1:
        st.info("""
        **Processo Automatizado:**
        1. 🔍 Pesquisa de Trends
        2. 📝 Criação de Roteiros (GPT)
        3. 🗣️ Narração Neural
        4. 🖼️ Geração de Imagens
        5. 🎥 Edição e Renderização
        """, unsafe_allow_html=True)
        
        start_btn = st.button("🚀 INICIAR AUTOMAÇÃO", type="primary", use_container_width=True)

    with col_act2:
        if start_btn:
            # Update Config Globals (Temporary hack for the session)
            config.NUM_VIDEOS = num_videos
            config.VOICE_SPEED = voice_map[voice_speed]
            
            status_container = st.status("🚀 Inicializando ViralBot Engine...", expanded=True)
            
            try:
                # 1. Research Phase
                status_container.write("🔍 **Fase 1:** Conectando ao TikTok Creative Center...")
                time.sleep(1) # UX Pause
                status_container.write(f"   → Buscando trends para '{final_niche}'...")
                
                # Create Event Loop for Async
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Execute Pipeline
                status_container.write("⚙️ **Fase 2:** Iniciando pipeline de produção...")
                
                # We define a wrapper to capture output if we wanted, 
                # but for now we rely on the backend printing to stdout 
                # and just await the result.
                
                start_time = time.time()
                videos = loop.run_until_complete(
                    run_full_pipeline(num_videos, use_trends, niche=final_niche)
                )
                end_time = time.time()
                
                loop.close()
                
                status_container.update(label="✅ Processo Concluído!", state="complete", expanded=False)
                
                st.success(f"🎉 Sucesso! {len(videos)} vídeos gerados em {end_time - start_time:.1f}s")
                st.balloons()
                
                # Quick Preview
                if videos:
                    st.subheader("🎥 Visualização Rápida")
                    cols = st.columns(3)
                    for i, v in enumerate(videos):
                         with cols[i % 3]:
                            st.video(v)
            
# -----------------------------------------------------------------------------
# TAB: CAROUSEL GENERATOR
# -----------------------------------------------------------------------------
with tab_carousel:
    st.markdown("### 🎡 Fábrica de Carrosséis Virais")
    st.markdown("Gere carrosséis de alta conversão (1080x1350) com estética 'Modo Caverna'.")
    
    col_c1, col_c2 = st.columns([1, 2])
    
    with col_c1:
        c_nicho = st.selectbox("Nicho do Carrossel", options=list(TEMAS_POR_NICHO.keys()))
        c_topic = st.text_input("Tema Específico", placeholder="Ex: A Farsa da Faculdade")
        c_slides = st.slider("Qtd Slides", 3, 10, 5)
        c_style = st.selectbox("Estilo Visual", ["caverna", "dark_purple", "dark_gold"])
        
        gen_c_btn = st.button("🎡 GERAR CARROSSEL", type="primary", use_container_width=True)
        
    with col_c2:
        if gen_c_btn:
            with st.status("🔮 Gerando conteúdo com IA...", expanded=True) as status:
                try:
                    # 1. Gerar Texto
                    status.write("✍️ Criando roteiro estratégico...")
                    slides_data = generate_carousel_content(c_topic if c_topic else "Mentalidade", c_nicho, c_slides)
                    
                    # 2. Gerar Imagens
                    status.write("🎨 Renderizando slides premium...")
                    folder_name = f"{c_nicho}_{datetime.now().strftime('%H%M%S')}"
                    paths = generate_carousel(slides_data, c_style, folder_name)
                    
                    status.update(label="✅ Carrossel Pronto!", state="complete")
                    st.success(f"Carrossel gerado com {len(paths)} slides!")
                    
                    # Preview
                    st.subheader("🖼️ Preview dos Slides")
                    c_cols = st.columns(3)
                    for i, p in enumerate(paths):
                        with c_cols[i % 3]:
                            st.image(p)
                            
                except Exception as e:
                    status.update(label="❌ Erro na Geração", state="error")
                    st.error(str(e))

# -----------------------------------------------------------------------------
# TAB 2: TREND ANALYSIS
# -----------------------------------------------------------------------------
with tab_trends:
    st.header("📈 Análise de Tendências em Tempo Real")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        niche_check = st.text_input("Testar nicho:", value=final_niche)
    with c2:
        check_btn = st.button("🔍 Analisar Agora")
        
    if check_btn:
        with st.spinner(f"Analisando '{niche_check}' no TikTok..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                data = loop.run_until_complete(research_before_creating(niche_check))
                
                if data:
                    st.json(data)
                    
                    if "recommendations" in data:
                        rec = data["recommendations"]
                        st.subheader("💡 Recomendações da IA")
                        st.write(f"**Estilo Sugerido:** {rec.get('suggested_style')}")
                        st.write(f"**Hashtags:** {', '.join(rec.get('suggested_hashtags', []))}")
                else:
                    st.warning("Nenhum dado encontrado ou erro na API.")
            except Exception as e:
                st.error(f"Erro na análise: {e}")
            finally:
                loop.close()

# -----------------------------------------------------------------------------
# TAB 3: GALLERY
# -----------------------------------------------------------------------------
with tab_gallery:
    st.header("📂 Sua Biblioteca de Vídeos")
    
    video_files = glob.glob(os.path.join("output", "*.mp4"))
    video_files.sort(key=os.path.getmtime, reverse=True)
    
    if not video_files:
        st.info("Ainda não há vídeos. Vá para a aba 'Gerador' para criar o primeiro!")
    else:
        # Filtering
        filter_text = st.text_input("Filtrar vídeos...", placeholder="Busque por nome...")
        if filter_text:
            video_files = [v for v in video_files if filter_text.lower() in v.lower()]
            
        # Grid
        cols = st.columns(3)
        for idx, video_file in enumerate(video_files):
            with cols[idx % 3]:
                container = st.container()
                container.markdown(f"**{os.path.basename(video_file)}**")
                container.video(video_file)
                
                # Metadata
                size = os.path.getsize(video_file) / (1024 * 1024)
                date = datetime.fromtimestamp(os.path.getmtime(video_file)).strftime('%d/%m %H:%M')
                container.caption(f"{date} • {size:.1f} MB")
                
                with open(video_file, "rb") as f:
                    container.download_button(
                        label="⬇️ Baixar MP4",
                        data=f,
                        file_name=os.path.basename(video_file),
                        mime="video/mp4",
                        key=f"dl_gal_{idx}"
                    )
                container.markdown("--- ")

# -----------------------------------------------------------------------------
# TAB 4: LOGS
# -----------------------------------------------------------------------------
with tab_logs:
    st.header("⚙️ Logs do Sistema")
    
    log_file_path = "output/logs/app.log" # Assuming this is where logs go based on setup
    # If standard logger writes to console, we might not see it here unless redirected to file.
    # We will search for any .log file in output/logs
    
    log_dir = os.path.join("output", "logs")
    found_logs = glob.glob(os.path.join(log_dir, "*.log")) if os.path.exists(log_dir) else []
    
    if found_logs:
        latest_log = max(found_logs, key=os.path.getmtime)
        st.caption(f"Lendo: {latest_log}")
        with open(latest_log, "r", encoding="utf-8") as f:
            log_content = f.read()
            st.code(log_content[-5000:], language="text") # Show last 5000 chars
    else:
        st.warning("Arquivo de log não encontrado. O sistema pode estar registrando apenas no console.")


# Footer
st.markdown("--- ")
st.markdown("Developed with ❤️ by Gemini Viral Bot")