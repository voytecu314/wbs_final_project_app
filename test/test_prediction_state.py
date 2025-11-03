"""Simple tests for PredictionState - no mocks, just basic functionality."""

from hand_signs_recognition.prediction_state import PredictionState


def test_initial_prediction_is_no_hand_detected():
    """Test that new state starts with 'No hand detected'."""
    state = PredictionState()
    assert state.get_prediction() == "No hand detected"


def test_can_set_and_get_prediction():
    """Test setting and getting a prediction."""
    state = PredictionState()
    state.set_prediction("Hammer")
    assert state.get_prediction() == "Hammer"


def test_prediction_can_be_changed():
    """Test that prediction can be updated."""
    state = PredictionState()
    state.set_prediction("Hammer")
    assert state.get_prediction() == "Hammer"

    state.set_prediction("Lehrer")
    assert state.get_prediction() == "Lehrer"


def test_frame_count_starts_at_zero():
    """Test that frame count initializes to 0."""
    state = PredictionState()
    assert state.frame_count == 0


def test_should_predict_increments_frame_count():
    """Test that calling should_predict increments frame count."""
    state = PredictionState()
    state.should_predict()
    assert state.frame_count == 1

    state.should_predict()
    assert state.frame_count == 2


def test_should_predict_returns_true_every_5th_frame():
    """Test that prediction happens every 5th frame by default."""
    state = PredictionState()

    # Frames 1-4: should be False
    assert state.should_predict() == False  # frame 1
    assert state.should_predict() == False  # frame 2
    assert state.should_predict() == False  # frame 3
    assert state.should_predict() == False  # frame 4

    # Frame 5: should be True
    assert state.should_predict() == True  # frame 5

    # Frames 6-9: should be False again
    assert state.should_predict() == False  # frame 6
    assert state.should_predict() == False  # frame 7
    assert state.should_predict() == False  # frame 8
    assert state.should_predict() == False  # frame 9

    # Frame 10: should be True
    assert state.should_predict() == True  # frame 10


def test_should_predict_with_custom_skip_frames():
    """Test should_predict with different skip_frames values."""
    state = PredictionState()

    # With skip_frames=3
    assert state.should_predict(skip_frames=3) == False  # frame 1
    assert state.should_predict(skip_frames=3) == False  # frame 2
    assert state.should_predict(skip_frames=3) == True  # frame 3
    assert state.should_predict(skip_frames=3) == False  # frame 4
    assert state.should_predict(skip_frames=3) == False  # frame 5
    assert state.should_predict(skip_frames=3) == True  # frame 6
