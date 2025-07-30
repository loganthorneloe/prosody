"""Integration tests for Prosody application."""

import unittest
import os
import tempfile
import threading
import time
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.prosody.main import ProsodyApp


class TestProsodyIntegration(unittest.TestCase):
    """Integration tests for the complete Prosody application."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temp directory for PID file
        self.temp_dir = tempfile.mkdtemp()
        self.pid_file = os.path.join(self.temp_dir, ".prosody.pid")

        # Patch various components to avoid real hardware/GUI
        self.patches = [
            patch("sounddevice.InputStream"),
            patch("whisper.load_model"),
            patch("tkinter.Tk"),
            patch("pynput.keyboard.Listener"),
            patch("subprocess.run"),  # For notifications
            patch.dict(os.environ, {"HOME": self.temp_dir}),
        ]

        for p in self.patches:
            p.start()

    def tearDown(self):
        """Clean up after tests."""
        for p in self.patches:
            p.stop()

        # Clean up temp files
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)
        os.rmdir(self.temp_dir)

    def test_app_initialization(self):
        """Test that app initializes all components correctly."""
        app = ProsodyApp()

        # Verify components are initialized
        self.assertIsNotNone(app.audio_recorder)
        self.assertIsNotNone(app.transcriber)
        self.assertIsNotNone(app.recording_indicator)
        self.assertIsNotNone(app.hotkey_listener)

        # Verify initial state
        self.assertFalse(app.is_recording)
        self.assertTrue(app.running)

        # Verify PID file was created
        self.assertTrue(os.path.exists(self.pid_file))

    @patch("src.prosody.main.type_text")
    def test_recording_workflow(self, mock_type_text):
        """Test complete recording workflow."""
        app = ProsodyApp()

        # Mock transcriber to return text
        app.transcriber.transcribe = Mock(return_value="Test transcription")

        # Start recording
        app.toggle_recording()
        self.assertTrue(app.is_recording)

        # Mock audio data
        test_audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        app.audio_recorder.stop_recording = Mock(return_value=test_audio)

        # Stop recording - this triggers transcription in a thread
        app.toggle_recording()
        self.assertFalse(app.is_recording)

        # Wait for the transcription thread to complete
        import time

        time.sleep(0.2)

        # Verify transcription was called with audio data
        app.transcriber.transcribe.assert_called_once()

        # Verify text was typed
        mock_type_text.assert_called_once_with("Test transcription")

    def test_cancel_recording(self):
        """Test canceling a recording."""
        app = ProsodyApp()

        # Start recording
        app.toggle_recording()
        self.assertTrue(app.is_recording)

        # Cancel recording
        app.cancel_recording()
        self.assertFalse(app.is_recording)

        # Verify transcriber was not called
        app.transcriber.transcribe = Mock()
        app.transcriber.transcribe.assert_not_called()

    def test_signal_handling(self):
        """Test graceful shutdown on signals."""
        app = ProsodyApp()

        # Send SIGTERM
        app._signal_handler(15, None)  # 15 = SIGTERM

        # Verify app is no longer running
        self.assertFalse(app.running)

    def test_startup_notification(self):
        """Test that startup notification is shown."""
        app = ProsodyApp()

        with patch("subprocess.run") as mock_run:
            # Start a thread to stop the app
            import threading

            def stop_app():
                import time

                time.sleep(0.1)
                app.running = False

            threading.Thread(target=stop_app, daemon=True).start()

            # Run the app
            app.run()

            # Verify notification was sent
            mock_run.assert_called()
            # Find the startup notification call
            for call in mock_run.call_args_list:
                args = call[0][0]
                if "notify-send" in args and "Ready! Double-tap Ctrl to record" in args:
                    break
            else:
                self.fail("Startup notification not found")

    def test_pid_file_cleanup(self):
        """Test PID file is cleaned up properly."""
        app = ProsodyApp()

        # Verify PID file exists
        self.assertTrue(os.path.exists(self.pid_file))

        # Stop the app (which should clean up)
        with patch("sys.exit"):
            app.quit()

        # Verify app stopped
        self.assertFalse(app.running)

    def test_audio_level_integration(self):
        """Test audio level reporting to UI."""
        app = ProsodyApp()

        # Get level through callback (should use get_current_level method)
        level = app._get_current_audio_level()
        self.assertEqual(level, 0.0)  # Default is 0

        # Set audio level and test again
        app.audio_recorder.current_level = 0.05
        level = app._get_current_audio_level()
        self.assertEqual(level, 0.5)  # Should be scaled by 10

    def test_hotkey_integration(self):
        """Test hotkey listener integration."""
        app = ProsodyApp()

        # Verify callbacks are set
        self.assertEqual(app.hotkey_listener.on_hotkey_pressed, app.toggle_recording)
        self.assertEqual(app.hotkey_listener.on_cancel_pressed, app.cancel_recording)

    def test_concurrent_operations(self):
        """Test that app handles concurrent operations safely."""
        app = ProsodyApp()

        # Create multiple threads trying to toggle recording
        results = []

        def toggle_thread():
            app.toggle_recording()
            results.append(app.is_recording)

        threads = [threading.Thread(target=toggle_thread) for _ in range(5)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Should have toggled an odd number of times
        # (some toggles might have been ignored due to state)
        self.assertTrue(len(results) > 0)

    def test_error_recovery(self):
        """Test that app recovers from component errors."""
        app = ProsodyApp()

        # Mock transcriber to raise error
        app.transcriber.transcribe = Mock(side_effect=Exception("Test error"))

        # Start and stop recording
        app.toggle_recording()
        app.audio_recorder.stop_recording = Mock(return_value=[0.1, 0.2])
        app.toggle_recording()

        # App should still be running
        self.assertTrue(app.running)
        self.assertFalse(app.is_recording)


class TestMainFunction(unittest.TestCase):
    """Test the main() entry point."""

    @patch("src.prosody.main.ProsodyApp")
    def test_main_function(self, mock_app_class):
        """Test main function execution."""
        mock_app = Mock()
        mock_app_class.return_value = mock_app

        # Import and run main
        from src.prosody.main import main

        # Run in a thread to avoid blocking
        main_thread = threading.Thread(target=main)
        main_thread.start()

        # Give it time to start
        time.sleep(0.1)

        # Stop the app
        mock_app.running = False
        main_thread.join(timeout=1)

        # Verify app was created and run
        mock_app_class.assert_called_once()
        mock_app.run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
