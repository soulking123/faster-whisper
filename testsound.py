import pyaudio
import webrtcvad
import collections
import sys

# Constants for the audio stream
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # VAD operates at 8000, 16000, or 32000 Hz
CHUNK_DURATION_MS = 30  # Duration of an audio chunk in milliseconds
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)

# VAD settings
VAD_MODE = 1  # VAD aggressiveness (0-3). 3 is most aggressive.
SPEECH_WINDOW = 5  # Number of consecutive speech chunks to confirm talking

# Initialize PyAudio and VAD
audio = pyaudio.PyAudio()
vad = webrtcvad.Vad(VAD_MODE)

# Open audio stream
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

print("Listening for speech...")

speech_frames = collections.deque(maxlen=SPEECH_WINDOW)
is_talking = False

try:
    while True:
        # Read a chunk of audio data
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)

        # Pass the chunk to the VAD
        is_speech = vad.is_speech(data, RATE)

        # Update the speech buffer
        speech_frames.append(is_speech)

        # Check for talking condition
        if sum(speech_frames) >= SPEECH_WINDOW and not is_talking:
            print("yes")
            is_talking = True
        elif sum(speech_frames) == 0 and is_talking:
            is_talking = False

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    audio.terminate()