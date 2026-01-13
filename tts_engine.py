"""
TTS Engine - Gerador de Narração com Edge TTS
100% Gratuito usando Microsoft Edge TTS
"""

import edge_tts
import asyncio
import os
import config
from logger import get_logger

logger = get_logger()

# Vozes disponíveis em português
VOICES = {
    "feminina": "pt-BR-FranciscaNeural",
    "masculina": "pt-BR-AntonioNeural"
}

async def generate_audio(text: str, output_path: str, voice: str = "masculina", rate: str = config.VOICE_SPEED) -> str:
    """
    Gera áudio a partir de texto usando Edge TTS.
    
    Args:
        text: Texto para converter em áudio
        output_path: Caminho do arquivo de saída
        voice: "feminina" ou "masculina"
        rate: Velocidade da fala (ex: "+10%", "-5%")
    
    Returns:
        Caminho do arquivo de áudio gerado
    """
    voice_id = VOICES.get(voice, VOICES["masculina"])
    
    logger.info(f"🔊 Gerando narração com voz {voice} ({voice_id}) [Speed: {rate}]...")
    
    try:
        communicate = edge_tts.Communicate(text, voice_id, rate=rate)
        await communicate.save(output_path)
        logger.info(f"✅ Áudio salvo: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"❌ Erro ao gerar áudio: {e}")
        raise

async def generate_all_audios(videos: list, output_dir: str) -> dict:
    """
    Gera áudios para todos os vídeos.
    
    Returns:
        Dict com {video_id: audio_path}
    """
    from content import get_full_script
    
    audio_paths = {}
    
    for video in videos:
        video_id = video["id"]
        script = get_full_script(video)
        output_path = os.path.join(output_dir, f"audio_video_{video_id}.mp3")
        
        await generate_audio(script, output_path)
        audio_paths[video_id] = output_path
    
    return audio_paths

# Teste standalone
if __name__ == "__main__":
    async def test():
        test_text = "Olá! Este é um teste do gerador de voz."
        await generate_audio(test_text, "test_audio.mp3")
    
    asyncio.run(test())