#!/usr/bin/env python3
"""
Test suite for refactored Prosody dictation tool
"""

import unittest
import tempfile
import os
import time
import threading
import numpy as np
from unittest.mock import Mock, patch, MagicMock, mock_open, PropertyMock
from pathlib import Path

from prosody import (
    Config, DictationState, ConsoleUI, PermissionManager, DeviceManager,
    AudioRecorder, TranscriptionService, TextRefinementService, TypingService,
    HotkeyListener, AppController, create_app
)


class BaseProsodyTest(unittest.TestCase):
    """Base test class with common mocks and setup"""
    
    def setUp(self):
        """Set up common mocks for all tests"""
        # Mock external dependencies
        self.whisper_patcher = patch('prosody.WhisperModel')
        self.pipeline_patcher = patch('prosody.pipeline')
        self.torch_patcher = patch('prosody.torch')
        self.sounddevice_patcher = patch('prosody.sd')
        self.keyboard_patcher = patch('prosody.KeyboardController')
        self.platform_patcher = patch('prosody.platform.system', return_value='Darwin')
        
        # Start all patches
        self.mock_whisper = self.whisper_patcher.start()
        self.mock_pipeline = self.pipeline_patcher.start()
        self.mock_torch = self.torch_patcher.start()
        self.mock_sd = self.sounddevice_patcher.start()
        self.mock_keyboard = self.keyboard_patcher.start()
        self.mock_platform = self.platform_patcher.start()
        
        # Configure common mock behavior
        self.mock_torch.backends.mps.is_available.return_value = True
        self.mock_torch.cuda.is_available.return_value = False
        self.mock_torch.float16 = 'float16'
        
        # Mock pipeline return
        self.mock_llm = MagicMock()
        self.mock_pipeline.return_value = self.mock_llm
        
        # Mock Whisper model
        self.mock_whisper_instance = MagicMock()
        self.mock_whisper.return_value = self.mock_whisper_instance
        
        # Mock audio devices
        self.mock_sd.query_devices.return_value = [
            {'name': 'Test Mic', 'max_input_channels': 1},
            {'name': 'Test Speaker', 'max_input_channels': 0}
        ]
        self.mock_sd.InputStream = MagicMock()
        
    def tearDown(self):
        """Clean up patches"""
        self.whisper_patcher.stop()
        self.pipeline_patcher.stop()
        self.torch_patcher.stop()
        self.sounddevice_patcher.stop()
        self.keyboard_patcher.stop()
        self.platform_patcher.stop()


class TestConfig(BaseProsodyTest):
    """Tests for the Config dataclass"""
    
    def test_default_initialization(self):
        """Test default configuration values"""
        config = Config()
        self.assertEqual(config.hotkey, "ctrl_l")
        self.assertFalse(config.push_to_talk)
        self.assertFalse(config.debug)
        self.assertEqual(config.whisper_model_name, "small")
        self.assertEqual(config.sample_rate, 16000)
        self.assertEqual(config.hotkey_double_tap_threshold, 0.5)
        self.assertIsNone(config.input_device)
    
    def test_custom_initialization(self):
        """Test configuration with custom values"""
        config = Config(
            hotkey="f12",
            push_to_talk=True,
            debug=True,
            whisper_model_name="large",
            sample_rate=22050,
            input_device=1
        )
        self.assertEqual(config.hotkey, "f12")
        self.assertTrue(config.push_to_talk)
        self.assertTrue(config.debug)
        self.assertEqual(config.whisper_model_name, "large")
        self.assertEqual(config.sample_rate, 22050)
        self.assertEqual(config.input_device, 1)


