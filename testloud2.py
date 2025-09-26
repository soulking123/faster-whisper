import pyaudio
import numpy as np

# --- Audio Stream Configuration ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

# --- Loudness Measurement Configuration ---
LOUDNESS_THRESHOLD = 500  # Adjust this value based on your environment
is_loud = False

# --- PyAudio Setup ---
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Listening for loud sounds...")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Calculate the Root Mean Square (RMS)
        # Check for empty data to prevent errors
        if audio_data.size > 0:
            rms = np.sqrt(np.mean(np.square(audio_data)))
        else:
            rms = 0
        
        # Check if the sound is loud
        if rms > LOUDNESS_THRESHOLD and not is_loud:
            print(f"Loud sound detected! RMS: {rms:.2f}")
            is_loud = True
        elif rms <= LOUDNESS_THRESHOLD and is_loud:
            print(f"Sound is now quiet. RMS: {rms:.2f}")
            is_loud = False

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    # --- Clean up ---
    stream.stop_stream()
    stream.close()
    p.terminate()