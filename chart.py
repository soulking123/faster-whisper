import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import time

# --- Audio Stream Configuration ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024 # A smaller chunk size for better time resolution
RMS_REF = (2**15) - 1
xnum=1

# --- Plot Configuration ---
fig, ax = plt.subplots(figsize=(10, 5))
x_data = np.fft.fftfreq(CHUNK, d=1/RATE)[:CHUNK//2] # Frequencies for the x-axis
y_data = np.zeros(CHUNK//2) # Initial y-axis data (magnitudes)

line, = ax.plot(x_data, y_data, color='b')
ax.set_ylim(0, 200000) # Adjust this based on your microphone's loudness
ax.set_xlim(0, RATE/2) # Set x-axis limit to Nyquist frequency
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Magnitude")
ax.set_title("Real-Time Audio Spectrum")
ax.grid(True)

# --- PyAudio Setup ---
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

time.sleep(5)

def update_plot(frame):
    global xnum

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
            db_value = 20 * math.log10(rms / RMS_REF)
            # print(db_value)

            # if(db_value > -10):
            #     xnum +=1
            #     print(xnum)
            # print(rms)
            if(rms > 1000):
                xnum +=1
                print(xnum)
        
        # Update the plot line
        line.set_ydata(y_data)
        
    except IOError:
        # Handle cases where the audio buffer overflows
        pass

    return line,

# --- Run the Animation ---
ani = animation.FuncAnimation(fig, update_plot, interval=50, blit=True)

try:
    plt.show()
except KeyboardInterrupt:
    pass
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()