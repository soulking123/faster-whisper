import pyaudio									# handle audio in and out
import numpy as np
import math
import time
import wave										# handle wave file (list of feedback sound are in a .wav format
import re										# handle the regular expression 
import RPi.GPIO as GPIO							# handle IO
from faster_whisper import WhisperModel			# import speech to text model
import board
import neopixel

RELAY1 = 23
RELAY2 = 24
RELAY3 = 25
RELAY = [RELAY1, RELAY2, RELAY3]

soundList = {
				0: ["/home/admin/faster-whisper/voice/0.wav", "Roger is online, ready to assist"],
				1: ["/home/admin/faster-whisper/voice/1.wav", "Keyword detected, waiting for command"],
				2: ["/home/admin/faster-whisper/voice/2.wav", "Command unclear, please repeat the command"],
				3: ["/home/admin/faster-whisper/voice/3.wav", "Turning on the television"],
				4: ["/home/admin/faster-whisper/voice/4.wav", "Turning off the television"],
				5: ["/home/admin/faster-whisper/voice/5.wav", "Turning on the fan"],
				6: ["/home/admin/faster-whisper/voice/6.wav", "Turning off the fan"],
				7: ["/home/admin/faster-whisper/voice/7.wav", "Turning on the light"],
				8: ["/home/admin/faster-whisper/voice/8.wav", "Turning off the light"]
			}
			

PIXEL_COUNT = 16  								# The number of LEDs in your ring
LED_PIN = board.D18 							# GPIO 18 (Data line)
BRIGHTNESS = 0.3    							# Set brightness (0.0 to 1.0)
ORDER = neopixel.GRB 							# WS2812 generally uses GRB order
pixels = neopixel.NeoPixel(LED_PIN, PIXEL_COUNT, brightness=BRIGHTNESS, auto_write=False, pixel_order = ORDER)

model_size = "base.en"
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
isAccessed = False

# --- PyAudio Setup ---
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

def handleIO(RELAY):
	GPIO.setmode(GPIO.BCM)
	# Set all relay to the output mode and set it to HIGH (relay off)
	for i in RELAY:
		GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, GPIO.HIGH)
		
def deviceSpeak(soundFile):
	CHUNK = 1024 
	try:
		wf = wave.open(soundFile[0], 'rb')
		q = pyaudio.PyAudio()

		# Configure the stream using properties from the WAV file
		stream2 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
						channels=wf.getnchannels(),
						rate=wf.getframerate(),
						output=True,)

		# Stream the audio data in chunks
		print(soundFile[1])
		data = wf.readframes(CHUNK)
		while data:
			stream2.write(data)
			data = wf.readframes(CHUNK)
		

		# Cleanup
		stream2.stop_stream()
		stream2.close()
		q.terminate()

	except FileNotFoundError:
		print(f"Error: WAV file not found at {soundList[0][0]}")
	except Exception as e:
		print(f"An error occurred: {e}")

def deviceLED(color, interval):
	global PIXEL_COUNT, pixels
	
	for i in range(PIXEL_COUNT):
		pixels[i] = color
		pixels.show()
		time.sleep(interval)

def listening():
    global is_talking, SILENCE_TIMEOUT_CHUNKS, silent_frames_count, frames, isAccessed

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
            #print(rms)
            if(rms > 160000):
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
                      stream.stop_stream()
                      deviceLED((0, 0, 255), 0.05) 
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
                          text = segment.text.lower()
                          processedText = re.sub(r"[,. ]", "", text)
                          print(f"processed text = {processedText}")
                          if isAccessed:
                              print(processedText)
                              if "turnonthetelevision" in processedText:
                                  GPIO.output(23, GPIO.LOW)
                                  deviceSpeak(soundList[3])
                              elif "turnoffthetelevision" in processedText:
                                  GPIO.output(23, GPIO.HIGH)
                                  deviceSpeak(soundList[4])
                              elif "turnonthefan" in processedText:
                                  GPIO.output(24, GPIO.LOW)
                                  deviceSpeak(soundList[5])
                              elif "turnoffthefan" in processedText:
                                  GPIO.output(24, GPIO.HIGH)
                                  deviceSpeak(soundList[6])
                              elif "turnonthelight" in processedText:
                                  GPIO.output(25, GPIO.LOW)
                                  deviceSpeak(soundList[7])
                              elif "turnofthelight" in processedText:
                                  GPIO.output(25, GPIO.HIGH)
                                  deviceSpeak(soundList[8])
                              else:
                                  deviceSpeak(soundList[2])
                              isAccessed = False
                          elif "helloroger" in processedText:
                              deviceSpeak(soundList[1])
                              isAccessed = True
                          else:
                              print(segment.text)
                              print("Fail Keyword")
                      time.sleep(2)
                      deviceLED((0, 255, 0), 0.05)
                      stream.start_stream()
    except IOError:
        # Handle cases where the audio buffer overflows
        pass

pixels.fill((0, 0, 0))
time.sleep(3)
frames = []

handleIO(RELAY)

deviceLED((0, 255, 0), 0.05) 
stream.stop_stream()
deviceSpeak(soundList[0])
stream.start_stream()

try:
    while True:
        listening()
except KeyboardInterrupt:
    pass

