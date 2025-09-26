import pyaudio
import numpy as np

# --- Audio Stream Configuration ---
FORMAT = pyaudio.paInt16 
CHANNELS = 1
RATE = 44100  # Sample rate
CHUNK = 1024  # Size of audio buffer

# --- Loudness Threshold ---
# This value may need to be adjusted based on your microphone's sensitivity
# and your environment's noise level.
LOUDNESS_THRESHOLD = 100

# --- Initialize PyAudio ---
p = pyaudio.PyAudio()

# --- Open Audio Stream ---
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Listening for loud sounds...")

try:
    while True:
        # Read a chunk of audio data
        data = stream.read(CHUNK, exception_on_overflow=False)
        
        # Convert the audio data to a numpy array
        # The 'dtype' should match the 'FORMAT' from PyAudio (paInt16 corresponds to np.int16)
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Calculate the Root Mean Square (RMS)
        # We use a small epsilon value to prevent division by zero in some cases
        rms = np.sqrt(np.mean(np.square(audio_data)))
        
        # Check if the RMS value exceeds the threshold
        if rms > LOUDNESS_THRESHOLD:
            print(f"Loud sound detected! RMS: {rms:.2f}")
        else:
            print(f"{rms:.2f}")

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    # --- Clean up ---
    stream.stop_stream()
    stream.close()
    p.terminate()