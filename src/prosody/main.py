"""Main entry point for Prosody application."""

import sys
import os
import threading
import signal
import subprocess
from typing import Optional

from .hotkey import HotkeyListener
from .audio import AudioRecorder

# Use polished UI with waveform
from .ui_polished import PolishedWaveformIndicator as RecordingIndicator, type_text


from .transcription import Transcriber

# Check if running in development mode
DEV_MODE = os.environ.get('PROSODY_DEV') == '1' or sys.argv[0].endswith('__main__.py')


def log(message: str, important: bool = False):
    """Log a message, respecting dev/production mode."""
    if DEV_MODE:
        print(message)


class ProsodyApp:
    """Main application class that coordinates all components."""

    def __init__(self):
        """Initialize the Prosody application."""
        self.audio_recorder = AudioRecorder()
        self.transcriber = None  # Initialize later to control timing
        self.recording_indicator = RecordingIndicator(
            get_audio_level=self._get_current_audio_level
        )
        self.hotkey_listener = HotkeyListener(
            on_hotkey_pressed=self.toggle_recording,
            on_cancel_pressed=self.cancel_recording,
        )

        self.is_recording = False
        self.running = True

        # Write PID file
        self.pid_file = os.path.expanduser("~/.prosody.pid")
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        log("\nShutting down Prosody...")
        self.running = False

    def _get_current_audio_level(self):
        """Get current audio level for waveform visualization."""
        try:
            return self.audio_recorder.get_current_level()
        except:
            return 0.0

    def toggle_recording(self):
        """Toggle recording on/off."""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start audio recording."""
        if self.is_recording:
            return

        log("Starting recording...")
        self.is_recording = True

        # Show recording indicator
        self.recording_indicator.show()

        # Start audio recording
        try:
            self.audio_recorder.start_recording()
        except Exception as e:
            log(f"Error starting recording: {e}", important=True)
            self.is_recording = False
            self.recording_indicator.hide()
            # Show error notification
            try:
                subprocess.run(
                    [
                        "notify-send",
                        "-i", "dialog-error",
                        "-t", "3000",
                        "Prosody Error",
                        f"Failed to start recording: {e}",
                    ],
                    check=False,
                )
            except:
                pass

    def stop_recording(self):
        """Stop recording and transcribe audio."""
        if not self.is_recording:
            return

        log("Stopping recording...")
        self.is_recording = False

        # Hide recording indicator
        self.recording_indicator.hide()

        # Stop recording and get audio data
        audio_data = self.audio_recorder.stop_recording()

        if len(audio_data) > 0:
            log("Transcribing audio...")

            # Transcribe in a separate thread to avoid blocking
            threading.Thread(
                target=self._transcribe_and_type, args=(audio_data,), daemon=True
            ).start()
        else:
            log("No audio recorded")

    def cancel_recording(self):
        """Cancel recording without transcribing."""
        if not self.is_recording:
            return

        log("Recording cancelled")
        self.is_recording = False

        # Hide recording indicator
        self.recording_indicator.hide()

        # Stop recording but discard audio
        self.audio_recorder.stop_recording()

        # Notify user
        try:
            subprocess.run(
                [
                    "notify-send",
                    "-i",
                    "audio-input-microphone",
                    "-t",
                    "1500",
                    "Prosody",
                    "Recording cancelled",
                ],
                check=False,
            )
        except:
            pass

    def _transcribe_and_type(self, audio_data):
        """Transcribe audio and type the result."""
        try:
            # Check if transcriber is initialized
            if not self.transcriber:
                log("Transcriber not ready", important=True)
                return
                
            # Transcribe the audio
            text = self.transcriber.transcribe(audio_data)

            if text:
                log(f"Transcribed: {text}")
                # Type the transcribed text
                type_text(text)
            else:
                log("No speech detected")

        except Exception as e:
            log(f"Transcription error: {e}", important=True)

    def run(self):
        """Run the main application loop."""
        log("Prosody is starting...")
        log("Double-tap Left Ctrl to start/stop recording")
        log("Press Escape to cancel recording")

        # Initialize transcriber (loads model)
        log("Loading speech recognition model...")
        self.transcriber = Transcriber()

        # Start the hotkey listener
        self.hotkey_listener.start()

        # Show ready notification only after model is loaded
        try:
            subprocess.run(
                [
                    "notify-send",
                    "-i",
                    "audio-input-microphone",
                    "-t",
                    "2000",
                    "Prosody Ready",
                    "Double-tap Ctrl to start recording",
                ],
                check=False,
            )
        except:
            pass

        try:
            # Keep running
            while self.running:
                import time

                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.quit()

    def quit(self):
        """Quit the application gracefully."""
        if not self.running:
            return

        self.running = False

        # Stop recording if active
        if self.is_recording:
            self.stop_recording()

        # Stop components
        self.hotkey_listener.stop()
        self.recording_indicator.hide()

        # Clean up PID file
        try:
            os.remove(self.pid_file)
        except:
            pass

        log("Prosody has stopped")
        sys.exit(0)


def main():
    """Main entry point."""
    app = ProsodyApp()
    app.run()


if __name__ == "__main__":
    main()