class TestDictationState(BaseProsodyTest):
    """Tests for the DictationState dataclass"""
    
    def test_initialization(self):
        """Test state initialization"""
        state = DictationState()
        self.assertFalse(state.is_recording)
        self.assertEqual(state.audio_data, [])
        self.assertIsNone(state.transcription)
    
    def test_reset(self):
        """Test state reset functionality"""
        state = DictationState()
        state.is_recording = True
        state.audio_data = [np.array([1, 2, 3])]
        state.transcription = "test"
        
        state.reset()
        
        self.assertFalse(state.is_recording)
        self.assertEqual(state.audio_data, [])
        self.assertIsNone(state.transcription)
    
    def test_thread_safety(self):
        """Test concurrent access to state object"""
        state = DictationState()
        
        def modify_state():
            for i in range(100):
                state.is_recording = not state.is_recording
                state.audio_data.append(np.array([i]))
                if len(state.audio_data) > 50:
                    state.reset()
        
        # Run concurrent modifications
        threads = [threading.Thread(target=modify_state) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # State should be consistent (no crashes)
        self.assertIsInstance(state.is_recording, bool)
        self.assertIsInstance(state.audio_data, list)


class TestConsoleUI(BaseProsodyTest):
    """Tests for the ConsoleUI class"""
    
    def test_initialization(self):
        """Test UI initialization"""
        ui = ConsoleUI(debug=True)
        self.assertTrue(ui.debug)
        
        ui = ConsoleUI(debug=False)
        self.assertFalse(ui.debug)
    
    def test_show_startup_banner(self):
        """Test startup banner display"""
        ui = ConsoleUI()
        with patch('builtins.print') as mock_print:
            ui.show_startup_banner()
            mock_print.assert_called()
            # Check that the banner was printed (look for the ASCII art or tool name)
            calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("Local Dictation Tool" in call for call in calls))
    
    def test_show_ready_state(self):
        """Test ready state display"""
        ui = ConsoleUI()
        config = Config(hotkey="ctrl_l", push_to_talk=False)
        
        with patch('builtins.print') as mock_print:
            ui.show_ready_state(config)
            mock_print.assert_called()
            calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("READY TO DICTATE" in call for call in calls))


class TestDeviceManager(BaseProsodyTest):
    """Tests for the DeviceManager class"""
    
    def test_get_best_device_mps(self):
        """Test device detection for Apple MPS"""
        self.mock_torch.cuda.is_available.return_value = False
        self.mock_torch.backends.mps.is_available.return_value = True
        
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        device = device_manager.get_best_device()
        self.assertEqual(device, "mps")
    
    def test_get_best_device_cuda(self):
        """Test device detection for CUDA"""
        self.mock_torch.cuda.is_available.return_value = True
        self.mock_torch.cuda.get_device_name.return_value = "RTX 4080"
        
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        device = device_manager.get_best_device()
        self.assertEqual(device, "cuda")
    
    def test_get_best_device_cpu_fallback(self):
        """Test CPU fallback when no acceleration available"""
        self.mock_torch.cuda.is_available.return_value = False
        self.mock_torch.backends.mps.is_available.return_value = False
        
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        device = device_manager.get_best_device()
        self.assertEqual(device, "cpu")
    
    def test_get_best_device_directml(self):
        """Test DirectML detection on Windows"""
        self.mock_torch.cuda.is_available.return_value = False
        self.mock_torch.backends.mps.is_available.return_value = False
        
        # Mock torch_directml import
        with patch('builtins.__import__') as mock_import:
            mock_directml = MagicMock()
            mock_directml.is_available.return_value = True
            mock_directml.device.return_value = "dml"
            
            def side_effect(name, *args, **kwargs):
                if name == 'torch_directml':
                    return mock_directml
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            ui = ConsoleUI()
            device_manager = DeviceManager(ui)
            device = device_manager.get_best_device()
            self.assertEqual(device, "dml")


class TestTextRefinementService(BaseProsodyTest):
    """Tests for the TextRefinementService class"""
    
    def test_basic_text_cleanup(self):
        """Test basic text cleanup functionality"""
        config = Config()
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        service = TextRefinementService(config, device_manager)
        
        # Test filler word removal
        input_text = "um so I was uh thinking that er maybe we should go"
        expected = "so I was thinking that maybe we should go"
        result = service._basic_text_cleanup(input_text)
        self.assertEqual(result, expected)
        
        # Test empty input
        self.assertEqual(service._basic_text_cleanup(""), "")
        
        # Test no filler words
        clean_text = "This is already clean text"
        self.assertEqual(service._basic_text_cleanup(clean_text), clean_text)
    
    def test_refine_text_with_llm(self):
        """Test text refinement with LLM"""
        config = Config()
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        service = TextRefinementService(config, device_manager)
        service.text_llm = self.mock_llm
        
        # Mock LLM response
        self.mock_llm.return_value = [{'generated_text': 'This is clean text.'}]
        
        result = service.refine_text("um this is uh messy text")
        self.assertEqual(result, "This is clean text.")
        
        # Verify LLM was called
        self.mock_llm.assert_called_once()
    
    def test_refine_text_fallback(self):
        """Test text refinement fallback to basic cleanup"""
        config = Config()
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        service = TextRefinementService(config, device_manager)
        service.text_llm = None  # No LLM available
        
        result = service.refine_text("um this is uh test text")
        expected = "this is test text"  # Basic cleanup removes filler words
        self.assertEqual(result, expected)


