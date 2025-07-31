"""Polished UI with full-width waveform and proper tray menu."""

import threading
import queue
import time
import numpy as np
from typing import Optional, Callable

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk


class PolishedWaveformIndicator:
    """Pill-shaped waveform that uses the full width including rounded edges."""

    def __init__(self, get_audio_level: Callable[[], float]):
        """Initialize the waveform indicator.

        Args:
            get_audio_level: Function that returns current audio level (0.0 to 1.0)
        """
        self.get_audio_level = get_audio_level
        self.root: Optional[tk.Tk] = None
        self.window: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self.command_queue = queue.Queue()
        self.thread: Optional[threading.Thread] = None
        self.waveform_lines = []
        self.history = [0.0] * 50  # Audio level history
        self._start_gui_thread()

    def _start_gui_thread(self):
        """Start the GUI thread."""
        self.thread = threading.Thread(target=self._gui_thread, daemon=True)
        self.thread.start()
        time.sleep(0.1)

    def _gui_thread(self):
        """Run the GUI in its own thread."""
        self.root = tk.Tk()
        self.root.withdraw()

        def process_queue():
            try:
                while True:
                    command = self.command_queue.get_nowait()
                    if command == "show":
                        self._create_waveform()
                    elif command == "hide":
                        self._destroy_waveform()
                    elif command == "quit":
                        self.root.quit()
                        return
            except queue.Empty:
                pass
            finally:
                self.root.after(50, process_queue)

        self.root.after(50, process_queue)
        self.root.mainloop()

    def _create_waveform(self):
        """Create the pill-shaped waveform window."""
        if self.window is not None:
            return

        self.window = tk.Toplevel(self.root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        # Make window transparent
        self.window.wait_visibility()
        self.window.wm_attributes("-transparentcolor", "black")
        self.window.configure(bg="black")

        # Small pill size
        width, height = 140, 36
        self.canvas = tk.Canvas(
            self.window, width=width, height=height, bg="black", highlightthickness=0
        )
        self.canvas.pack()

        # Draw pill background
        radius = height // 2
        # Left circle
        self.canvas.create_oval(
            0, 0, height, height, fill="#1a1a1a", outline="#333333", width=1
        )
        # Right circle
        self.canvas.create_oval(
            width - height, 0, width, height, fill="#1a1a1a", outline="#333333", width=1
        )
        # Center rectangle
        self.canvas.create_rectangle(
            radius, 0, width - radius, height, fill="#1a1a1a", outline="", width=0
        )
        # Top and bottom borders
        self.canvas.create_line(radius, 0, width - radius, 0, fill="#333333", width=1)
        self.canvas.create_line(
            radius, height - 1, width - radius, height - 1, fill="#333333", width=1
        )

        # Position at bottom center of screen
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = (screen_width - width) // 2
        y_position = screen_height - height - 40
        self.window.geometry(f"{width}x{height}+{x_position}+{y_position}")

        # Start animation
        self._animate_waveform()

    def _animate_waveform(self):
        """Animate the waveform using full pill width."""
        if not self.window or not self.canvas:
            return

        # Clear previous lines
        for line in self.waveform_lines:
            self.canvas.delete(line)
        self.waveform_lines = []

        # Get current audio level
        current_level = self.get_audio_level()

        # Update history
        self.history.pop(0)
        self.history.append(current_level)

        # Draw waveform
        width = 140
        height = 36
        center_y = height // 2

        # Create points for the waveform
        # Use more points and extend to edges
        points = []
        num_points = 40

        for i in range(num_points):
            # Map i to x position (from edge to edge)
            x = 5 + (i * (width - 10) / (num_points - 1))

            # Get interpolated audio level
            history_index = int(i * len(self.history) / num_points)
            level = (
                self.history[history_index] if history_index < len(self.history) else 0
            )

            # Add some smooth variation
            smooth_factor = np.sin(i * np.pi / (num_points - 1))  # Bell curve
            y = center_y - (level * 12 * smooth_factor)

            points.extend([x, y])

        if len(points) >= 4:
            # Draw main waveform line
            line = self.canvas.create_line(
                points, fill="white", width=2, smooth=True, splinesteps=20
            )
            self.waveform_lines.append(line)

            # Draw glow effect
            glow = self.canvas.create_line(
                points, fill="#444444", width=4, smooth=True, splinesteps=20
            )
            self.canvas.tag_lower(glow)
            self.waveform_lines.append(glow)

        # Continue animation
        self.window.after(40, self._animate_waveform)

    def _destroy_waveform(self):
        """Destroy the waveform window."""
        if self.window:
            try:
                self.window.destroy()
            except:
                pass
            self.window = None
            self.canvas = None
            self.waveform_lines = []

    def show(self):
        """Show the waveform indicator."""
        self.command_queue.put("show")

    def hide(self):
        """Hide the waveform indicator."""
        self.command_queue.put("hide")

    def __del__(self):
        """Cleanup when destroyed."""
        try:
            self.command_queue.put("quit")
        except:
            pass


def type_text(text: str):
    """Type the given text into the currently focused application."""
    from pynput.keyboard import Controller

    keyboard = Controller()

    for char in text:
        keyboard.type(char)

    time.sleep(0.1)
