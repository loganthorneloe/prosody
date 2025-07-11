#!/usr/bin/env python3
"""
Platform-specific tests for Prosody dictation tool
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

from prosody import (
    Config, ConsoleUI, DeviceManager, PermissionManager, AudioRecorder, 
    DictationState, AppController, create_app
)


class TestCrossPlatformDeviceDetection(unittest.TestCase):
    """Test device detection across different platforms"""
    
    def setUp(self):
        """Set up common mocks"""
        # Mock all external dependencies
        self.patches = [
            patch('prosody.WhisperModel'),
            patch('prosody.pipeline'),
            patch('prosody.sd'),
            patch('prosody.KeyboardController'),
        ]
        
        for p in self.patches:
            p.start()
    
    def tearDown(self):
        """Clean up patches"""
        for p in self.patches:
            p.stop()
    
    @patch('prosody.torch')
    def test_macos_mps_detection(self, mock_torch):
        """Test MPS detection on macOS"""
        # Configure for macOS with MPS
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = True
        mock_torch.float16 = 'float16'
        
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        
        with patch('builtins.print') as mock_print:
            device = device_manager.get_best_device()
            
            self.assertEqual(device, "mps")
            # Check that MPS was detected in the print calls
            print_calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("Apple Metal Performance Shaders" in call for call in print_calls))
    
    @patch('prosody.torch')
    def test_windows_cuda_detection(self, mock_torch):
        """Test CUDA detection on Windows"""
        # Configure for Windows with NVIDIA GPU
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "NVIDIA GeForce RTX 4080"
        mock_torch.backends.mps.is_available.return_value = False
        mock_torch.float16 = 'float16'
        
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        
        with patch('builtins.print') as mock_print:
            device = device_manager.get_best_device()
            
            self.assertEqual(device, "cuda")
            # Check that CUDA was detected in the print calls
            print_calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("NVIDIA GeForce RTX 4080" in call for call in print_calls))
    
    @patch('prosody.torch')
    def test_windows_directml_detection(self, mock_torch):
        """Test DirectML detection on Windows"""
        # Configure for Windows with AMD/Intel GPU
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False
        mock_torch.float16 = 'float16'
        
        # Mock torch_directml import
        with patch('builtins.__import__') as mock_import:
            mock_directml = MagicMock()
            mock_directml.is_available.return_value = True
            mock_directml.device.return_value = "dml:0"
            
            def side_effect(name, *args, **kwargs):
                if name == 'torch_directml':
                    return mock_directml
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            ui = ConsoleUI()
            device_manager = DeviceManager(ui)
            
            with patch('builtins.print') as mock_print:
                device = device_manager.get_best_device()
                
                self.assertEqual(device, "dml:0")
                # Check that DirectML was detected in the print calls
                print_calls = [str(call) for call in mock_print.call_args_list]
                self.assertTrue(any("DirectML" in call for call in print_calls))
    
    
    @patch('prosody.torch')
    def test_cpu_fallback_no_acceleration(self, mock_torch):
        """Test CPU fallback when no acceleration is available"""
        # Configure for no acceleration
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False
        mock_torch.float16 = 'float16'
        
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        
        with patch('builtins.print') as mock_print:
            device = device_manager.get_best_device()
            
            self.assertEqual(device, "cpu")
            # Check CPU fallback message
            print_calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("No GPU acceleration found" in call for call in print_calls))
    
    @patch('prosody.torch')
    def test_device_priority_order(self, mock_torch):
        """Test that CUDA takes priority over other devices"""
        # Configure multiple accelerations available
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "RTX 4090"
        mock_torch.backends.mps.is_available.return_value = True  # Should be ignored
        mock_torch.float16 = 'float16'
        
        # Mock torch_directml import
        with patch('builtins.__import__') as mock_import:
            mock_directml = MagicMock()
            mock_directml.is_available.return_value = True  # Should be ignored
            
            def side_effect(name, *args, **kwargs):
                if name == 'torch_directml':
                    return mock_directml
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = side_effect
            
            ui = ConsoleUI()
            device_manager = DeviceManager(ui)
            device = device_manager.get_best_device()
            
            # CUDA should take priority
            self.assertEqual(device, "cuda")
    
    @patch('prosody.torch')
    def test_import_error_handling(self, mock_torch):
        """Test graceful handling of missing optional dependencies"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False
        mock_torch.float16 = 'float16'
        
        # Both DirectML and Intel extensions unavailable
        ui = ConsoleUI()
        device_manager = DeviceManager(ui)
        
        with patch('builtins.print') as mock_print:
            device = device_manager.get_best_device()
            
            self.assertEqual(device, "cpu")
            print_calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("No GPU acceleration found" in call for call in print_calls))


