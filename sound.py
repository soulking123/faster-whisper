import simpleaudio as sa
import time

# --- Configuration ---
# Replace 'my_prompt.wav' with the path to your audio file
audio_file = './voice/0.wav' 
time.sleep(15)
def play_audio(file_path):
    try:
        # Load the WAV file into a WaveObject
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        
        # Play the sound
        play_obj = wave_obj.play()
        
        print(f"Playing audio: {file_path}")
        
        # ? CRITICAL FIX: Wait for the sound to finish playing.
        # This prevents the script from ending and prematurely killing the audio.
        play_obj.wait_done() 
        
    except FileNotFoundError:
        print(f"Error: Audio file not found at {file_path}")
    except Exception as e:
        print(f"An error occurred during playback: {e}")

# --- Example Usage ---
print("Attempting to play audio...")
#play_audio(audio_file)
play_audio('/home/admin/faster-whisper/voice/0.wav')
time.sleep(1)
play_audio('/home/admin/faster-whisper/voice/1.wav')
play_audio('/home/admin/faster-whisper/voice/2.wav')
play_audio('/home/admin/faster-whisper/voice/3.wav')
play_audio('/home/admin/faster-whisper/voice/4.wav')
play_audio('/home/admin/faster-whisper/voice/5.wav')
play_audio('/home/admin/faster-whisper/voice/6.wav')
play_audio('/home/admin/faster-whisper/voice/7.wav')
play_audio('/home/admin/faster-whisper/voice/8.wav')
print("Playback finished and script complete.")

# You no longer need the 'time.sleep(1)' here since wait_done() handles the pause.
