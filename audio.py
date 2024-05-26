import pyaudio
import numpy as np
import subprocess
import pulsectl
import time
from numba import jit
from scipy.signal import butter, lfilter

#RGB
import rgb
rgb.connect()

#Audio parameters
CHUNK = int(512.0*0.5)  # Number of data points to read at a time
FORMAT = pyaudio.paInt16
CHANNELS = 2

#Reactivity parameters
rate_of_change_down = 1.0/15 #Rate of change for the sigmoid function to fall
rate_of_change_up = 1.0/40 #Rate of change for the sigmoid function to climb

#Audio filtering parameters
frequency_low = 350 # Lower frequency range to pass
frequency_high = 1000 # Higher frequency range to pass

falloff = 8 # Order of the filter, each order adds 6dB per octave
sigmoid_falloff = 1 # Sigmoid falloff factor, higher values make the sigmoid function more linear      !DOES NOT WORK FOR NOW, NO IDEA WHY!
#   ^^ Fix me! ^^

#Communication parameters
_baud_rate = 9600 # For now does not affect communication, only sleep time

_tsleep = 1.0/(_baud_rate) * 250

#PulseAudio functions
# Function to create a combined sink with selected speakers
def create_combined_sink(speaker_sink_name):
    subprocess.run(["pactl", "load-module", "module-combine-sink", f"slaves={speaker_sink_name},loopback", "sink_name=combined_sink"])

# Function to terminate the combined sink
def terminate_combined_sink():
    subprocess.run(["pactl", "unload-module", "module-combine-sink"])

# Initialize PyAudio
p = pyaudio.PyAudio()
device_count = p.get_device_count()
for i in range(device_count):
    device_info = p.get_device_info_by_index(i)
    print(f"{i}: {device_info['name']}")

# List available devices and let the user select one
device_index = int(input("Select device index: "))
device_info = p.get_device_info_by_index(device_index)

RATE = int(device_info['defaultSampleRate'])

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                output=False,
                output_device_index=device_index)

print("Recording...")

data = b''

#Signal processing functions
def butter_bandpass(lowcut, highcut, RATE, order=5):
    nyq = 0.5 * RATE
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, order=5):
    b, a = butter_bandpass(lowcut, highcut, RATE, order)
    y = lfilter(b, a, data)
    return y




# List available sinks and let the user select one
with pulsectl.Pulse('select-speaker-sink') as pulse:
    sinks = pulse.sink_list()
    for i, sink in enumerate(sinks):
        print(f"{i + 1}. {sink.description}")

    speaker_sink_index = int(input("Select speaker sink: ")) - 1
    speaker_sink_name = sinks[speaker_sink_index].name

# Create the combined sink with the selected speaker sink
create_combined_sink(speaker_sink_name)

@jit(nopython=True, fastmath=True, cache=True)
def convert_to_8bit(audio_data):
    # Scale the 16-bit data to 8-bit
    return [(sample + 32768) // 2 for sample in audio_data]

#@jit
def calculate_average(audio_data):
    # Ensure audio_data is a list
    if isinstance(audio_data, np.ndarray):
        audio_data = audio_data.tolist()
    # Calculate the sum of all values
    total_sum = sum(audio_data)
    # Calculate the average using integer division
    average = total_sum // len(audio_data)
    return average

def apply_sigmoid_255_indev(audio_data):
    # Ensure audio_data is a NumPy array
    if not isinstance(audio_data, np.ndarray):
        audio_data = np.array(audio_data)
    if np.exp(audio_data) == 0:
        return 0
    # Apply true sigmoid function between 0 and 1
    data = 1 / (1 + (np.exp(-audio_data)/sigmoid_falloff))
    return data*255.0 - 127.5

def to_hex(value):
    # Convert the value to hexadecimal and format it to two digits
    return f"{value:02x}"

# Main loop to read audio data from the stream
_prev = 1.0
initial_value = 0.0
try:
    while True:
        data += stream.read(CHUNK)
        numpydata = np.frombuffer(data[-CHUNK:], dtype=np.int16)
        left_channel = numpydata[::2]  # Take every second element starting from index 0
        right_channel = numpydata[1::2]  # Take every second element starting from index 1

        #Audio filtering
        filtered_bass = butter_bandpass_filter(left_channel, frequency_low, frequency_high, order=falloff)

        #Code to display the audio data
        processed_data = convert_to_8bit(filtered_bass)
        average_data = calculate_average(processed_data) - 16384
        sigmoid_result = apply_sigmoid_255_indev(average_data)

        if initial_value < abs(sigmoid_result):
            new_value = initial_value - (initial_value - sigmoid_result) *rate_of_change_up
        else:
            new_value = initial_value - (initial_value - sigmoid_result) * rate_of_change_down

        initial_value = abs(new_value)
        hex_result = to_hex(abs(int(2*new_value)))
        #print(f"Average: {average_data}, Sigmoid: {sigmoid_result}, Hex: {hex_result}")

        rgb.requestColor(hex_result+hex_result+hex_result)
        #sleep for baud rate
        time.sleep(_tsleep)
except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()

# Terminate the combined sink after exiting the main loop
terminate_combined_sink()