class TestTranscriptionService(BaseProsodyTest):
    """Tests for the TranscriptionService class"""
    
    def test_transcribe_no_model(self):
        """Test transcription when Whisper model is not loaded"""
        config = Config()
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        service = TranscriptionService(config, device_manager)
        service.whisper_model = None
        
        result = service.transcribe([])
        self.assertIsNone(result)
    
    def test_transcribe_no_data(self):
        """Test transcription with no audio data"""
        config = Config()
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        service = TranscriptionService(config, device_manager)
        service.whisper_model = self.mock_whisper_instance
        
        result = service.transcribe([])
        self.assertIsNone(result)
    
    def test_transcribe_success(self):
        """Test successful audio transcription"""
        config = Config()
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        service = TranscriptionService(config, device_manager)
        service.whisper_model = self.mock_whisper_instance
        
        audio_data = [np.array([0.1, 0.2, 0.3], dtype=np.float32)]
        
        # Mock whisper transcription
        mock_segment = MagicMock()
        mock_segment.text = "Hello world"
        self.mock_whisper_instance.transcribe.return_value = ([mock_segment], None)
        
        result = service.transcribe(audio_data)
        self.assertEqual(result, "Hello world")


class TestHotkeyListener(BaseProsodyTest):
    """Test hotkey handling functionality"""
    
    def test_hotkey_matching_ctrl_l(self):
        """Test ctrl_l hotkey matching"""
        config = Config(hotkey="ctrl_l")
        ui = ConsoleUI()
        listener = HotkeyListener(config, ui)
        
        # Mock callbacks
        mock_start = MagicMock()
        mock_stop = MagicMock()
        listener.set_callbacks(mock_start, mock_stop)
        
        # Mock key object
        from pynput.keyboard import Key
        with patch('prosody.Key', Key):
            # Simulate double-tap
            listener.on_hotkey_press(Key.ctrl_l)
            listener.last_hotkey_time = time.time() - 0.1  # Within threshold
            listener.on_hotkey_press(Key.ctrl_l)
            
            mock_start.assert_called_once()
    
    def test_push_to_talk_press(self):
        """Test push-to-talk key press"""
        config = Config(hotkey="ctrl_l", push_to_talk=True)
        ui = ConsoleUI()
        listener = HotkeyListener(config, ui)
        
        mock_start = MagicMock()
        mock_stop = MagicMock()
        listener.set_callbacks(mock_start, mock_stop)
        
        from pynput.keyboard import Key
        with patch('prosody.Key', Key):
            listener.on_hotkey_press(Key.ctrl_l)
            mock_start.assert_called_once()
    
    def test_push_to_talk_release(self):
        """Test push-to-talk key release"""
        config = Config(hotkey="ctrl_l", push_to_talk=True)
        ui = ConsoleUI()
        listener = HotkeyListener(config, ui)
        listener.key_pressed = True
        
        mock_start = MagicMock()
        mock_stop = MagicMock()
        listener.set_callbacks(mock_start, mock_stop)
        
        from pynput.keyboard import Key
        with patch('prosody.Key', Key):
            listener.on_hotkey_release(Key.ctrl_l)
            # Wait for timer to execute
            time.sleep(0.2)
            mock_stop.assert_called_once()
    
    def test_hotkey_match_function(self):
        """Test hotkey matching function"""
        config = Config(hotkey="f12")
        ui = ConsoleUI()
        listener = HotkeyListener(config, ui)
        
        from pynput.keyboard import Key
        with patch('prosody.Key', Key):
            self.assertTrue(listener._is_hotkey_match(Key.f12))
            self.assertFalse(listener._is_hotkey_match(Key.ctrl_l))


