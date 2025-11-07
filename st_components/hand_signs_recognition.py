import time

import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from hand_signs_recognition.frame_processor import create_frame_callback
from hand_signs_recognition.mediapipe_config import MediaPipeConfig
from hand_signs_recognition.prediction_state import PredictionState


def render_hand_signs_recognition():
    """Main Streamlit UI for hand signs recognition."""

    # Header
    st.title("MediaPipe Hands - Landmarks Overlay with Inference Classifier")
    st.markdown(
        "This page overlays MediaPipe on each video frame and predicts the hand sign. "
        "Install the dependency with `pip install mediapipe` if you don't have it."
    )

    # Load MediaPipe config and model (cached)
    @st.cache_resource
    def load_config():
        return MediaPipeConfig()

    config = load_config()

    # Initialize prediction state in session
    if "prediction_state" not in st.session_state:
        st.session_state.prediction_state = PredictionState()

    prediction_state = st.session_state.prediction_state

    # Create callback function
    callback = create_frame_callback(config, prediction_state)

    # WebRTC Streamer
    webrtc_ctx = webrtc_streamer(
        key="mediapipe-hands-landmarks",
        mode=WebRtcMode.SENDRECV,
        video_frame_callback=callback,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    # Display current prediction with live updates
    st.markdown("---")
    prediction_placeholder = st.empty()

    # Update display while streaming
    if webrtc_ctx.state.playing:
        while webrtc_ctx.state.playing:
            current_pred = prediction_state.get_prediction()
            prediction_placeholder.markdown(
                f"### Current Prediction: **{current_pred}**"
            )
            time.sleep(0.1)  # Small delay to avoid overwhelming the UI
    else:
        prediction_placeholder.markdown(
            f"### Current Prediction: **{prediction_state.get_prediction()}**"
        )

    # Information notes
    st.markdown(
        "**Notes:**\n"
        "- Predictions are made every 5th frame (about 6 times per second at 30fps)\n"
        "- This reduces CPU load while maintaining responsive predictions\n"
        "- If still experiencing issues, increase `skip_frames` value to 10 or more\n"
        "- Real-time predictions are always visible on the video feed itself"
    )
