"""
Simple tests for frame_processor - just basic checks.
Note: These tests require actual MediaPipe and model to work.
"""

from hand_signs_recognition.frame_processor import create_frame_callback
from hand_signs_recognition.mediapipe_config import MediaPipeConfig
from hand_signs_recognition.prediction_state import PredictionState


def test_create_frame_callback_returns_function():
    """Test that create_frame_callback returns a callable function."""
    config = MediaPipeConfig()
    state = PredictionState()

    callback = create_frame_callback(config, state)

    assert callable(callback)


def test_callback_function_exists():
    """Test that we can create a callback without errors."""
    config = MediaPipeConfig()
    state = PredictionState()

    # Should not raise any exception
    callback = create_frame_callback(config, state)
    assert callback is not None
