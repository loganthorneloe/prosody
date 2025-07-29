"""Speech transcription using OpenAI's Whisper model."""

import os
import numpy as np
import whisper
from typing import Optional
import warnings

# Suppress warnings from whisper
warnings.filterwarnings("ignore", category=UserWarning)


class Transcriber:
    """Handles speech-to-text transcription using Whisper."""
    
    def __init__(self, model_name: str = "base.en"):
        """Initialize the transcriber with a Whisper model.
        
        Args:
            model_name: Name of the Whisper model to use (default "base.en")
                       Options: tiny, base, small, medium, large
                       Add .en suffix for English-only models (faster)
        """
        self.model_name = model_name
        self.model: Optional[whisper.Whisper] = None
        self._load_model()
        
    def _load_model(self):
        """Load the Whisper model."""
        try:
            print(f"Loading Whisper model '{self.model_name}'...")
            self.model = whisper.load_model(self.model_name)
            print(f"Model loaded successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}")
    
    def transcribe(self, audio_data: np.ndarray, language: str = "en") -> str:
        """Transcribe audio data to text.
        
        Args:
            audio_data: NumPy array containing audio samples (float32)
            language: Language code for transcription (default "en")
            
        Returns:
            Transcribed text string
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
            
        if len(audio_data) == 0:
            return ""
        
        try:
            # Ensure audio is float32 and in the correct range
            audio_data = audio_data.astype(np.float32)
            
            # Normalize audio if needed
            if np.abs(audio_data).max() > 1.0:
                audio_data = audio_data / np.abs(audio_data).max()
            
            # Transcribe the audio
            result = self.model.transcribe(
                audio_data,
                language=language,
                fp16=False,  # Use FP32 for better CPU compatibility
                verbose=False
            )
            
            # Extract and clean the text
            text = result["text"].strip()
            return text
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def get_available_models(self) -> list:
        """Get list of available Whisper models.
        
        Returns:
            List of model names
        """
        return [
            "tiny.en", "tiny",
            "base.en", "base",
            "small.en", "small",
            "medium.en", "medium",
            "large"
        ]
    
    def get_model_info(self) -> dict:
        """Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        if self.model is None:
            return {"name": self.model_name, "loaded": False}
            
        return {
            "name": self.model_name,
            "loaded": True,
            "multilingual": not self.model_name.endswith(".en"),
            "n_text_ctx": getattr(self.model, "n_text_ctx", "unknown"),
        }