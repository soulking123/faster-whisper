import simpleaudio as sa
from pydub import AudioSegment
import time
import io

# --- Configuration ---
audio_file = './voice/00.wav'
SILENCE_MS = 3000  # 0.5 seconds of silence (adjust this value if needed)

def play_padded_audio(file_path):
    try:
        # 1. Load the audio file using Pydub
        print(f"Loading and padding: {file_path}")
        audio = AudioSegment.from_wav(file_path)
        
        # 2. Create SILENCE (0.5 seconds of silence)
        silence = AudioSegment.silent(duration=SILENCE_MS)
        
        # 3. Prepend the silence to the original audio
        padded_audio = silence + audio

        # 4. Get the raw audio data from the padded file
        raw_data = padded_audio.raw_data

        # 5. Create a WaveObject from the padded raw data
        wave_obj = sa.WaveObject(
            audio_data=raw_data,
            num_channels=padded_audio.channels,
            bytes_per_sample=padded_audio.sample_width,
            sample_rate=padded_audio.frame_rate
        )

        # 6. Play the padded object
        play_obj = wave_obj.play()
        print("Playing padded audio...")
        
        # CRITICAL: Wait for the sound to finish playing
        play_obj.wait_done()
        
    except FileNotFoundError:
        print(f"Error: Audio file not found at {file_path}")
    except Exception as e:
        # This will catch missing FFmpeg if the file was MP3, 
        # or other Pydub/simpleaudio errors.
        print(f"An error occurred during playback. Check Pydub/FFmpeg: {e}")

# --- Example Usage ---
print("Attempting to play padded audio...")
play_padded_audio(audio_file)
print("Playback finished and script complete.")
