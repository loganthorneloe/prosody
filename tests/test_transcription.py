"""Tests for the transcription module."""

import unittest
import numpy as np
import os
from unittest.mock import Mock, patch, MagicMock
from src.prosody.transcription import Transcriber


class TestTranscriber(unittest.TestCase):
    """Test cases for Transcriber class."""

    @patch("whisper.load_model")
    def setUp(self, mock_load_model):
        """Set up test fixtures."""
        # Create a mock model
        self.mock_model = Mock()
        mock_load_model.return_value = self.mock_model

        # Create transcriber instance
        self.transcriber = Transcriber(model_name="base.en")

    def test_initialization(self):
        """Test Transcriber initialization."""
        self.assertEqual(self.transcriber.model_name, "base.en")
        self.assertIsNotNone(self.transcriber.model)

    @patch("whisper.load_model")
    def test_model_loading_error(self, mock_load_model):
        """Test handling of model loading errors."""
        mock_load_model.side_effect = Exception("Model not found")

        with self.assertRaises(RuntimeError) as context:
            Transcriber(model_name="invalid_model")

        self.assertIn("Failed to load Whisper model", str(context.exception))

    def test_transcribe_empty_audio(self):
        """Test transcribing empty audio data."""
        empty_audio = np.array([], dtype=np.float32)
        result = self.transcriber.transcribe(empty_audio)
        self.assertEqual(result, "")

    def test_transcribe_audio(self):
        """Test transcribing audio data."""
        # Create mock audio data
        audio_data = np.random.randn(16000).astype(np.float32) * 0.1

        # Mock the model's transcribe method
        self.mock_model.transcribe.return_value = {"text": " Hello, world! "}

        # Transcribe
        result = self.transcriber.transcribe(audio_data)

        # Verify
        self.assertEqual(result, "Hello, world!")
        self.mock_model.transcribe.assert_called_once()

        # Check that audio was passed with correct parameters
        call_args = self.mock_model.transcribe.call_args
        np.testing.assert_array_almost_equal(call_args[0][0], audio_data)
        self.assertEqual(call_args[1]["language"], "en")
        self.assertEqual(call_args[1]["fp16"], False)

    def test_transcribe_normalized_audio(self):
        """Test that audio is normalized if values exceed 1.0."""
        # Create audio data with values > 1.0
        audio_data = np.random.randn(16000).astype(np.float32) * 2.0

        self.mock_model.transcribe.return_value = {"text": "Test"}

        result = self.transcriber.transcribe(audio_data)

        # Verify audio was normalized
        call_args = self.mock_model.transcribe.call_args
        normalized_audio = call_args[0][0]
        self.assertLessEqual(np.abs(normalized_audio).max(), 1.0)

    def test_transcribe_error_handling(self):
        """Test error handling during transcription."""
        audio_data = np.random.randn(16000).astype(np.float32)

        # Mock transcribe to raise an exception
        self.mock_model.transcribe.side_effect = Exception("Transcription failed")

        # Should return empty string on error
        result = self.transcriber.transcribe(audio_data)
        self.assertEqual(result, "")

    def test_get_available_models(self):
        """Test getting list of available models."""
        models = self.transcriber.get_available_models()

        # Check that common models are included
        self.assertIn("base.en", models)
        self.assertIn("small", models)
        self.assertIn("medium", models)
        self.assertIn("large", models)

    def test_get_model_info(self):
        """Test getting model information."""
        info = self.transcriber.get_model_info()

        self.assertEqual(info["name"], "base.en")
        self.assertTrue(info["loaded"])
        self.assertFalse(info["multilingual"])

    @patch("whisper.load_model")
    def test_get_model_info_not_loaded(self, mock_load_model):
        """Test getting model info when model is not loaded."""
        transcriber = Transcriber.__new__(Transcriber)
        transcriber.model_name = "test_model"
        transcriber.model = None

        info = transcriber.get_model_info()

        self.assertEqual(info["name"], "test_model")
        self.assertFalse(info["loaded"])

    def test_different_language(self):
        """Test transcribing with a different language."""
        audio_data = np.random.randn(16000).astype(np.float32)

        self.mock_model.transcribe.return_value = {"text": "Bonjour"}

        result = self.transcriber.transcribe(audio_data, language="fr")

        # Verify language parameter was passed
        call_args = self.mock_model.transcribe.call_args
        self.assertEqual(call_args[1]["language"], "fr")


if __name__ == "__main__":
    unittest.main()
