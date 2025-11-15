import random
import time

import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from hand_signs_recognition_for_quiz.frame_processor import create_frame_callback
from hand_signs_recognition_for_quiz.mediapipe_config import MediaPipeConfig
from hand_signs_recognition_for_quiz.prediction_state import PredictionState

from .sub_components.highscore_redis import main as highscores
from st_components import translate

quiz_classes = ["6","12","11","28","14"]
pics_names = [
    "089hammer",
    "schwei_automat",
    "204schrauben",
    "217spiralbohrer",
    "Maulschluessel1"
    ]

def render_quiz_hand_signs():
    """Main Streamlit UI for hand signs recognition."""

    st.html("""
            <style> 

                h1, .stMarkdown p { text-align: center; }
                img { border-radius: 20%; }
                iframe { margin-top: 20% !important; }

            </style>
        """)

    @st.dialog("Provide your nickname")
    def register_nickname():
        nickname = st.text_input("Type your nickname here:")
        language = st.selectbox("Select your spoken language:", ["English", "German"])
        if st.button("Submit"):
            if nickname.strip() == "":
                st.warning("Nickname cannot be empty.")
                return
            else:
                st.session_state.nickname = nickname
                st.session_state.language = language
                st.rerun()

    if "nickname" not in st.session_state:
        register_nickname()

    else:

        # Header
        st.markdown(
            f"Hello, **{st.session_state.nickname}**! Welcome to the Hand Signs Quiz."
            if 
            st.session_state.language == "English"
            else 
            f"Hallo, **{st.session_state.nickname}**! Willkommen zum Handzeichen-Quiz."
        )
        st.title(
            "Use hand signs for this quiz."
            if 
            st.session_state.language == "English"
            else
            "Verwende Handzeichen für dieses Quiz."
            )

        # Load MediaPipe config and model (cached)
        @st.cache_resource
        def load_config():
            return MediaPipeConfig()

        config = load_config()
        if "correct_class_index" not in st.session_state:
            st.session_state.correct_class_index = random.randint(0, len(quiz_classes)-1)
        if "correct_class" not in st.session_state:
            st.session_state.correct_class = quiz_classes[st.session_state.correct_class_index]
        if "points" not in st.session_state:
            st.session_state.points = 0

        # Initialize prediction state in session
        if "prediction_state" not in st.session_state:
            st.session_state.prediction_state = PredictionState()

        prediction_state = st.session_state.prediction_state

        quiz_container, cam_webrtc = st.columns([1, 1], vertical_alignment="top")

        # Create callback function
        callback = create_frame_callback(config, prediction_state, st.session_state.correct_class)
        
        # WebRTC Streamer
        with cam_webrtc:
            webrtc_ctx = webrtc_streamer(
                key="mediapipe-hands-landmarks",
                mode=WebRtcMode.SENDRECV,
                video_frame_callback=callback,
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,
            )

        # Display current prediction with live updates
        with quiz_container:
            st.markdown(translate("### What is this tool?", "### Was ist dieses Werkzeug?"))
            st.markdown(
                f"""![Alt Text](https://fachgebaerdenlexikon.de/fileadmin/_migrated/pics/{pics_names[st.session_state.correct_class_index]}.jpg)"""
            )
            prediction_placeholder = st.empty()
            progress = st.empty()
            progress.progress(0)
            prediction_weight = 0
        # Update display while streaming
        if webrtc_ctx.state.playing:
            while webrtc_ctx.state.playing:
                current_strength = prediction_state.get_prediction_strength()
                bar_percent = current_strength if .05 < current_strength <= 1 else 0
                progress.progress(bar_percent)
                prediction_weight = bar_percent if bar_percent == 0 else round(sum(prediction_state.predictions_weights))
                prediction_placeholder.markdown(
                    f"{translate('Gaining points', 'Neue Punkte')}: {prediction_weight}"
                )
                if current_strength >= 1:
                    st.session_state.points += prediction_weight
                    prediction_state.set_prediction_strength(-1)
                    succes_msg = st.empty()
                    score_msg = st.empty()
                    succes_msg.success(config.labels_dict[int(st.session_state.correct_class)] + translate(f" is correct!, You gained {prediction_weight} extra points!", " ist korrekt!, Du hast gewonnen") + f" {prediction_weight} Punkte!")
                    score_msg.markdown(f"#### {translate('Current Score', 'Aktueller Punktestand')}:  {st.session_state.points}")
                    st.session_state.correct_class_index = (st.session_state.correct_class_index + random.randint(1, len(quiz_classes)-1)) % len(quiz_classes)
                    st.session_state.correct_class = quiz_classes[st.session_state.correct_class_index]
                    time.sleep(2)
                    succes_msg.empty()
                    st.rerun()
                time.sleep(0.5)  # Small delay to avoid overwhelming the UI
        else:
            prediction_placeholder.markdown(
                translate(
                    "### Press START to turn on the camera", 
                    "### Drücke START, um die Kamera einzuschalten"
                    )
            )

        highscores()
