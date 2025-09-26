import pyaudio
import webrtcvad
import collections
import sys
import wave
import io
import numpy as np
from faster_whisper import WhisperModel

# --- VAD & PyAudio Configuration ---
FORMAT = pyaudio.paInt16  # PyAudio format for 16-bit signed integers
CHANNELS = 1
RATE = 16000  # VAD and Whisper models work best with a 16kHz sample rate
CHUNK_DURATION_MS = 30  # Duration of an audio chunk in milliseconds
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)

# VAD settings
VAD_MODE = 0  # VAD aggressiveness (0-3), 3 is most aggressive
SPEECH_WINDOW = 50  # Number of consecutive speech chunks to confirm talking

# --- Faster-Whisper Model Configuration ---
model_size = "tiny.en"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

# --- Initialize PyAudio and VAD ---
audio = pyaudio.PyAudio()
vad = webrtcvad.Vad(VAD_MODE)

# --- Open Audio Stream and Buffers ---
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

print("Listening for speech...")

speech_frames = collections.deque(maxlen=SPEECH_WINDOW)
audio_buffer = []
is_talking = False

try:
    while True:
        # Read a chunk of audio data
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)

        # Pass the chunk to the VAD and store it in the audio buffer
        is_speech = vad.is_speech(data, RATE)
        speech_frames.append(is_speech)
        audio_buffer.append(data)

        # Check for talking condition and trigger transcription
        if sum(speech_frames) >= SPEECH_WINDOW and not is_talking:
            print("Speech detected. Transcribing...")
            is_talking = True
        elif sum(speech_frames) == 0 and is_talking:
            is_talking = False
            
            if audio_buffer:
                # Concatenate all audio chunks into a single byte string
                full_audio_data = b''.join(audio_buffer)

                # Convert the raw bytes to a NumPy array for the model
                audio_np = np.frombuffer(full_audio_data, dtype=np.int16).flatten().astype(np.float32) / 32768.0

                # Transcribe the audio
                segments, info = model.transcribe(audio_np, beam_size=5)

                # Print the transcription
                print("Transcription results:")
                print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
                for segment in segments:
                    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
                
                # Clear the buffer for the next speech segment
                audio_buffer = []

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    audio.terminate()