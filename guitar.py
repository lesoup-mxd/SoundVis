import numpy as np
import sounddevice as sd
import scipy.signal
import scipy.io.wavfile as wav

# Function to generate Brownian noise
def brownian_noise(duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration))
    noise = np.cumsum(np.random.normal(size=len(t)))
    return noise

# Function to apply a simple low-pass filter
def low_pass_filter(signal, cutoff_freq, sample_rate):
    nyquist_freq = 0.5 * sample_rate
    normal_cutoff = cutoff_freq / nyquist_freq
    b, a = scipy.signal.butter(8, normal_cutoff, btype='low', analog=False)
    filtered_signal = scipy.signal.filtfilt(b, a, signal)
    return filtered_signal

# Function to stretch the waveform
def stretch_wave(waveform, original_duration, target_duration):
    num_samples = len(waveform)
    target_sample_rate = int(target_duration * sample_rate)
    stretched_waveform = np.interp(np.linspace(0, 1, target_sample_rate),
                                   np.linspace(0, 1, num_samples),
                                   waveform)
    return stretched_waveform

# Parameters
original_duration = 10  # Original duration in seconds
target_duration = 20  # Target duration after stretching
sample_rate = 44100  # Sample rate
cutoff_freq = 2000  # Cutoff frequency for the low-pass filter
amplitude = 0.001  # Amplitude of the noise

# Generate Brownian noise
noise = brownian_noise(original_duration, sample_rate)

# Apply low-pass filter
filtered_noise = low_pass_filter(noise, cutoff_freq, sample_rate)

# Stretch the waveform
stretched_noise = stretch_wave(filtered_noise, original_duration, target_duration)

# Normalize the signal
stretched_noise /= np.max(np.abs(stretched_noise)) * amplitude

# Convert to 16-bit PCM WAV format
audio_data = np.int16(stretched_noise * 32767)

# Save the audio file
wav.write('filtered_stretched_guitar_sound.wav', sample_rate, audio_data)
