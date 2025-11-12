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
import paho.mqtt.client as mqtt
import serial 

PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200

TIMEOUT = 1000

BROKER_ADRESS = "broker.emqx.io"
TOPIC = "polibatam/homeassistant/#"


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
				8: ["/home/admin/faster-whisper/voice/8.wav", "Turning off the light"],
				9: ["/home/admin/faster-whisper/voice/9.wav", "Turn on the air conditioner and set it to normal"],
				10: ["/home/admin/faster-whisper/voice/10.wav", "Turn on the air conditioner and set it to cool"],
				11: ["/home/admin/faster-whisper/voice/11.wav", "Turn on the air conditioner and set it to freezing"],
				12: ["/home/admin/faster-whisper/voice/12.wav", "Turn off the air conditioner"],
                                13: ["/home/admin/faster-whisper/voice/13.wav", "Switch to the previous channel"],
                                14: ["/home/admin/faster-whisper/voice/14.wav", "Switch to the next channel"]
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

def on_connect(client, userdata, flags, rc):
    print(f"Connected wirh result code {rc}")
    client.subscribe(TOPIC)
    print(f"Subscribed to topic :{TOPIC}")

def on_message(cliend, userData, msg):
    payload_str = msg.payload.decode("utf-8")
    print(f"[{msg.topic}] Received message: {payload_str} ")
    if msg.topic == "polibatam/homeassistant/television":
        if payload_str == "true":
            GPIO.output(23, GPIO.LOW)
            time.sleep(25)
            ser.write("TV_SELECTCHANNEL".encode())
        else:
            GPIO.output(23, GPIO.HIGH)
    elif msg.topic == "polibatam/homeassistant/fan":
        if payload_str == "true":
            GPIO.output(24, GPIO.LOW)
        else:
            GPIO.output(24, GPIO.HIGH)
    elif msg.topic == "polibatam/homeassistant/light":
        if payload_str == "true":
            GPIO.output(25, GPIO.LOW)
        else:
            GPIO.output(25, GPIO.HIGH)
    elif msg.topic == "polibatam/homeassistant/airconditioner":
        if payload_str == "true":
            ser.write("AC_ON25".encode())
        else:
            ser.write("AC_OFF".encode())

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
        #ser.write("AC_ON25".encode())
        #print("acon")
        #time.sleep(2)
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
            if(rms > 40000):
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
                              isAccessed = False
                              if "turnonthetelevision" in processedText:
                                  #GPIO.output(23, GPIO.LOW)
                                  deviceSpeak(soundList[3])
                                  client.publish("polibatam/homeassistant/television","true")
                                  #deviceSpeak(soundList[3])
                                  #time.sleep(25)
                                  ser.write("TV_SELECTCHANNEL".encode())
                                  #deviceSpeak(soundList[3])
                              elif "turnoffthetelevision" in processedText:
                                  #GPIO.output(23, GPIO.HIGH)
                                  client.publish("polibatam/homeassistant/television","false")
                                  deviceSpeak(soundList[4])
                              elif "turnonthefan" in processedText:
                                  client.publish("polibatam/homeassistant/fan","true")
                                  #GPIO.output(24, GPIO.LOW)
                                  deviceSpeak(soundList[5])
                              elif "turnoffthefan" in processedText:
                                  client.publish("polibatam/homeassistant/fan","false")
                                  #GPIO.output(24, GPIO.HIGH)
                                  deviceSpeak(soundList[6])
                              elif "turnonthelight" in processedText:
                                  client.publish("polibatam/homeassistant/light","true")
                                  #GPIO.output(25, GPIO.LOW)
                                  deviceSpeak(soundList[7])
                              elif "turnoffthelight" in processedText:
                                  client.publish("polibatam/homeassistant/light","false")
                                  #GPIO.output(25, GPIO.HIGH)
                                  deviceSpeak(soundList[8])
                              elif "turnontheairconditioner" in processedText:
                                  message_to_send = "AC_ON25"
                                  ser.write(message_to_send.encode())
                                  deviceSpeak(soundList[9])
                              elif "airconditionercool" in processedText:
                                  message_to_send = "AC_ON20"
                                  ser.write(message_to_send.encode())
                                  deviceSpeak(soundList[10])
                              elif "airconditionerfreezing" in processedText:
                                  message_to_send = "AC_ON16"
                                  ser.write(message_to_send.encode())
                                  deviceSpeak(soundList[11])
                              elif "turnofftheairconditioner" in processedText:
                                  message_to_send = "AC_OFF"
                                  ser.write(message_to_send.encode())
                                  deviceSpeak(soundList[12])
                              elif "nextchannel" in processedText:
                                  ser.write("TV_NEXT".encode())
                                  deviceSpeak(soundList[14])
                              elif "previouschannel" in processedText:
                                  ser.write("TV_PREVIOUS".encode())
                                  deviceSpeak(soundList[13])
                              else:
                                  deviceSpeak(soundList[2])
                                  isAccessed = True
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
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_ADRESS, 1883, 68)
client.loop_start()

deviceLED((0, 255, 0), 0.05) 
stream.stop_stream()
deviceSpeak(soundList[0])
stream.start_stream()

try:
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUD_RATE,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=TIMEOUT
    )
    print(f"Connected to {PORT} at {BAUD_RATE} baud.")
    while True:
        listening()
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()

