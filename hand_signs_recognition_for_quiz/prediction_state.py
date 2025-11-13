import threading


class PredictionState:
    """Thread-safe storage for prediction results."""

    def __init__(self):
        self.lock = threading.Lock()
        self.prediction = "No hand detected"
        self.prediction_strength = 0.0
        self.predictions_weights = []
        self.previous_landmarks = 84 * [0.0] # hardcoded config.EXPECTED_LENGTH
        self.last_prediction_time = 0
        self.frame_count = 0

    def set_prediction(self, value):
        """Set the current prediction value (thread-safe)."""
        with self.lock:
            self.prediction = value

    def get_prediction(self):
        """Get the current prediction value (thread-safe)."""
        with self.lock:
            return self.prediction

    def set_prediction_strength(self, value):
        """Set the current prediction strength (thread-safe)."""
        with self.lock:
            if value < 0:
                self.prediction_strength = 0
                self.predictions_weights = []
            elif 0 <= value <= .1:
                new_strength = self.prediction_strength - .05
                if new_strength < 0:
                    self.prediction_strength = 0
                else:
                    self.prediction_strength = new_strength
            else:
                if 0 <= self.prediction_strength < .3:
                    new_strength = self.prediction_strength + .02
                elif .3 <= self.prediction_strength < .6:
                    new_strength = self.prediction_strength + .05
                else:
                    new_strength = self.prediction_strength + .1
                if new_strength > 1:
                    self.prediction_strength = 1
                else:
                    self.prediction_strength = new_strength
            "skip" if value < 0 else self.predictions_weights.append(value)

    def get_prediction_strength(self):
        """Get the current prediction strength (thread-safe)."""
        with self.lock:
            return self.prediction_strength

    def set_previous_landmarks(self, landmarks):
        """Set the previous landmarks (thread-safe)."""
        with self.lock:
            self.previous_landmarks = landmarks

    def get_previous_landmarks(self):
        """Get the previous landmarks (thread-safe)."""
        with self.lock:
            return self.previous_landmarks

    def should_predict(self, skip_frames=5):
        """
        Only predict every N frames to reduce CPU load.

        Args:
            skip_frames: Number of frames to skip between predictions

        Returns:
            True if prediction should run on this frame
        """
        with self.lock:
            self.frame_count += 1
            if self.frame_count % skip_frames == 0:
                print("Predicting on this frame.", self.frame_count)
                return True
            return False
