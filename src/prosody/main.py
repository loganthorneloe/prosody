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


class ProsodyApp:
    """Main application class that coordinates all components."""

    def __init__(self):
        """Initialize the Prosody application."""
        self.audio_recorder = AudioRecorder()
        self.transcriber = Transcriber()
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
        print("\nShutting down Prosody...")
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

        print("Starting recording...")
        self.is_recording = True

        # Show recording indicator
        self.recording_indicator.show()

        # Start audio recording
        try:
            self.audio_recorder.start_recording()
        except Exception as e:
            print(f"Error starting recording: {e}")
            self.is_recording = False
            self.recording_indicator.hide()

    def stop_recording(self):
        """Stop recording and transcribe audio."""
        if not self.is_recording:
            return

        print("Stopping recording...")
        self.is_recording = False

        # Hide recording indicator
        self.recording_indicator.hide()

        # Stop recording and get audio data
        audio_data = self.audio_recorder.stop_recording()

        if len(audio_data) > 0:
            print("Transcribing audio...")

            # Transcribe in a separate thread to avoid blocking
            threading.Thread(
                target=self._transcribe_and_type, args=(audio_data,), daemon=True
            ).start()
        else:
            print("No audio recorded")

    def cancel_recording(self):
        """Cancel recording without transcribing."""
        if not self.is_recording:
            return

        print("Recording cancelled")
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
            # Transcribe the audio
            text = self.transcriber.transcribe(audio_data)

            if text:
                print(f"Transcribed: {text}")
                # Type the transcribed text
                type_text(text)
            else:
                print("No speech detected")

        except Exception as e:
            print(f"Transcription error: {e}")

    def run(self):
        """Run the main application loop."""
        print("Prosody is starting...")
        print("Double-tap Left Ctrl to start/stop recording")
        print("Double-tap Escape to cancel recording")

        # Start the hotkey listener
        self.hotkey_listener.start()

        # Show startup notification
        try:
            subprocess.run(
                [
                    "notify-send",
                    "-i",
                    "audio-input-microphone",
                    "-t",
                    "2000",
                    "Prosody Speech-to-Text",
                    "Ready! Double-tap Ctrl to record",
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

        print("Prosody has stopped")
        sys.exit(0)


def main():
    """Main entry point."""
    app = ProsodyApp()
    app.run()


if __name__ == "__main__":
    main()