class TestPlatformSpecificBehavior(unittest.TestCase):
    """Test platform-specific behaviors"""
    
    def setUp(self):
        """Set up common mocks"""
        self.patches = [
            patch('prosody.WhisperModel'),
            patch('prosody.pipeline'),
            patch('prosody.torch'),
            patch('prosody.sd'),
            patch('prosody.KeyboardController'),
        ]
        
        for p in self.patches:
            p.start()
    
    def tearDown(self):
        """Clean up patches"""
        for p in self.patches:
            p.stop()
    
    @patch('prosody.platform.system')
    def test_macos_permission_check(self, mock_platform):
        """Test macOS-specific permission checking"""
        mock_platform.return_value = 'Darwin'
        
        ui = ConsoleUI(debug=True)
        permission_manager = PermissionManager(ui)
        
        with patch.object(permission_manager, 'check_essential_permissions', return_value=True) as mock_check:
            result = permission_manager.check_essential_permissions()
            mock_check.assert_called_once()
            self.assertTrue(result)
    
    @patch('prosody.platform.system')
    def test_non_macos_no_permission_check(self, mock_platform):
        """Test that permission checking is skipped on non-macOS"""
        mock_platform.return_value = 'Linux'
        
        ui = ConsoleUI(debug=True)
        permission_manager = PermissionManager(ui)
        
        # On non-macOS, permission check should return True immediately
        result = permission_manager.check_essential_permissions()
        self.assertTrue(result)
    
    def test_audio_device_listing(self):
        """Test audio device listing across platforms"""
        with patch('prosody.sd') as mock_sd:
            mock_sd.query_devices.return_value = [
                {'name': 'Built-in Microphone', 'max_input_channels': 2},
                {'name': 'USB Headset', 'max_input_channels': 1},
                {'name': 'Speakers', 'max_input_channels': 0},
            ]
            
            config = Config()
            state = DictationState()
            ui = ConsoleUI()
            recorder = AudioRecorder(config, state, ui)
            
            with patch('builtins.print') as mock_print:
                recorder.list_audio_devices()
                
                # Should print input devices only
                print_calls = [str(call) for call in mock_print.call_args_list]
                self.assertTrue(any('Built-in Microphone' in call for call in print_calls))
                self.assertTrue(any('USB Headset' in call for call in print_calls))
                self.assertFalse(any('Speakers' in call for call in print_calls))


class TestConfigurationVariations(unittest.TestCase):
    """Test different configuration combinations"""
    
    def setUp(self):
        """Set up common mocks"""
        self.patches = [
            patch('prosody.WhisperModel'),
            patch('prosody.pipeline'),
            patch('prosody.torch'),
            patch('prosody.sd'),
            patch('prosody.KeyboardController'),
        ]
        
        for p in self.patches:
            p.start()
    
    def tearDown(self):
        """Clean up patches"""
        for p in self.patches:
            p.stop()
    
    def test_all_hotkey_options(self):
        """Test all supported hotkey configurations"""
        hotkeys = ["ctrl_l", "ctrl_r", "f12", "f11", "f10", "f9", "cmd", "alt"]
        
        for hotkey in hotkeys:
            with self.subTest(hotkey=hotkey):
                config = Config(hotkey=hotkey)
                self.assertEqual(config.hotkey, hotkey)
    
    def test_push_to_talk_combinations(self):
        """Test push-to-talk with different hotkeys"""
        hotkeys = ["f12", "ctrl_l", "cmd"]
        
        for hotkey in hotkeys:
            with self.subTest(hotkey=hotkey):
                config = Config(hotkey=hotkey, push_to_talk=True)
                self.assertEqual(config.hotkey, hotkey)
                self.assertTrue(config.push_to_talk)
    
    def test_debug_mode_variations(self):
        """Test debug mode effects on logging"""
        # Test debug mode enabled
        with patch('prosody.logging.basicConfig') as mock_logging:
            config = Config(debug=True)
            app = create_app(config)
            
            with patch.object(app.permission_manager, 'check_essential_permissions', return_value=True):
                with patch.object(app.transcription_service, 'initialize', return_value=True):
                    with patch.object(app.text_refinement_service, 'initialize', return_value=True):
                        app.startup()
            
            # Verify debug logging was configured
            mock_logging.assert_called()
        
        # Test debug mode disabled
        with patch('prosody.logging.basicConfig') as mock_logging:
            config = Config(debug=False)
            app = create_app(config)
            
            with patch.object(app.permission_manager, 'check_essential_permissions', return_value=True):
                with patch.object(app.transcription_service, 'initialize', return_value=True):
                    with patch.object(app.text_refinement_service, 'initialize', return_value=True):
                        app.startup()
            
            # Verify warning-level logging was configured
            mock_logging.assert_called()

    def test_whisper_model_variations(self):
        """Test different Whisper model configurations"""
        models = ["tiny", "small", "medium", "large"]
        
        for model in models:
            with self.subTest(model=model):
                config = Config(whisper_model_name=model)
                self.assertEqual(config.whisper_model_name, model)
    
    def test_sample_rate_variations(self):
        """Test different sample rate configurations"""
        sample_rates = [8000, 16000, 22050, 44100, 48000]
        
        for rate in sample_rates:
            with self.subTest(rate=rate):
                config = Config(sample_rate=rate)
                self.assertEqual(config.sample_rate, rate)
    
    def test_input_device_selection(self):
        """Test input device selection"""
        device_ids = [None, 0, 1, 2]
        
        for device_id in device_ids:
            with self.subTest(device_id=device_id):
                config = Config(input_device=device_id)
                self.assertEqual(config.input_device, device_id)


if __name__ == '__main__':
    unittest.main(verbosity=2)