class TestAudioRecorder(BaseProsodyTest):
    """Test audio recording functionality"""
    
    def test_audio_callback_recording(self):
        """Test audio callback when recording"""
        config = Config()
        state = DictationState()
        ui = ConsoleUI()
        recorder = AudioRecorder(config, state, ui)
        
        state.is_recording = True
        test_audio = np.array([0.1, 0.2, 0.3])
        
        with patch.object(recorder.audio_queue, 'put') as mock_put:
            recorder.audio_callback(test_audio, None, None, None)
            mock_put.assert_called_once()
    
    def test_audio_callback_not_recording(self):
        """Test audio callback when not recording"""
        config = Config()
        state = DictationState()
        ui = ConsoleUI()
        recorder = AudioRecorder(config, state, ui)
        
        state.is_recording = False
        test_audio = np.array([0.1, 0.2, 0.3])
        
        with patch.object(recorder.audio_queue, 'put') as mock_put:
            recorder.audio_callback(test_audio, None, None, None)
            mock_put.assert_not_called()
    
    def test_start_recording(self):
        """Test starting audio recording"""
        config = Config()
        state = DictationState()
        ui = ConsoleUI()
        recorder = AudioRecorder(config, state, ui)
        
        with patch('prosody.threading.Thread') as mock_thread:
            recorder.start_recording()
            
            self.assertTrue(state.is_recording)
            self.mock_sd.InputStream.assert_called_once()
    
    def test_stop_recording(self):
        """Test stopping audio recording"""
        config = Config()
        state = DictationState()
        ui = ConsoleUI()
        recorder = AudioRecorder(config, state, ui)
        
        state.is_recording = True
        
        # Mock stream and thread
        mock_stream = MagicMock()
        mock_thread = MagicMock()
        recorder.stream = mock_stream
        recorder.processing_thread = mock_thread
        
        recorder.stop_recording()
        
        self.assertFalse(state.is_recording)
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()
        mock_thread.join.assert_called_once()
    
    def test_list_audio_devices(self):
        """Test listing audio devices"""
        config = Config()
        state = DictationState()
        ui = ConsoleUI()
        recorder = AudioRecorder(config, state, ui)
        
        with patch('builtins.print') as mock_print:
            recorder.list_audio_devices()
            mock_print.assert_called()
            # Should show available devices
            calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("Test Mic" in call for call in calls))


class TestPermissionManager(BaseProsodyTest):
    """Test permission checking functionality"""
    
    def test_check_microphone_permission_success(self):
        """Test successful microphone permission check"""
        ui = ConsoleUI()
        permission_manager = PermissionManager(ui)
        
        # Mock successful permission check
        self.mock_sd.InputStream.return_value.__enter__ = MagicMock()
        self.mock_sd.InputStream.return_value.__exit__ = MagicMock()
        
        result = permission_manager.check_microphone_permission()
        self.assertTrue(result)
    
    def test_check_microphone_permission_failure(self):
        """Test failed microphone permission check"""
        ui = ConsoleUI()
        permission_manager = PermissionManager(ui)
        
        # Mock failed permission check
        self.mock_sd.InputStream.side_effect = Exception("Permission denied")
        
        result = permission_manager.check_microphone_permission()
        self.assertFalse(result)
    
    def test_check_accessibility_permission_success(self):
        """Test successful accessibility permission check"""
        ui = ConsoleUI()
        permission_manager = PermissionManager(ui)
        
        # Mock successful accessibility check
        mock_controller = MagicMock()
        self.mock_keyboard.return_value = mock_controller
        
        result = permission_manager.check_accessibility_permission()
        self.assertTrue(result)
        mock_controller.press.assert_called_with('f13')
        mock_controller.release.assert_called_with('f13')
    
    def test_check_accessibility_permission_failure(self):
        """Test failed accessibility permission check"""
        ui = ConsoleUI()
        permission_manager = PermissionManager(ui)
        
        # Mock failed accessibility check
        mock_controller = MagicMock()
        mock_controller.press.side_effect = Exception("Permission denied")
        self.mock_keyboard.return_value = mock_controller
        
        result = permission_manager.check_accessibility_permission()
        self.assertFalse(result)
    
    def test_check_essential_permissions_macos(self):
        """Test essential permissions check on macOS"""
        ui = ConsoleUI()
        permission_manager = PermissionManager(ui)
        
        with patch.object(permission_manager, 'check_microphone_permission', return_value=True):
            result = permission_manager.check_essential_permissions()
            self.assertTrue(result)
    
    def test_check_essential_permissions_non_macos(self):
        """Test essential permissions check on non-macOS"""
        ui = ConsoleUI()
        permission_manager = PermissionManager(ui)
        
        with patch('prosody.platform.system', return_value='Linux'):
            result = permission_manager.check_essential_permissions()
            self.assertTrue(result)


