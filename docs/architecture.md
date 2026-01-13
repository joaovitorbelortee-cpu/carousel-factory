# Viral Bot - Arquitetura Técnica

## Diagrama de Fluxo

```mermaid
flowchart TD
    A[Usuário] --> B[Web Panel / CLI]
    B --> C{Orquestrador main.py}
    C --> D[trend_researcher.py]
    D --> E[Tendências]
    C --> F[content_modeler.py]
    E --> F
    F --> G[Roteiro]
    C --> H[tts_engine.py]
    G --> H
    H --> I[Áudio MP3]
    C --> J[image_generator.py]
    G --> J
    J --> K[Imagens PNG]
    C --> L[video_engine.py]
    I --> L
    K --> L
    L --> M[Vídeo MP4]
    M --> N[output/]
```

## Camadas (AGENTS.md)

| Camada | Responsabilidade | Arquivos |
|--------|-----------------|----------|
| **L1: Directives** | SOPs, instruções | `directives/*.md` |
| **L2: Orchestration** | Decisões, fluxo | `src/main.py`, `src/web_panel.py` |
| **L3: Execution** | Trabalho determinístico | `execution/*.py` |

## Módulos

| Módulo | Função |
|--------|--------|
| `trend_researcher.py` | Busca tendências |
| `content_modeler.py` | Gera roteiros |
| `tts_engine.py` | Gera áudio |
| `image_generator.py` | Gera imagens |
| `video_engine.py` | Monta vídeo |
| `web_panel.py` | Interface web |
