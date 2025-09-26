import simpleaudio as sa
from pydub import AudioSegment
import time

# --- Configuration ---
BLINK_AUDIO_FILE = './voice/blink.wav' 
MAIN_AUDIO_FILE = './voice/arcade.wav'

def play_concatenated_audio(blink_path, main_path):
    try:
        # 1. Load both audio segments using Pydub
        print(f"Loading {blink_path} and {main_path}...")
        blink_audio = AudioSegment.from_wav(blink_path)
        main_audio = AudioSegment.from_wav(main_path)
        
        # 2. Concatenate the blink sound followed by the main sound
        # The '+' operator handles concatenation in Pydub
        combined_audio = blink_audio + main_audio
        print("Audio concatenated successfully.")

        # 3. Extract the raw data from the combined audio object
        raw_data = combined_audio.raw_data

        # 4. Create a WaveObject from the raw data and properties
        wave_obj = sa.WaveObject(
            audio_data=raw_data,
            num_channels=combined_audio.channels,
            bytes_per_sample=combined_audio.sample_width,
            sample_rate=combined_audio.frame_rate
        )

        # 5. Play the combined object
        play_obj = wave_obj.play()
        print("Playing combined audio...")
        
        # CRITICAL: Wait for the sound to finish playing
        play_obj.wait_done()
        
    except FileNotFoundError:
        print("Error: One or both audio files not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Example Usage ---
print("Attempting to play concatenated audio...")
play_concatenated_audio(BLINK_AUDIO_FILE, MAIN_AUDIO_FILE)
print("Playback finished and script complete.")