class TestTypingService(BaseProsodyTest):
    """Test text typing functionality"""
    
    def test_type_text_success(self):
        """Test successful text typing"""
        ui = ConsoleUI()
        typing_service = TypingService(ui)
        
        result = typing_service.type_text("Hello world")
        self.assertTrue(result)
        typing_service.keyboard_controller.type.assert_called_with("Hello world ")
    
    def test_type_text_failure(self):
        """Test text typing failure handling"""
        ui = ConsoleUI()
        typing_service = TypingService(ui)
        
        # Mock keyboard controller failure
        typing_service.keyboard_controller.type.side_effect = Exception("Permission denied")
        
        with patch('builtins.print') as mock_print:
            result = typing_service.type_text("test text")
            self.assertFalse(result)
            
            # Should print error message
            mock_print.assert_called()
            print_calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("Could not type text automatically" in call for call in print_calls))
    
    def test_type_empty_text(self):
        """Test typing empty text"""
        ui = ConsoleUI()
        typing_service = TypingService(ui)
        
        result = typing_service.type_text("")
        self.assertTrue(result)
        typing_service.keyboard_controller.type.assert_not_called()


class TestAppController(BaseProsodyTest):
    """Test the main AppController orchestrator"""
    
    def test_startup_sequence(self):
        """Test application startup sequence"""
        config = Config()
        ui = ConsoleUI()
        permission_manager = PermissionManager(ui)
        device_manager = DeviceManager(ui)
        state = DictationState()
        audio_recorder = AudioRecorder(config, state, ui)
        transcription_service = TranscriptionService(config, device_manager)
        text_refinement_service = TextRefinementService(config, device_manager)
        typing_service = TypingService(ui)
        hotkey_listener = HotkeyListener(config, ui)
        
        app_controller = AppController(
            config, ui, permission_manager, device_manager, audio_recorder,
            transcription_service, text_refinement_service, typing_service, hotkey_listener
        )
        
        with patch.object(permission_manager, 'check_essential_permissions', return_value=True):
            with patch.object(transcription_service, 'initialize', return_value=True):
                with patch.object(text_refinement_service, 'initialize', return_value=True):
                    result = app_controller.startup()
                    self.assertTrue(result)
    
    def test_process_dictation_workflow(self):
        """Test complete dictation processing workflow"""
        config = Config()
        ui = ConsoleUI()
        permission_manager = PermissionManager(ui)
        device_manager = DeviceManager(ui)
        state = DictationState()
        audio_recorder = AudioRecorder(config, state, ui)
        transcription_service = TranscriptionService(config, device_manager)
        text_refinement_service = TextRefinementService(config, device_manager)
        typing_service = TypingService(ui)
        hotkey_listener = HotkeyListener(config, ui)
        
        app_controller = AppController(
            config, ui, permission_manager, device_manager, audio_recorder,
            transcription_service, text_refinement_service, typing_service, hotkey_listener
        )
        
        # Setup test data
        state.audio_data = [np.array([0.1, 0.2, 0.3], dtype=np.float32)]
        
        with patch.object(transcription_service, 'transcribe', return_value="Hello world"):
            with patch.object(text_refinement_service, 'refine_text', return_value="Hello world."):
                with patch.object(typing_service, 'type_text', return_value=True) as mock_type:
                    app_controller._process_dictation()
                    mock_type.assert_called_once_with("Hello world.")
    
    def test_process_dictation_no_speech(self):
        """Test dictation processing with no speech detected"""
        config = Config()
        ui = ConsoleUI()
        permission_manager = PermissionManager(ui)
        device_manager = DeviceManager(ui)
        state = DictationState()
        audio_recorder = AudioRecorder(config, state, ui)
        transcription_service = TranscriptionService(config, device_manager)
        text_refinement_service = TextRefinementService(config, device_manager)
        typing_service = TypingService(ui)
        hotkey_listener = HotkeyListener(config, ui)
        
        app_controller = AppController(
            config, ui, permission_manager, device_manager, audio_recorder,
            transcription_service, text_refinement_service, typing_service, hotkey_listener
        )
        
        # Setup test data
        state.audio_data = [np.array([0.1, 0.2, 0.3], dtype=np.float32)]
        
        with patch.object(transcription_service, 'transcribe', return_value=None):
            with patch.object(ui, 'show_no_speech_detected') as mock_no_speech:
                app_controller._process_dictation()
                mock_no_speech.assert_called_once()


