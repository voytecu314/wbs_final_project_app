"""
Services package for hand sign recognition.

Contains:
- mediapipe_config: MediaPipe setup and model loading
- prediction_state: Thread-safe prediction state management
- frame_processor: Video frame processing callback
"""

from .frame_processor import create_frame_callback
from .mediapipe_config import MediaPipeConfig
from .prediction_state import PredictionState

__all__ = ["MediaPipeConfig", "PredictionState", "create_frame_callback"]
