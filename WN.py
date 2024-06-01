import numpy as np
from scipy.io.wavfile import write
import sounddevice as sd
from scipy.signal import butter, lfilter

# Parameters
sample_rate = 44100  # Sample rate in Hz
RATE = 44100
frequency = 240  # Frequency in Hz
duration = 15  # Duration in seconds
amplitude = 4000  # Amplitude level






# Generate time values
t = np.linspace(0, duration, int(sample_rate * duration), False)

# Generate sine wave


noise = np.random.normal(scale=0.000001, size=t.shape) * 100000000

sine_wave = noise
sine_wave = sine_wave.astype(np.int16)
_lenwindow = 0.0002 # Frequency of the noise
window = np.hanning(len(sine_wave)*_lenwindow)
sine_wave = np.convolve(sine_wave, window, mode='same')
sine = amplitude * np.sin(2 * np.pi * frequency * t)
sine_wave = sine_wave + sine
sine_wave = np.where(np.isnan(sine_wave), 0, sine_wave)
sine_wave = np.nan_to_num(sine_wave)
sine_wave = sine_wave.astype(np.int16)

# Convert to 16-bit PCM WAV format

# Save the WAV file
sd.play(sine_wave, samplerate=sample_rate)
sd.wait()
