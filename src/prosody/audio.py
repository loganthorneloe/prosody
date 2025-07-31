"""Audio recording functionality for Prosody."""

import os
import sys
import threading
import queue
import numpy as np
import sounddevice as sd
from typing import Optional, Tuple

# Check if running in development mode
DEV_MODE = os.environ.get('PROSODY_DEV') == '1' or sys.argv[0].endswith('__main__.py')
# Suppress output in tests
if 'pytest' in sys.modules:
    DEV_MODE = False


def log(message: str, important: bool = False):
    """Log a message, respecting dev/production mode."""
    if DEV_MODE:
        print(message)


class AudioRecorder:
    """Handles audio recording from the default microphone."""

    def __init__(self, samplerate: int = 16000, channels: int = 1):
        """Initialize the audio recorder.

        Args:
            samplerate: Sample rate for recording (default 16000 Hz for Whisper)
            channels: Number of channels (default 1 for mono)
        """
        self.samplerate = samplerate
        self.channels = channels
        self.recording = False
        self.audio_queue = queue.Queue()
        self.stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()
        self.current_level = 0.0

    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream."""
        if status:
            log(f"Audio recording status: {status}", important=True)

        # Copy audio data to queue
        if self.recording:
            self.audio_queue.put(indata.copy())
            # Calculate current audio level (RMS)
            self.current_level = float(np.sqrt(np.mean(indata**2)))

    def start_recording(self) -> None:
        """Start recording audio from the default microphone."""
        with self._lock:
            if self.recording:
                return

            # Clean up any existing stream first
            if self.stream:
                try:
                    self.stream.stop()
                    self.stream.close()
                except:
                    pass
                self.stream = None

            # Clear any existing data in the queue
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break

            try:
                # Create and start the audio stream
                self.stream = sd.InputStream(
                    samplerate=self.samplerate,
                    channels=self.channels,
                    callback=self._audio_callback,
                    dtype=np.float32,
                )
                self.stream.start()
                self.recording = True
            except Exception as e:
                self.recording = False
                if self.stream:
                    try:
                        self.stream.close()
                    except:
                        pass
                    self.stream = None
                raise RuntimeError(f"Failed to start audio recording: {e}")

    def stop_recording(self) -> np.ndarray:
        """Stop recording and return the recorded audio data.

        Returns:
            NumPy array containing the recorded audio
        """
        with self._lock:
            if not self.recording:
                return np.array([], dtype=np.float32)

            self.recording = False
            self.current_level = 0.0

            # Stop and close the stream
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            # Collect all audio data from the queue
            audio_chunks = []
            while not self.audio_queue.empty():
                try:
                    audio_chunks.append(self.audio_queue.get_nowait())
                except queue.Empty:
                    break

            # Concatenate all audio chunks
            if audio_chunks:
                audio_data = np.concatenate(audio_chunks, axis=0)
                # Flatten to 1D array if mono
                if self.channels == 1:
                    audio_data = audio_data.flatten()
                return audio_data
            else:
                return np.array([], dtype=np.float32)

    def get_current_level(self) -> float:
        """Get the current audio level (0.0 to 1.0).

        Returns:
            Current audio level as a float between 0 and 1
        """
        return min(1.0, self.current_level * 10)  # Scale up and clamp to 0-1

    def get_available_devices(self) -> list:
        """Get list of available audio input devices.

        Returns:
            List of device information dictionaries
        """
        devices = sd.query_devices()
        input_devices = []

        for i, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                input_devices.append(
                    {
                        "index": i,
                        "name": device["name"],
                        "channels": device["max_input_channels"],
                    }
                )

        return input_devices

    def __del__(self):
        """Cleanup when the recorder is destroyed."""
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
        except:
            pass
