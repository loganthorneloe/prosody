#!/usr/bin/env python3
"""
Prosody: A Local, AI-Powered Dictation Tool (Refactored)

Refactored to use Single Responsibility Principle and Dependency Injection
for better testability and maintainability.
"""

import argparse
import logging
import sys
import threading
import time
import queue
import platform
from typing import Optional, List, Protocol, runtime_checkable
from dataclasses import dataclass
from abc import ABC, abstractmethod

import numpy as np
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Controller as KeyboardController, Key
from faster_whisper import WhisperModel
from transformers import pipeline
import torch


# Global configuration constants
LLM_REFINEMENT_PROMPT_TEMPLATE = """<|im_start|>system
Remove "um", "uh", "er" and add periods. Keep everything else exactly the same.<|im_end|>
<|im_start|>user
{text}<|im_end|>
<|im_start|>assistant
"""


@dataclass
class Config:
    """Configuration settings for Prosody"""
    hotkey: str = "ctrl_l"
    push_to_talk: bool = False
    debug: bool = False
    whisper_model_name: str = "small"
    sample_rate: int = 16000
    hotkey_double_tap_threshold: float = 0.5
    input_device: Optional[int] = None


@dataclass
class DictationState:
    """Holds the current state of the dictation process"""
    is_recording: bool = False
    audio_data: List[np.ndarray] = None
    transcription: Optional[str] = None
    
    def __post_init__(self):
        if self.audio_data is None:
            self.audio_data = []
    
    def reset(self):
        """Reset state for a new dictation session"""
        self.is_recording = False
        self.audio_data = []
        self.transcription = None


# Abstract interfaces for dependency injection
@runtime_checkable
class TranscriptionServiceProtocol(Protocol):
    """Protocol for transcription services"""
    
    def transcribe(self, audio_data: List[np.ndarray]) -> Optional[str]:
        """Transcribe audio data to text"""
        ...


@runtime_checkable
class TextRefinementServiceProtocol(Protocol):
    """Protocol for text refinement services"""
    
    def refine_text(self, text: str) -> str:
        """Refine and clean up text"""
        ...


@runtime_checkable
class TypingServiceProtocol(Protocol):
    """Protocol for typing services"""
    
    def type_text(self, text: str) -> bool:
        """Type text into active application"""
        ...


class ConsoleUI:
    """Manages all console output"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def show_startup_banner(self):
        """Display startup banner"""
        print("\n" + "="*60)
        print("""
    ____                            __     
   / __ \\_________  _________  ____/ /_  __
  / /_/ / ___/ __ \\/ ___/ __ \\/ __  / / / /
 / ____/ /  / /_/ (__  ) /_/ / /_/ / /_/ / 