class TestCreateApp(BaseProsodyTest):
    """Test the application factory function"""
    
    def test_create_app_with_defaults(self):
        """Test creating app with default configuration"""
        config = Config()
        app = create_app(config)
        
        self.assertIsInstance(app, AppController)
        self.assertEqual(app.config, config)
        self.assertIsInstance(app.ui, ConsoleUI)
        self.assertIsInstance(app.permission_manager, PermissionManager)
        self.assertIsInstance(app.device_manager, DeviceManager)
        self.assertIsInstance(app.audio_recorder, AudioRecorder)
        self.assertIsInstance(app.transcription_service, TranscriptionService)
        self.assertIsInstance(app.text_refinement_service, TextRefinementService)
        self.assertIsInstance(app.typing_service, TypingService)
        self.assertIsInstance(app.hotkey_listener, HotkeyListener)
    
    def test_create_app_with_custom_config(self):
        """Test creating app with custom configuration"""
        config = Config(hotkey="f12", push_to_talk=True, debug=True)
        app = create_app(config)
        
        self.assertIsInstance(app, AppController)
        self.assertEqual(app.config.hotkey, "f12")
        self.assertTrue(app.config.push_to_talk)
        self.assertTrue(app.config.debug)
    
    def test_create_app_state_consistency(self):
        """Test that AppController and AudioRecorder share the same state object"""
        config = Config()
        app = create_app(config)
        
        # The AppController and AudioRecorder should share the same state object
        self.assertIs(app.state, app.audio_recorder.state)
        
        # Test that audio data put into AudioRecorder state is visible to AppController
        test_audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        app.audio_recorder.state.audio_data.append(test_audio)
        
        # AppController should see the same audio data
        self.assertEqual(len(app.state.audio_data), 1)
        np.testing.assert_array_equal(app.state.audio_data[0], test_audio)


class TestErrorHandling(BaseProsodyTest):
    """Test error handling and edge cases"""
    
    def test_transcription_with_malformed_audio(self):
        """Test transcription with malformed audio data"""
        config = Config()
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        service = TranscriptionService(config, device_manager)
        service.whisper_model = self.mock_whisper_instance
        
        # Malformed audio data
        audio_data = [np.array([np.inf, np.nan, 1.0])]
        
        # Should handle gracefully
        result = service.transcribe(audio_data)
        # The method should still attempt transcription
        self.mock_whisper_instance.transcribe.assert_called_once()
    
    def test_llm_unexpected_response(self):
        """Test LLM handling with unexpected response format"""
        config = Config()
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        service = TextRefinementService(config, device_manager)
        service.text_llm = self.mock_llm
        
        # Mock unexpected response format
        self.mock_llm.side_effect = Exception("Model error")
        
        with patch.object(service, '_basic_text_cleanup', return_value="fallback") as mock_fallback:
            result = service.refine_text("test text")
            mock_fallback.assert_called_once_with("test text")
    
    def test_audio_recorder_initialization_failure(self):
        """Test audio recorder handling initialization failure"""
        config = Config()
        state = DictationState()
        ui = ConsoleUI()
        recorder = AudioRecorder(config, state, ui)
        
        # Mock stream creation failure
        self.mock_sd.InputStream.side_effect = Exception("Audio device error")
        
        # Should handle gracefully and not crash
        recorder.start_recording()
        self.assertFalse(state.is_recording)
    
    def test_service_initialization_failure(self):
        """Test service initialization failure handling"""
        config = Config()
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        
        # Mock whisper model loading failure
        self.mock_whisper.side_effect = Exception("Model loading failed")
        
        transcription_service = TranscriptionService(config, device_manager)
        
        with self.assertRaises(Exception):
            transcription_service.initialize()


if __name__ == '__main__':
    unittest.main(verbosity=2)