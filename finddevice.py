import pyaudio

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    device_info = p.get_device_info_by_host_api_device_index(0, i)
    print(f"Index {i}: {device_info.get('name')}")

p.terminate()
# Look for the index number corresponding to your Bluetooth speaker.
