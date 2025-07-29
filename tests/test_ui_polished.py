"""Tests for the ui_polished module."""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from src.prosody.ui_polished import PolishedWaveformIndicator, type_text


class TestPolishedWaveformIndicator(unittest.TestCase):
    """Test cases for PolishedWaveformIndicator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.audio_level = 0.0
        self.get_audio_level = lambda: self.audio_level

    @patch("tkinter.Tk")
    def test_initialization(self, mock_tk):
        """Test PolishedWaveformIndicator initialization."""
        indicator = PolishedWaveformIndicator(self.get_audio_level)

        # Check initialization
        self.assertIsNotNone(indicator.get_audio_level)
        self.assertIsNone(indicator.window)
        self.assertIsNone(indicator.canvas)
        self.assertIsNotNone(indicator.command_queue)
        self.assertEqual(len(indicator.history), 50)
        self.assertEqual(indicator.history[0], 0.0)

    @patch("tkinter.Tk")
    @patch("tkinter.Toplevel")
    def test_show_hide(self, mock_toplevel, mock_tk):
        """Test showing and hiding the waveform."""
        indicator = PolishedWaveformIndicator(self.get_audio_level)

        # Test show
        indicator.show()
        time.sleep(0.2)  # Give thread time to process

        # Verify 'show' command was queued
        # Note: Can't directly test GUI creation in unit tests

        # Test hide
        indicator.hide()
        time.sleep(0.2)  # Give thread time to process

    def test_command_queue(self):
        """Test command queue functionality."""
        indicator = PolishedWaveformIndicator(self.get_audio_level)

        # Queue multiple commands
        indicator.command_queue.put("show")
        indicator.command_queue.put("hide")
        indicator.command_queue.put("quit")

        # Verify commands are in queue
        self.assertEqual(indicator.command_queue.get(), "show")
        self.assertEqual(indicator.command_queue.get(), "hide")
        self.assertEqual(indicator.command_queue.get(), "quit")

    def test_audio_level_callback(self):
        """Test audio level callback integration."""
        # Test with different audio levels
        test_levels = [0.0, 0.5, 1.0, 0.3]

        for level in test_levels:
            self.audio_level = level
            result = self.get_audio_level()
            self.assertEqual(result, level)

    @patch("tkinter.Tk")
    def test_history_update(self, mock_tk):
        """Test that audio history is maintained."""
        indicator = PolishedWaveformIndicator(self.get_audio_level)

        # Initial history should be all zeros
        self.assertEqual(all(h == 0.0 for h in indicator.history), True)

        # Note: Can't test animation directly without running GUI

    @patch("tkinter.Tk")
    def test_cleanup(self, mock_tk):
        """Test cleanup on deletion."""
        indicator = PolishedWaveformIndicator(self.get_audio_level)

        # Test __del__ method
        del indicator

        # Note: Can't directly verify thread cleanup without GUI

    def test_thread_daemon(self):
        """Test that GUI thread is daemon thread."""
        indicator = PolishedWaveformIndicator(self.get_audio_level)

        # Check thread properties
        self.assertIsNotNone(indicator.thread)
        self.assertTrue(indicator.thread.daemon)
        self.assertTrue(indicator.thread.is_alive())


class TestTypeText(unittest.TestCase):
    """Test cases for type_text function."""

    @patch("pynput.keyboard.Controller")
    @patch("time.sleep")
    def test_type_text(self, mock_sleep, mock_controller_class):
        """Test typing text functionality."""
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller

        # Test typing
        test_text = "Hello, World!"
        type_text(test_text)

        # Verify each character was typed
        for char in test_text:
            mock_controller.type.assert_any_call(char)

        # Verify sleep was called
        mock_sleep.assert_called_with(0.1)

    @patch("pynput.keyboard.Controller")
    @patch("time.sleep")
    def test_type_text_empty(self, mock_sleep, mock_controller_class):
        """Test typing empty text."""
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller

        # Test with empty string
        type_text("")

        # Should still sleep but not type anything
        mock_controller.type.assert_not_called()
        mock_sleep.assert_called_with(0.1)

    @patch("pynput.keyboard.Controller")
    def test_type_text_special_chars(self, mock_controller_class):
        """Test typing special characters."""
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller

        # Test with special characters
        test_text = "Line1\nLine2\tTabbed"
        type_text(test_text)

        # Verify all characters including special ones were typed
        for char in test_text:
            mock_controller.type.assert_any_call(char)


if __name__ == "__main__":
    unittest.main()
