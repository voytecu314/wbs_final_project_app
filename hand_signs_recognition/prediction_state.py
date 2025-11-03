import threading


class PredictionState:
    """Thread-safe storage for prediction results."""

    def __init__(self):
        self.lock = threading.Lock()
        self.prediction = "No hand detected"
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
