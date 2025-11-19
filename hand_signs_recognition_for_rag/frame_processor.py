import av
import cv2
import numpy as np


def create_frame_callback(config, prediction_state):
    """
    Factory function that creates a video frame callback.

    Args:
        config: MediaPipeConfig instance with model and hands detector
        prediction_state: PredictionState instance for storing results

    Returns:
        Callback function for processing video frames
    """

    def callback(frame: av.VideoFrame) -> av.VideoFrame:
        """
        Video frame callback runs in the webrtc thread/process.
        Processes each frame to detect hands and make predictions.
        """
        # Convert incoming frame to numpy BGR image
        img_bgr = frame.to_ndarray(format="bgr24")

        # Prepare RGB image for MediaPipe (it expects RGB)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        # Flip the frame horizontally for a mirror effect
        img_rgb = cv2.flip(img_rgb, 1)
        # Process the frame to find hands
        results = config.hands.process(img_rgb)

        # Draw landmarks on a copy of the RGB image
        img_rgb_draw = img_rgb.copy()

        if results.multi_hand_landmarks:
            # Initialize data collection arrays
            data_aux = []
            x_ = []
            y_ = []

            # First pass: collect all x and y coordinates from ALL hands
            for hand_landmarks in results.multi_hand_landmarks:
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)

            # Second pass: normalize and build data_aux from ALL hands
            for hand_landmarks in results.multi_hand_landmarks:
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))

            # Draw landmarks on each hand
            for hand_landmarks in results.multi_hand_landmarks:
                if config.mp_styles is not None:
                    config.mp_drawing.draw_landmarks(
                        img_rgb_draw,
                        hand_landmarks,
                        config.mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=config.mp_styles.get_default_hand_landmarks_style(),
                        connection_drawing_spec=config.mp_styles.get_default_hand_connections_style(),
                    )
                else:
                    config.mp_drawing.draw_landmarks(
                        img_rgb_draw, hand_landmarks, config.mp_hands.HAND_CONNECTIONS
                    )

            # Only run prediction every N frames
            if prediction_state.should_predict(skip_frames=10):
                # Pad or truncate data_aux
                if len(data_aux) < config.EXPECTED_LENGTH:
                    data_aux += [0] * (config.EXPECTED_LENGTH - len(data_aux))
                elif len(data_aux) > config.EXPECTED_LENGTH:
                    data_aux = data_aux[: config.EXPECTED_LENGTH]

                try:
                    # Make prediction with probability
                    prediction = config.model.predict([np.asarray(data_aux)])
                    prediction_proba = config.model.predict_proba(
                        [np.asarray(data_aux)]
                    )

                    predicted_class = int(prediction[0])
                    confidence = max(prediction_proba[0])  # Highest probability

                    # Only accept if confidence is high enough
                    if confidence < 0.1:  # Adjust threshold (0.1 = 10% confidence)
                        predicted_character = "Unknown gesture"
                    elif predicted_class in config.labels_dict:
                        predicted_character = f"{config.labels_dict[predicted_class]}"
                    else:
                        predicted_character = f"Unknown class: {predicted_class}"

                    prediction_state.set_prediction(predicted_character)
                except Exception as e:
                    print(f"Prediction error: {e}")
                    prediction_state.set_prediction("Error")

            # Get current prediction to display
            current_prediction = prediction_state.get_prediction()

            # Draw prediction near the hand
            h, w, _ = img_rgb_draw.shape
            if x_ and y_:  # Make sure we have coordinates
                xmin = int(max(0, min(x_) * w))
                ymin = int(max(0, min(y_) * h))

                cv2.putText(
                    img_rgb_draw,
                    current_prediction,
                    (xmin, max(10, ymin - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )
        else:
            # No hand detected
            prediction_state.set_prediction("No hand detected")

        # Convert back to BGR for encoding/display
        out_bgr = cv2.cvtColor(img_rgb_draw, cv2.COLOR_RGB2BGR)

        return av.VideoFrame.from_ndarray(out_bgr, format="bgr24")

    return callback
