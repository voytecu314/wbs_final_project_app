import pickle

import mediapipe as mp


class MediaPipeConfig:
    """Configuration and initialization for MediaPipe hands detection."""

    def __init__(self):
        """Initialize MediaPipe components and configuration."""
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        # Drawing styles (optional, available in newer mediapipe versions)
        try:
            self.mp_styles = mp.solutions.drawing_styles
        except Exception:
            self.mp_styles = None

        # Initialize hands detector
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,  # False for video streaming
            max_num_hands=2,  # Limit to 2 hands
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # Model configuration
        self.EXPECTED_LENGTH = 84
        self.labels_dict = {0: "Hammer", 1: "Lehrer", 2: "Lehrnen", 3: "Schule"}

        # Load ML model
        self.model = self._load_model()

    def _load_model(self):
        """Load the trained model from pickle file."""
        model_dict = pickle.load(
            open("hand_signs_recognition/hand_signs_model.p", "rb")
        )
        return model_dict["model"]
