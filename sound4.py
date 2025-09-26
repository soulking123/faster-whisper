import pyaudio
import wave

CHUNK = 1024 
WAV_FILE = './voice/000.wav'

try:
    wf = wave.open(WAV_FILE, 'rb')
    p = pyaudio.PyAudio()

    # Configure the stream using properties from the WAV file
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=2)

    # Stream the audio data in chunks
    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

    # Cleanup
    stream.stop_stream()
    stream.close()
    p.terminate()

except FileNotFoundError:
    print(f"Error: WAV file not found at {WAV_FILE}")
except Exception as e:
    print(f"An error occurred: {e}")