/_/   /_/   \\____/____/\\____/\\__,_/\\__, /  
                                  /____/   
        """)
        print("🎙️  Local Dictation Tool")
        print("="*60)
    
    def show_loading_message(self, component: str):
        """Show loading message for a component"""
        print(f"🤖 Loading {component}...")
    
    def show_success_message(self, component: str):
        """Show success message for a component"""
        print(f"✅ {component} ready")
    
    def show_error_message(self, component: str, error: str):
        """Show error message for a component"""
        print(f"❌ {component} failed: {error}")
    
    def show_gpu_acceleration(self, device: str):
        """Show GPU acceleration information"""
        if device == "cpu":
            print("⚠️  No GPU acceleration found - using CPU (will be slower)")
        else:
            print(f"🚀 GPU acceleration: {device}")
    
    def show_ready_state(self, config: Config):
        """Show ready state and instructions"""
        mode_desc = "push-to-talk" if config.push_to_talk else "toggle mode"
        print("🎉 READY TO DICTATE!")
        print("="*50)
        print(f"Mode: {mode_desc}")
        print(f"Hotkey: {config.hotkey}")
        if not config.push_to_talk:
            print("Double-tap hotkey to start/stop recording, text appears when you stop")
        else:
            print("Hold hotkey to record, release to stop and insert text")
        print("="*50)
        print()
        print("Listening for hotkeys... (Press Ctrl+C to exit)")
    
    def show_recording_status(self):
        """Show recording status"""
        print("🎙️  Recording...")
    
    def show_processing_status(self):
        """Show processing status"""
        print("🧠 Refining...")
    
    def show_raw_transcription(self, text: str):
        """Show raw Whisper transcription"""
        print(f"🎤 Raw: {text}")
    
    def show_output(self, text: str):
        """Show refined output"""
        print(f"📝 Refined: {text}")
    
    def show_no_speech_detected(self):
        """Show no speech detected message"""
        print("❌ No speech detected")
    
    def show_permission_warning(self, permission_type: str):
        """Show permission warning"""
        if permission_type == "microphone":
            print("⚠️  MICROPHONE ACCESS REQUIRED")
            print("   Go to: System Settings > Privacy & Security > Microphone")
            print("   Enable access for your terminal application")
        elif permission_type == "accessibility":
            print("⚠️  ACCESSIBILITY ACCESS REQUIRED")
            print("   Go to: System Settings > Privacy & Security > Accessibility")
            print("   Add your terminal application and enable it")


class PermissionManager:
    """Handles macOS permission checks"""
    
    def __init__(self, ui: ConsoleUI):
        self.ui = ui
        self.logger = logging.getLogger(__name__)
    
    def check_essential_permissions(self) -> bool:
        """Check essential permissions on macOS"""
        if platform.system() != "Darwin":
            return True
        
        if self.ui.debug:
            print("🔍 Checking permissions...")
        
        mic_ok = self.check_microphone_permission()
        if not mic_ok:
            self.ui.show_permission_warning("microphone")
        elif self.ui.debug:
            print("✅ Microphone access OK")
        
        if self.ui.debug:
            print()
            print("ℹ️  ABOUT PERMISSIONS:")
            print("   • MICROPHONE: Required to capture your speech")
            print("   • ACCESSIBILITY: Required to type text into apps")
            print("     (Prosody simulates keyboard input to insert transcribed text)")
            print()
            print("   Prosody will ask for these when first needed.")
            print("   You can use basic dictation with just microphone access.")
        
        return mic_ok
    
    def check_microphone_permission(self) -> bool:
        """Check if microphone permission is granted"""
        try:
            # Try to query audio devices to test microphone access
            _ = sd.query_devices()
            
            # Try to create a temporary input stream
            with sd.InputStream(samplerate=16000, channels=1, blocksize=1024):
                pass
            return True
        except Exception:
            return False
    
    def check_accessibility_permission(self) -> bool:
        """Check if accessibility permission is granted"""
        try:
            # Test if we can create a keyboard controller
            controller = KeyboardController()
            
            # Try to press and release a key (this requires accessibility permission)
            controller.press('f13')  # F13 key is rarely used and won't interfere
            controller.release('f13')
            return True
        except Exception:
            return False


class DeviceManager:
    """Manages hardware acceleration device detection"""
    
    def __init__(self, ui: ConsoleUI):
        self.ui = ui
        self.logger = logging.getLogger(__name__)
    
    def get_best_device(self) -> str:
        """Detect the best available device for AI acceleration"""
        # NVIDIA CUDA (Windows/Linux)
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            self.logger.info(f"CUDA GPU detected: {device_name}")
            self.ui.show_gpu_acceleration(device_name)
            return "cuda"
        
        # Apple Metal Performance Shaders (macOS)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            self.logger.info("Apple Metal Performance Shaders detected")
            self.ui.show_gpu_acceleration("Apple Metal Performance Shaders")
            return "mps"
        
        # DirectML (Windows with AMD/Intel GPUs)
        try:
            import torch_directml
            if torch_directml.is_available():
                self.logger.info("DirectML detected (Windows GPU acceleration)")
                self.ui.show_gpu_acceleration("DirectML (Windows)")
                return torch_directml.device()
        except ImportError:
            pass
        
        # Intel Extension for PyTorch (Intel GPUs/NPUs)
        try:
            import intel_extension_for_pytorch as ipex
            if ipex.xpu.is_available():
                self.logger.info("Intel XPU detected")
                self.ui.show_gpu_acceleration("Intel XPU")
                return "xpu"
        except ImportError:
            pass
        
        # Fallback to CPU
        self.logger.warning("No GPU acceleration detected, using CPU")
        self.ui.show_gpu_acceleration("cpu")
        return "cpu"


class AudioRecorder:
    """Manages all sounddevice interactions for recording audio"""
    
    def __init__(self, config: Config, state: DictationState, ui: ConsoleUI):
        self.config = config
        self.state = state
        self.ui = ui
        self.logger = logging.getLogger(__name__)
        self.audio_queue = queue.Queue()
        self.stream = None
        self.processing_thread = None
    
    def list_audio_devices(self):
        """List available audio input devices"""
        print("\nAvailable audio input devices:")
        devices = sd.query_devices()
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  [{idx}] {device['name']} (Channels: {device['max_input_channels']})")
    
    def audio_callback(self, indata, _frames, _time_info, status):
        """Callback for audio recording"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        
        if self.state.is_recording:
            # Copy the audio data and add to queue
            self.audio_queue.put(indata.copy())
    
    def start_recording(self):
        """Start audio recording"""
        try:
            self.state.reset()
            self.state.is_recording = True
            
            self.ui.show_recording_status()
            
            # Start audio stream
            self.stream = sd.InputStream(
                device=self.config.input_device,
                channels=1,
                samplerate=self.config.sample_rate,
                callback=self.audio_callback,
                blocksize=int(self.config.sample_rate * 0.1)  # 100ms blocks
            )
            self.stream.start()
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._process_audio_queue)
            self.processing_thread.start()
            
            self.logger.info("Recording started")
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            self.state.is_recording = False
    
    def stop_recording(self):
        """Stop audio recording and process the result"""
        if not self.state.is_recording:
            return
            
        try:
            self.state.is_recording = False
            
            # Stop the stream
            if self.stream:
                self.stream.stop()
                self.stream.close()
            
            # Wait for threads to finish
            if self.processing_thread:
                self.processing_thread.join()
            
            self.logger.info("Recording stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
    
    def _process_audio_queue(self):
        """Process audio data from the queue"""
        while self.state.is_recording or not self.audio_queue.empty():
            try:
                # Get audio data with timeout
                audio_chunk = self.audio_queue.get(timeout=0.1)
                self.state.audio_data.append(audio_chunk)
            except queue.Empty:
                continue


class TranscriptionService:
    """Wraps the Whisper model to perform speech-to-text"""
    
    def __init__(self, config: Config, device_manager: DeviceManager):
        self.config = config
        self.device_manager = device_manager
        self.logger = logging.getLogger(__name__)
        self.whisper_model = None
    
    def initialize(self) -> bool:
        """Initialize the Whisper model"""
        try:
            self.logger.info(f"Loading Whisper model: {self.config.whisper_model_name}")
            
            # Use hardware acceleration for Whisper
            device = self.device_manager.get_best_device()
            
            # faster-whisper doesn't support MPS directly, but we can optimize compute_type
            if device == "mps":
                # For Mac, use CPU with optimized compute type
                whisper_device = "cpu"
                compute_type = "int8"  # More aggressive quantization for speed
            elif device == "cuda":
                whisper_device = "cuda"
                compute_type = "float16"
            else:
                whisper_device = "cpu"
                compute_type = "int8"
            
            self.whisper_model = WhisperModel(
                self.config.whisper_model_name, 
                device=whisper_device,
                compute_type=compute_type
            )
            self.logger.info("Whisper model loaded successfully")
            return True
        except (ConnectionError, OSError) as e:
            self.logger.error(f"Network error loading Whisper model: {e}")
            raise ConnectionError("Model download failed. Please check your internet connection.")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe(self, audio_data: List[np.ndarray]) -> Optional[str]:
        """Transcribe the recorded audio using Whisper"""
        try:
            # Check if Whisper model is loaded
            if self.whisper_model is None:
                self.logger.error("Whisper model not loaded - cannot transcribe audio")
                return None
            
            # Combine all audio chunks
            if not audio_data:
                return None
                
            audio_array = np.concatenate(audio_data, axis=0)
            audio_array = audio_array.flatten()
            
            # Ensure float32 format for Whisper
            if audio_array.dtype != np.float32:
                audio_array = audio_array.astype(np.float32)
            
            self.logger.info("Transcribing audio...")
            
            # Transcribe
            segments, _ = self.whisper_model.transcribe(
                audio_array,
                beam_size=5,
                language="en",
                condition_on_previous_text=True
            )
            
            # Combine segments
            transcription = " ".join([segment.text.strip() for segment in segments])
            
            self.logger.info(f"Raw transcription: {transcription}")
            return transcription
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return None


class TextRefinementService:
    """Wraps the LLM pipeline to clean up transcribed text"""
    
    def __init__(self, config: Config, device_manager: DeviceManager):
        self.config = config
        self.device_manager = device_manager
        self.logger = logging.getLogger(__name__)
        self.text_llm = None
    
    def initialize(self) -> bool:
        """Initialize the text refinement LLM"""
        try:
            self.logger.info("Loading Qwen2.5 1.5B for text refinement")
            
            device = self.device_manager.get_best_device()
            
            # Suppress transformers warnings during model loading
            import warnings
            import logging
            transformers_logger = logging.getLogger("transformers")
            old_level = transformers_logger.level
            transformers_logger.setLevel(logging.ERROR)
            
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                
                # Use original model for better quality
                self.text_llm = pipeline(
                    "text-generation",
                    model="Qwen/Qwen2.5-1.5B-Instruct",
                    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                    device=device,
                    model_kwargs={
                        "low_cpu_mem_usage": True,
                        "use_cache": True,
                    }
                )
            
            # Restore logger level
            transformers_logger.setLevel(old_level)
            
            self.logger.info(f"Using device: {device}")
            self.logger.info("Text refinement LLM loaded successfully")
            return True
        except (ConnectionError, OSError) as e:
            self.logger.error(f"Network error loading text refinement LLM: {e}")
            raise ConnectionError("Model download failed. Please check your internet connection.")
        except Exception as e:
            self.logger.error(f"Failed to load text refinement LLM: {e}")
            if self.config.debug:
                import traceback
                self.logger.error(f"Full traceback: {traceback.format_exc()}")
            raise
    
    def refine_text(self, text: str) -> str:
        """Use LLM to refine and clean up transcribed text"""
        if not text or not self.text_llm:
            return self._basic_text_cleanup(text)
        
        try:
            prompt = LLM_REFINEMENT_PROMPT_TEMPLATE.format(text=text)

            # Optimized generation settings for speed
            response = self.text_llm(
                prompt,
                max_new_tokens=len(text.split()) + 20,  # Dynamic based on input length
                do_sample=False,  # Use greedy decoding for speed
                temperature=None,  # Explicitly disable temperature
                top_p=None,  # Explicitly disable top_p
                top_k=None,  # Explicitly disable top_k
                pad_token_id=self.text_llm.tokenizer.eos_token_id,
                return_full_text=False,
                use_cache=True,  # Use KV cache
                num_beams=1,  # No beam search for speed
            )
            
            refined_text = response[0]['generated_text'].strip()
            
            # Remove quotes if the LLM wrapped the output in them
            if refined_text.startswith('"') and refined_text.endswith('"'):
                refined_text = refined_text[1:-1]
            elif refined_text.startswith("'") and refined_text.endswith("'"):
                refined_text = refined_text[1:-1]
            
            self.logger.info(f"LLM refined: '{text}' -> '{refined_text}'")
            return refined_text
            
        except Exception as e:
            self.logger.error(f"LLM text refinement failed: {e}")
            return self._basic_text_cleanup(text)
    
    def _basic_text_cleanup(self, text: str) -> str:
        """Basic text cleanup fallback"""
        if not text:
            return text
        try:
            # Remove common filler words
            filler_words = ["um", "uh", "er", "ah"]
            words = text.split()
            cleaned_words = [w for w in words if w.lower() not in filler_words]
            return " ".join(cleaned_words)
        except Exception:
            return text


class TypingService:
    """Wraps the pynput controller to type text into applications"""
    
    def __init__(self, ui: ConsoleUI):
        self.ui = ui
        self.logger = logging.getLogger(__name__)
        self.keyboard_controller = KeyboardController()
    
    def type_text(self, text: str) -> bool:
        """Type the given text using keyboard simulation"""
        if not text:
            return True
            
        try:
            # Small delay to ensure focus
            time.sleep(0.1)
            
            # Type the text with a space at the end
            self.keyboard_controller.type(text + " ")
            
            self.logger.info("Text typed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to type text: {e}")
            print(f"\n⚠️  Could not type text automatically: {e}")
            print("📋 Your transcribed text:")
            print(f'   "{text}"')
            print("💡 To enable automatic typing, grant Accessibility permission:")
            print("   System Settings > Privacy & Security > Accessibility")
            print("   Add your terminal application and enable it.")
            print()
            return False


class HotkeyListener:
    """Manages the keyboard listener and triggers events"""
    
    def __init__(self, config: Config, ui: ConsoleUI):
        self.config = config
        self.ui = ui
        self.logger = logging.getLogger(__name__)
        
        # Hotkey tracking
        self.last_hotkey_time = 0
        
        # Push-to-talk state
        self.key_pressed = False
        self.key_release_timer = None
        
        # Event callbacks
        self.on_start_recording = None
        self.on_stop_recording = None
    
    def set_callbacks(self, on_start_recording, on_stop_recording):
        """Set callback functions for recording events"""
        self.on_start_recording = on_start_recording
        self.on_stop_recording = on_stop_recording
    
    def on_hotkey_press(self, key):
        """Handle hotkey press events"""
        current_time = time.time()
        
        # Check if the correct key is pressed
        hotkey_matched = self._is_hotkey_match(key)
        
        if hotkey_matched:
            if self.config.push_to_talk:
                # Push-to-talk mode: start recording on key press
                if not self.key_pressed:
                    self.key_pressed = True
                    if self.on_start_recording:
                        self.on_start_recording()
                    
                    # Cancel any pending release timer
                    if self.key_release_timer:
                        self.key_release_timer.cancel()
                        self.key_release_timer = None
            else:
                # Toggle mode: double-tap to toggle
                if current_time - self.last_hotkey_time < self.config.hotkey_double_tap_threshold:
                    if self.on_start_recording:
                        self.on_start_recording()
                    
                    # Reset timer to prevent triple-tap
                    self.last_hotkey_time = 0
                else:
                    self.last_hotkey_time = current_time
    
    def on_hotkey_release(self, key):
        """Handle hotkey release events"""
        if not self.config.push_to_talk:
            return
            
        # Check if the correct key is released
        hotkey_matched = self._is_hotkey_match(key)
        
        if hotkey_matched and self.key_pressed:
            self.key_pressed = False
            
            # Add small delay to prevent accidental releases
            self.key_release_timer = threading.Timer(0.1, self._handle_key_release)
            self.key_release_timer.start()
    
    def _handle_key_release(self):
        """Handle delayed key release in push-to-talk mode"""
        if not self.key_pressed and self.on_stop_recording:
            self.on_stop_recording()
    
    def _is_hotkey_match(self, key) -> bool:
        """Check if the key matches the configured hotkey"""
        hotkey_map = {
            "ctrl_l": Key.ctrl_l,
            "ctrl_r": Key.ctrl_r,
            "f12": Key.f12,
            "f11": Key.f11,
            "f10": Key.f10,
            "f9": Key.f9,
            "cmd": Key.cmd,
            "alt": Key.alt,
        }
        return key == hotkey_map.get(self.config.hotkey)
    
    def start_listening(self):
        """Start keyboard listener"""
        with keyboard.Listener(
            on_press=self.on_hotkey_press,
            on_release=self.on_hotkey_release
        ) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                self.logger.info("Shutting down...")
                
                # Clean up timers
                if self.key_release_timer:
                    self.key_release_timer.cancel()


class AppController:
    """Central orchestrator that coordinates all services"""
    
    def __init__(self, 
                 config: Config,
                 ui: ConsoleUI,
                 permission_manager: PermissionManager,
                 device_manager: DeviceManager,
                 audio_recorder: AudioRecorder,
                 transcription_service: TranscriptionServiceProtocol,
                 text_refinement_service: TextRefinementServiceProtocol,
                 typing_service: TypingServiceProtocol,
                 hotkey_listener: HotkeyListener):
        
        self.config = config
        self.ui = ui
        self.permission_manager = permission_manager
        self.device_manager = device_manager
        self.audio_recorder = audio_recorder
        self.transcription_service = transcription_service
        self.text_refinement_service = text_refinement_service
        self.typing_service = typing_service
        self.hotkey_listener = hotkey_listener
        
        self.state = DictationState()
        self.logger = logging.getLogger(__name__)
        
        # Set up callbacks
        self.hotkey_listener.set_callbacks(
            on_start_recording=self._on_start_recording,
            on_stop_recording=self._on_stop_recording
        )
    
    def startup(self) -> bool:
        """Initialize all services and prepare for dictation"""
        self.ui.show_startup_banner()
        
        # Setup logging
        if self.config.debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            logging.basicConfig(
                level=logging.WARNING,
                format='%(levelname)s: %(message)s'
            )
        
        # Check permissions
        self.permission_manager.check_essential_permissions()
        
        # Load speech recognition
        self.ui.show_loading_message(f"Whisper {self.config.whisper_model_name} speech recognition")
        try:
            self.transcription_service.initialize()
            self.ui.show_success_message(f"Whisper {self.config.whisper_model_name} speech recognition")
        except ConnectionError as e:
            self.ui.show_error_message(f"Whisper {self.config.whisper_model_name} speech recognition", str(e))
            return False
        except Exception as e:
            self.ui.show_error_message(f"Whisper {self.config.whisper_model_name} speech recognition", str(e))
            return False
        
        # Load text refinement LLM
        self.ui.show_loading_message("Qwen2.5-1.5B text refinement")
        try:
            self.text_refinement_service.initialize()
            self.ui.show_success_message("Qwen2.5-1.5B text refinement")
        except ConnectionError as e:
            self.ui.show_error_message("Qwen2.5-1.5B text refinement", str(e))
            print("   Falling back to basic text cleanup")
        except Exception as e:
            self.ui.show_error_message("Qwen2.5-1.5B text refinement", str(e))
            print("   Falling back to basic text cleanup")
        
        # Show ready state
        self.ui.show_ready_state(self.config)
        
        return True
    
    def run(self):
        """Start the main application loop"""
        try:
            self.hotkey_listener.start_listening()
        except KeyboardInterrupt:
            print("\nShutting down...")
            sys.exit(0)
    
    def _on_start_recording(self):
        """Handle start recording event"""
        if self.state.is_recording:
            # Already recording, stop instead (toggle mode)
            self._on_stop_recording()
        else:
            self.audio_recorder.start_recording()
            self.state.is_recording = True
    
    def _on_stop_recording(self):
        """Handle stop recording event"""
        if not self.state.is_recording:
            return
        
        self.audio_recorder.stop_recording()
        self.state.is_recording = False
        
        # Process the complete audio
        if self.state.audio_data:
            self._process_dictation()
        else:
            self.ui.show_no_speech_detected()
    
    def _process_dictation(self):
        """Process the complete dictation workflow"""
        # Transcribe audio
        transcription = self.transcription_service.transcribe(self.state.audio_data)
        if not transcription or not transcription.strip():
            self.ui.show_no_speech_detected()
            return
        
        self.state.transcription = transcription
        
        # Show raw Whisper output first
        self.ui.show_raw_transcription(transcription)
        
        # Show that we're starting refinement
        self.ui.show_processing_status()
        
        # Apply intelligent text refinement
        refined_text = self.text_refinement_service.refine_text(transcription)
        
        # Show the output
        self.ui.show_output(refined_text)
        
        # Type the result
        self.typing_service.type_text(refined_text)


def create_app(config: Config) -> AppController:
    """Factory function to create the application with all dependencies"""
    
    # Create UI
    ui = ConsoleUI(debug=config.debug)
    
    # Create managers
    permission_manager = PermissionManager(ui)
    device_manager = DeviceManager(ui)
    
    # Create state
    state = DictationState()
    
    # Create services
    audio_recorder = AudioRecorder(config, state, ui)
    transcription_service = TranscriptionService(config, device_manager)
    text_refinement_service = TextRefinementService(config, device_manager)
    typing_service = TypingService(ui)
    hotkey_listener = HotkeyListener(config, ui)
    
    # Create controller
    app = AppController(
        config=config,
        ui=ui,
        permission_manager=permission_manager,
        device_manager=device_manager,
        audio_recorder=audio_recorder,
        transcription_service=transcription_service,
        text_refinement_service=text_refinement_service,
        typing_service=typing_service,
        hotkey_listener=hotkey_listener
    )
    
    # Use the same state object in AppController
    app.state = state
    
    return app


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Prosody: Local AI-Powered Dictation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with optimal defaults (recommended)
  python prosody_refactored.py
  
  # Use different hotkey
  python prosody_refactored.py --hotkey f12
  
  # Enable push-to-talk mode
  python prosody_refactored.py --push-to-talk
  
  # Enable debug mode with verbose logging
  python prosody_refactored.py --debug
        """
    )
    
    parser.add_argument(
        "--hotkey",
        type=str,
        default="ctrl_l",
        choices=["ctrl_l", "ctrl_r", "f12", "f11", "f10", "f9", "cmd", "alt"],
        help="Hotkey to toggle dictation (default: ctrl_l - double-tap to activate)"
    )
    
    parser.add_argument(
        "--push-to-talk",
        action="store_true",
        help="Enable push-to-talk mode (record while key is held down)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model to use for transcription (default: small)"
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = Config(
        hotkey=args.hotkey,
        push_to_talk=args.push_to_talk,
        debug=args.debug,
        whisper_model_name=args.model
    )
    
    # Create and run application
    app = create_app(config)
    
    # Run startup sequence
    try:
        if not app.startup():
            print("❌ Startup failed. Exiting.")
            sys.exit(1)
        
        # Run the application
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()