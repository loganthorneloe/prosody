"""Tests for the hotkey module."""

import unittest
import time
from unittest.mock import Mock, patch
from src.prosody.hotkey import HotkeyListener
from pynput import keyboard


class TestHotkeyListener(unittest.TestCase):
    """Test cases for HotkeyListener class."""

    def setUp(self):
        """Set up test fixtures."""
        self.callback_called = False
        self.callback_count = 0

        def test_callback():
            self.callback_called = True
            self.callback_count += 1

        self.test_callback = test_callback

    def test_initialization(self):
        """Test HotkeyListener initialization."""
        listener = HotkeyListener(self.test_callback)
        self.assertFalse(listener.is_recording)
        self.assertEqual(listener.last_press_time, 0)
        self.assertIsNone(listener.listener)

    def test_double_press_detection(self):
        """Test double press detection logic."""
        listener = HotkeyListener(self.test_callback)

        # Simulate first press
        current_time = time.time()
        with patch("time.time", return_value=current_time):
            listener._on_press(keyboard.Key.ctrl_l)

        # Verify callback not called on first press
        self.assertFalse(self.callback_called)
        self.assertGreater(listener.last_press_time, 0)

        # Simulate second press within interval
        with patch("time.time", return_value=current_time + 0.2):
            listener._on_press(keyboard.Key.ctrl_l)

        # Verify callback called on double press
        self.assertTrue(self.callback_called)
        self.assertEqual(self.callback_count, 1)
        self.assertTrue(listener.is_recording)

    def test_double_press_timeout(self):
        """Test that double press doesn't trigger if too slow."""
        listener = HotkeyListener(self.test_callback)

        # Simulate first press
        current_time = time.time()
        with patch("time.time", return_value=current_time):
            listener._on_press(keyboard.Key.ctrl_l)

        # Simulate second press after timeout
        with patch("time.time", return_value=current_time + 0.5):
            listener._on_press(keyboard.Key.ctrl_l)

        # Verify callback not called
        self.assertFalse(self.callback_called)

    def test_other_keys_ignored(self):
        """Test that other keys are ignored."""
        listener = HotkeyListener(self.test_callback)

        # Press other keys
        listener._on_press(keyboard.Key.space)
        listener._on_press(keyboard.Key.enter)
        listener._on_press(keyboard.Key.ctrl_r)

        # Verify callback not called
        self.assertFalse(self.callback_called)

    def test_toggle_recording_state(self):
        """Test that recording state toggles on each double press."""
        listener = HotkeyListener(self.test_callback)

        # First double press - start recording
        current_time = time.time()
        with patch("time.time", return_value=current_time):
            listener._on_press(keyboard.Key.ctrl_l)
        with patch("time.time", return_value=current_time + 0.1):
            listener._on_press(keyboard.Key.ctrl_l)

        self.assertTrue(listener.is_recording)
        self.assertEqual(self.callback_count, 1)

        # Second double press - stop recording
        current_time = time.time() + 1
        with patch("time.time", return_value=current_time):
            listener._on_press(keyboard.Key.ctrl_l)
        with patch("time.time", return_value=current_time + 0.1):
            listener._on_press(keyboard.Key.ctrl_l)

        self.assertFalse(listener.is_recording)
        self.assertEqual(self.callback_count, 2)

    @patch("pynput.keyboard.Listener")
    def test_start_stop(self, mock_listener_class):
        """Test starting and stopping the listener."""
        mock_listener_instance = Mock()
        mock_listener_class.return_value = mock_listener_instance

        listener = HotkeyListener(self.test_callback)

        # Test start
        listener.start()
        mock_listener_class.assert_called_once()
        mock_listener_instance.start.assert_called_once()

        # Test stop
        listener.stop()
        mock_listener_instance.stop.assert_called_once()
        self.assertIsNone(listener.listener)

    @patch("pynput.keyboard.Listener")
    def test_context_manager(self, mock_listener_class):
        """Test using HotkeyListener as a context manager."""
        mock_listener_instance = Mock()
        mock_listener_class.return_value = mock_listener_instance

        with HotkeyListener(self.test_callback) as listener:
            # Verify listener started
            mock_listener_instance.start.assert_called_once()

        # Verify listener stopped after context exit
        mock_listener_instance.stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
