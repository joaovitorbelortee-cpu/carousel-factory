# Diretiva: Gerar Vídeo Viral

## Objetivo
Gerar um vídeo curto (30-60s) otimizado para viralização no TikTok/Instagram.

## Inputs
- `nicho` (string): Tema do vídeo (ex: "Curiosidades da Roma Antiga")
- `quantidade` (int): Número de vídeos a gerar (1-10)
- `usar_trends` (bool): Se deve pesquisar tendências antes

## Ferramentas (execution/)
1. `trend_researcher.py` - Busca tendências reais
2. `content_modeler.py` - Gera roteiros modelados
3. `tts_engine.py` - Gera narração com Edge TTS
4. `image_generator.py` - Cria imagens para o vídeo
5. `video_engine.py` - Monta o vídeo final com Ken Burns

## Fluxo
1. Pesquisar tendências do nicho (se `usar_trends=True`)
2. Gerar roteiro baseado nas tendências
3. Criar narração de áudio
4. Gerar imagens para cada seção
5. Montar vídeo com transições e música
6. Salvar em `output/`

## Edge Cases
- Se tendências falharem, usar hooks genéricos
- Se imagem falhar, usar cor de fundo
- Se FFmpeg não estiver no PATH, usar imageio-ffmpeg

## Outputs
- Arquivo MP4 em `output/{nicho_slug}_{id}_final.mp4`
- Áudio MP3 em `output/audio_{nicho_slug}_{id}.mp3`
