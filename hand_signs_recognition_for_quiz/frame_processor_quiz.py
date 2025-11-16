import av
import cv2
import numpy as np


def create_frame_callback(config, prediction_state, correct_class):
    """
    Factory function that creates a video frame callback.

    Args:
        config: MediaPipeConfig instance with model and hands detector
        prediction_state: PredictionState instance for storing results
        correct_class: REQUIRED: The DGS class ID (string) expected for this challenge.

    Returns:
        Callback function for processing video frames
    """
    # Sicherstellen, dass die erwartete Klasse als Integer vorliegt
    try:
        expected_class_id = int(correct_class)
    except ValueError:
        print(f"ERROR: Invalid correct_class ID: {correct_class}")
        expected_class_id = -1  # Setze auf ungültige ID

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
            x_min_global = 1.0
            y_min_global = 1.0

            for hand_landmarks in results.multi_hand_landmarks:
                for lm in hand_landmarks.landmark:
                    x_min_global = min(x_min_global, lm.x)
                    y_min_global = min(y_min_global, lm.y)

            # 2. Iteriere über die Hände (bis zu 2)
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                if hand_idx >= 2:  # Max. 2 Hände verwenden
                    break

                # Sammle normalisierte Daten für die aktuelle Hand
                for lm in hand_landmarks.landmark:
                    # Normalisierung relativ zum Frame (oder zum Min-Punkt aller Hände)
                    data_aux.append(lm.x - x_min_global)
                    data_aux.append(lm.y - y_min_global)

                    # Fülle x_ und y_ nur für die erste Hand (hand_idx == 0)
                    # für die Textposition
                    if hand_idx == 0:
                        x_.append(lm.x)
                        y_.append(lm.y)

            # 3. Padding für Einhänder: Fülle den Vektor auf 84 Features auf
            if len(data_aux) < config.EXPECTED_LENGTH:
                # Füge 0en für die fehlende zweite Hand hinzu
                data_aux += [0.0] * (config.EXPECTED_LENGTH - len(data_aux))

            # 4. Trunkierung (Sicherheitsmechanismus, sollte nicht nötig sein
            # bei max_num_hands=2)
            elif len(data_aux) > config.EXPECTED_LENGTH:
                data_aux = data_aux[: config.EXPECTED_LENGTH]

            # Only run prediction every N frames
            if prediction_state.should_predict(
                skip_frames=10
            ):  # <--- WIEDER EINGEFÜGT!
                try:
                    # Make prediction with probability
                    prediction = config.model.predict([np.asarray(data_aux)])
                    prediction_proba = config.model.predict_proba(
                        [np.asarray(data_aux)]
                    )

                    predicted_class = int(prediction[0])
                    confidence = max(prediction_proba[0])  # Highest probability

                    # --- ZENTRALE KORREKTUR FÜR DGS-CHALLENGE (Unverändert) ---
                    if confidence >= 0.3 and predicted_class == expected_class_id:
                        predicted_character = (
                            f"{config.labels_dict[predicted_class]} ✅ "
                            f"({confidence:.2f})"
                        )
                        prediction_state.set_prediction(predicted_character)
                        prediction_state.increase_prediction_strength(confidence)
                    elif confidence >= 0.3:
                        predicted_character = (
                            f"{config.labels_dict[predicted_class]} ❌ "
                            and f"({confidence:.2f})"
                        )
                        prediction_state.set_prediction(predicted_character)
                        prediction_state.decrease_prediction_strength()
                    else:
                        predicted_character = "Unknown gesture"
                        prediction_state.set_prediction(predicted_character)
                        prediction_state.decrease_prediction_strength()
                    # -----------------------------------------------

                except Exception as e:
                    print(f"Prediction error: {e}")
                    prediction_state.set_prediction("Error")

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
            prediction_state.decrease_prediction_strength()  # Stärke senken

        # Convert back to BGR for encoding/display
        out_bgr = cv2.cvtColor(img_rgb_draw, cv2.COLOR_RGB2BGR)

        return av.VideoFrame.from_ndarray(out_bgr, format="bgr24")

    return callback
