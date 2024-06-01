import numpy as np
import sounddevice as sd

# Generate Brownian noise
duration = 5  # Duration in seconds
rng = np.random.default_rng()
dt = 0.0001 # Time step
T = 500  # Total time
num_steps = int(T/dt)
brownian_noise = rng.standard_normal(num_steps)

# Rescale and integrate to get smoother Brownian motion
scaled_brownian_motion = np.cumsum(brownian_noise) / np.sqrt(dt)

# Scale the Brownian motion to fit your application
scaling_factor = 0.5  # Adjust this value based on your requirements
scaled_brownian_motion *= scaling_factor

# Convert to audio waveform
sample_rate = 44100  # Sample rate in Hz
duration = len(scaled_brownian_motion) / sample_rate  # Calculate duration based on sample rate
audio_waveform = scaled_brownian_motion *0.05  # Scale to 16-bit range
audio_waveform = audio_waveform.astype(np.float32)


# Desired starting frequency in Hz
start_frequency = 440  # Example: Middle C

# Calculate phase offset
phase_offset = 2 * np.pi * start_frequency / sample_rate

# Shift the waveform to start around the specified frequency
shifted_waveform = np.cos(phase_offset) * audio_waveform + np.sin(phase_offset) * audio_waveform




# Play the audio waveform
with sd.OutputStream(samplerate=sample_rate, channels=1) as stream:
    stream.write(audio_waveform)
    sd.sleep(int(duration * 1000))  # Wait for the duration of the audio