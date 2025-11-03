"""
Simple tests for MediaPipeConfig - only basic checks.
Note: These tests require the actual model file to exist at 'st_components/model.p'
"""

from hand_signs_recognition.mediapipe_config import MediaPipeConfig


def test_expected_length_is_84():
    """Test that feature vector length is 84."""
    config = MediaPipeConfig()
    assert config.EXPECTED_LENGTH == 84


def test_mp_hands_is_initialized():
    """Test that MediaPipe hands module is loaded."""
    config = MediaPipeConfig()
    assert config.mp_hands is not None


def test_mp_drawing_is_initialized():
    """Test that MediaPipe drawing utils are loaded."""
    config = MediaPipeConfig()
    assert config.mp_drawing is not None


def test_hands_detector_is_created():
    """Test that hands detector object is created."""
    config = MediaPipeConfig()
    assert config.hands is not None


def test_model_is_loaded():
    """Test that ML model is loaded."""
    config = MediaPipeConfig()
    assert config.model is not None
