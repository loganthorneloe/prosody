"""Global hotkey listener for Prosody."""

import time
import threading
from typing import Callable, Optional
from pynput import keyboard

# Default hotkey configuration
HOTKEY = keyboard.Key.ctrl_l  # Left Control key
CANCEL_HOTKEY = keyboard.Key.esc  # Escape key
DOUBLE_PRESS_INTERVAL = 0.3  # Maximum time between presses (in seconds)


class HotkeyListener:
    """Listens for global hotkey events and triggers recording."""

    def __init__(
        self,
        on_hotkey_pressed: Callable[[], None],
        on_cancel_pressed: Optional[Callable[[], None]] = None,
    ):
        """Initialize the hotkey listener.

        Args:
            on_hotkey_pressed: Callback function to execute when hotkey is triggered
            on_cancel_pressed: Optional callback for cancel hotkey
        """
        self.on_hotkey_pressed = on_hotkey_pressed
        self.on_cancel_pressed = on_cancel_pressed
        self.is_recording = False
        self.last_press_time = 0
        self.last_escape_time = 0
        self.listener: Optional[keyboard.Listener] = None
        self._lock = threading.Lock()

    def _on_press(self, key):
        """Handle key press events."""
        current_time = time.time()

        if key == HOTKEY:
            with self._lock:
                # Check if this is a double press
                if current_time - self.last_press_time <= DOUBLE_PRESS_INTERVAL:
                    # Double press detected - toggle recording
                    self.is_recording = not self.is_recording
                    self.on_hotkey_pressed()
                    self.last_press_time = 0  # Reset to prevent triple press
                else:
                    # First press - record the time
                    self.last_press_time = current_time

        elif key == CANCEL_HOTKEY:
            with self._lock:
                # Check if this is a double escape press
                if current_time - self.last_escape_time <= DOUBLE_PRESS_INTERVAL:
                    # Double escape detected - cancel recording
                    if self.is_recording and self.on_cancel_pressed:
                        self.is_recording = False
                        self.on_cancel_pressed()
                    self.last_escape_time = 0  # Reset
                else:
                    # First escape press - record the time
                    self.last_escape_time = current_time

    def start(self):
        """Start listening for hotkey events."""
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def stop(self):
        """Stop listening for hotkey events."""
        if self.listener:
            self.listener.stop()
            self.listener = None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
