
import os
import sys
from video_engine import create_video_from_images_and_audio
from moviepy.editor import ColorClip, AudioFileClip, CompositeAudioClip
import numpy as np

# Mock audio creation
def create_mock_audio(filename, duration=3):
    from moviepy.audio.AudioClip import AudioArrayClip
    # Create a simple sine wave tone
    rate = 44100
    t = np.linspace(0, duration, rate * duration)
    data = np.sin(2 * np.pi * 440 * t) # 440Hz sine wave
    # Stereo
    data = np.array([data, data]).T
    audio = AudioArrayClip(data, fps=rate)
    audio.write_audiofile(filename, fps=rate)

# Mock image creation
def create_mock_image(filename, color=(255, 0, 0), size=(1920, 1080)):
    from PIL import Image
    img = Image.new('RGB', size, color)
    img.save(filename)

def test_rendering():
    print("Testing video rendering...")
    
    os.makedirs("test_output", exist_ok=True)
    
    audio_path = "test_output/test_audio.mp3"
    create_mock_audio(audio_path)
    
    image_paths = []
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    for i, color in enumerate(colors):
        path = f"test_output/img_{i}.png"
        create_mock_image(path, color)
        image_paths.append(path)
        
    output_path = "test_output/test_video.mp4"
    
    try:
        create_video_from_images_and_audio(
            images=image_paths,
            audio_path=audio_path,
            output_path=output_path,
            add_music=False # Skip looking for assets/music
        )
        print(f"✅ Video created successfully at {output_path}")
        return True
    except Exception as e:
        print(f"❌ Video creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rendering()
    if not success:
        sys.exit(1)
