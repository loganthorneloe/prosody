"""Tests for the audio module."""

import unittest
import numpy as np
import time
from unittest.mock import Mock, patch, MagicMock
from src.prosody.audio import AudioRecorder


class TestAudioRecorder(unittest.TestCase):
    """Test cases for AudioRecorder class."""

    def setUp(self):
        """Set up test fixtures."""
        self.recorder = AudioRecorder()

    def test_initialization(self):
        """Test AudioRecorder initialization."""
        self.assertIsNone(
            self.recorder.stream
        )  # Stream not created until recording starts
        self.assertEqual(self.recorder.samplerate, 16000)
        self.assertEqual(self.recorder.channels, 1)
        self.assertIsNotNone(self.recorder.audio_queue)
        self.assertFalse(self.recorder.recording)
        self.assertEqual(self.recorder.current_level, 0.0)

    def test_audio_recorder_parameters(self):
        """Test AudioRecorder with different parameters."""
        recorder = AudioRecorder(samplerate=44100, channels=2)
        self.assertEqual(recorder.samplerate, 44100)
        self.assertEqual(recorder.channels, 2)

    @patch("sounddevice.InputStream")
    def test_audio_callback(self, mock_stream_class):
        """Test audio callback function."""
        # Mock the stream
        mock_stream = Mock()
        mock_stream_class.return_value = mock_stream
        
        # Create test audio data
        test_audio = np.random.randn(1024, 1).astype(np.float32) * 0.1

        # Start recording
        self.recorder.start_recording()

        # Call the callback
        self.recorder._audio_callback(test_audio, None, None, None)

        # Check that audio was queued
        self.assertFalse(self.recorder.audio_queue.empty())

        # Check that level was calculated
        expected_level = float(np.sqrt(np.mean(test_audio**2)))
        self.assertEqual(self.recorder.current_level, expected_level)

    @patch("sounddevice.InputStream")
    def test_start_stop_recording(self, mock_stream_class):
        """Test starting and stopping recording."""
        mock_stream = Mock()
        mock_stream_class.return_value = mock_stream

        # Start recording
        self.recorder.start_recording()
        self.assertTrue(self.recorder.recording)
        mock_stream.start.assert_called_once()

        # Stop recording
        audio_data = self.recorder.stop_recording()
        self.assertFalse(self.recorder.recording)
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()
        self.assertIsInstance(audio_data, np.ndarray)

    def test_stop_recording_with_data(self):
        """Test stopping recording with queued audio data."""
        # Add some test audio to queue
        test_chunks = [
            np.random.randn(1024, 1).astype(np.float32) * 0.1,
            np.random.randn(1024, 1).astype(np.float32) * 0.1,
            np.random.randn(1024, 1).astype(np.float32) * 0.1,
        ]

        self.recorder.recording = True
        for chunk in test_chunks:
            self.recorder.audio_queue.put(chunk)

        # Stop recording and get audio data
        with patch("sounddevice.InputStream"):
            audio_data = self.recorder.stop_recording()

        # Verify
        expected_length = sum(len(chunk) for chunk in test_chunks)
        self.assertEqual(len(audio_data), expected_length)
        self.assertTrue(self.recorder.audio_queue.empty())

    def test_get_current_level(self):
        """Test getting current audio level."""
        # Test with no audio
        level = self.recorder.get_current_level()
        self.assertEqual(level, 0.0)

        # Test with audio
        self.recorder.current_level = 0.05
        level = self.recorder.get_current_level()
        self.assertEqual(level, 0.5)  # Scaled by 10

        # Test clamping
        self.recorder.current_level = 0.2
        level = self.recorder.get_current_level()
        self.assertEqual(level, 1.0)  # Clamped to max

    def test_recording_while_not_recording(self):
        """Test that audio is not queued when not recording."""
        test_audio = np.random.randn(1024, 1).astype(np.float32)

        # Ensure not recording
        self.recorder.recording = False

        # Call callback
        self.recorder._audio_callback(test_audio, None, None, None)

        # Check that nothing was queued
        self.assertTrue(self.recorder.audio_queue.empty())

    @patch("sounddevice.query_devices")
    def test_get_available_devices(self, mock_query):
        """Test getting available audio devices."""
        mock_query.return_value = [
            {"name": "Device 1", "max_input_channels": 2},
            {"name": "Device 2", "max_input_channels": 0},
            {"name": "Device 3", "max_input_channels": 1},
        ]

        devices = self.recorder.get_available_devices()

        # Should only return devices with input channels
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0]["name"], "Device 1")
        self.assertEqual(devices[1]["name"], "Device 3")

    def test_cleanup(self):
        """Test cleanup on deletion."""
        # Create a recorder
        recorder = AudioRecorder()

        # Mock a stream object
        mock_stream = Mock()
        recorder.stream = mock_stream

        # Call __del__ explicitly (more reliable than del)
        recorder.__del__()

        # Verify stream was stopped and closed
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()

    def test_thread_safety(self):
        """Test that audio queue is thread-safe."""
        import threading

        def producer():
            for i in range(100):
                self.recorder.audio_queue.put(np.array([i]))

        def consumer():
            items = []
            while len(items) < 100:
                try:
                    item = self.recorder.audio_queue.get(timeout=0.1)
                    items.append(item[0])
                except:
                    pass
            return items

        # Start producer thread
        producer_thread = threading.Thread(target=producer)
        producer_thread.start()

        # Consume in main thread
        items = consumer()

        producer_thread.join()

        # Verify all items were received
        self.assertEqual(len(items), 100)
        self.assertEqual(sorted(items), list(range(100)))


if __name__ == "__main__":
    unittest.main()
