import pyaudio
import numpy as np
import math
import time
import wave
from faster_whisper import WhisperModel

model_size = "tiny.en"
model = WhisperModel(model_size, device="cpu", compute_type="int8")


# --- Audio Stream Configuration ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024 # A smaller chunk size for better time resolution
is_talking = False
SILENCE_TIMEOUT_CHUNKS = 20
silent_frames_count = 0
WAVE_OUTPUT_FILENAME = "output.wav"

# --- PyAudio Setup ---
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

time.sleep(5)
print('Start')
frames = []

def listening():
    global is_talking, SILENCE_TIMEOUT_CHUNKS, silent_frames_count, frames

    """Function to update the plot with new audio data."""
    try:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # --- Perform FFT ---
        # Only perform FFT if data is present
        if audio_data.size > 0:
            fft_data = np.fft.fft(audio_data)
            # Take the magnitude and get the first half of the data
            y_data = np.abs(fft_data)[:CHUNK//2]

            rms = np.sqrt(np.mean(np.square(y_data)))

            # if(db_value > -10):
            #     xnum +=1
            #     print(xnum)
            # print(rms)
            if(rms > 15000):
                if not is_talking:
                    print("--- VOICE START ---")
                    is_talking = True
                print("voice")
                frames.append(data)
            else:
                if is_talking:
                  silent_frames_count += 1
                  frames.append(data)
                  if silent_frames_count >= SILENCE_TIMEOUT_CHUNKS:
                      print("--- VOICE END ---")
                      is_talking = False
                      silent_frames_count = 0

                      waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
                      waveFile.setnchannels(CHANNELS)
                      waveFile.setsampwidth(p.get_sample_size(FORMAT))
                      waveFile.setframerate(RATE)
                      waveFile.writeframes(b''.join(frames))
                      waveFile.close()

                      frames = []

                      segments, info = model.transcribe("output.wav", beam_size=5)
                      for segment in segments:
                        if "hello" in segment.text.lower():
                            print("Keyword detected!, Waiting for command...")
                        else:
                            print(segment.text)
                            print("fail keyword")
    except IOError:
        # Handle cases where the audio buffer overflows
        pass


try:
    while True:
        listening()
except KeyboardInterrupt:
    pass
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(p.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    print(f"Audio saved to {WAVE_OUTPUT_FILENAME}")