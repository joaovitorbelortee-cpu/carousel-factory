# Viral Bot - Project Brief

## Visão Geral
Sistema automatizado de geração de vídeos virais para TikTok e Instagram.

## Objetivos
1. Gerar vídeos curtos (30-60s) otimizados para viralização
2. Pesquisar tendências antes de criar conteúdo
3. Suportar qualquer nicho (Modo Geral)
4. Interface web para controle (http://localhost:5000)

## Arquitetura (3 Camadas)
- **Layer 1 (Directives)**: SOPs em `directives/`
- **Layer 2 (Orchestration)**: `src/main.py`, `src/web_panel.py`
- **Layer 3 (Execution)**: Scripts em `execution/`

## Funcionalidades v3.1
- [x] Campo de nicho customizado
- [x] Busca real de tendências
- [x] Geração de conteúdo do zero
- [x] Ken Burns + música
- [x] Interface web moderna

## Stack Tecnológico
- Python 3.13
- Flask (web panel)
- MoviePy (vídeo)
- Edge TTS (áudio)
- Pillow (imagens)
