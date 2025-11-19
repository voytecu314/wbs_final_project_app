import av
import cv2
import numpy as np


def create_frame_callback(config, prediction_state, correct_class):
    """
    Frame-Callback für die DGS-Quiz-Challenge.

    Wichtig:
    - Nutzt EXAKT die gleiche Feature-Pipeline wie hand_signs_recognition_for_rag/frame_processor.py
      (damit das Modell die gleichen Inputs bekommt wie im Learn-Chat-Bot).
    - Ergänzt nur:
        * expected_class_id (korrekte DGS-Klasse für diese Challenge)
        * PredictionStateQuiz mit increase/decrease_prediction_strength
    """

    # Erwartete Klasse als int parsen (z.B. "6" für Hammer)
    try:
        expected_class_id = int(correct_class)
    except ValueError:
        print(f"ERROR: Invalid correct_class ID: {correct_class}")
        expected_class_id = -1  # nie erfüllt, aber Callback läuft weiter

    def callback(frame: av.VideoFrame) -> av.VideoFrame:
        try:
            # 1. Frame nach BGR konvertieren
            img_bgr = frame.to_ndarray(format="bgr24")

            # 2. BGR -> RGB + Spiegelung (IDENTISCH zum RAG-Processor)
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            img_rgb = cv2.flip(img_rgb, 1)

            # 3. Hände erkennen
            results = config.hands.process(img_rgb)

            # 4. Kopie zum Zeichnen
            img_rgb_draw = img_rgb.copy()
            h, w, _ = img_rgb_draw.shape

            if results.multi_hand_landmarks:
                # --- IDENTISCH zur RAG-Version: Feature-Vektor bauen ---
                data_aux = []
                x_ = []
                y_ = []

                # Erster Durchgang: alle x/y-Koordinaten sammeln
                for hand_landmarks in results.multi_hand_landmarks:
                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        x_.append(x)
                        y_.append(y)

                # Zweiter Durchgang: normalisieren relativ zu min(x_), min(y_)
                if x_ and y_:
                    x_min = min(x_)
                    y_min = min(y_)
                else:
                    x_min, y_min = 0.0, 0.0

                for hand_landmarks in results.multi_hand_landmarks:
                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        data_aux.append(x - x_min)
                        data_aux.append(y - y_min)
                # ------------------------------------------------------

                # Landmarks zeichnen (wie im RAG-Processor)
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
                            img_rgb_draw,
                            hand_landmarks,
                            config.mp_hands.HAND_CONNECTIONS,
                        )

                # Nur alle N Frames vorhersagen (wie beim Kollegen)
                if prediction_state.should_predict(skip_frames=10):
                    # Padding/Trunkierung auf EXPECTED_LENGTH (84)
                    if len(data_aux) < config.EXPECTED_LENGTH:
                        data_aux += [0.0] * (config.EXPECTED_LENGTH - len(data_aux))
                    elif len(data_aux) > config.EXPECTED_LENGTH:
                        data_aux = data_aux[: config.EXPECTED_LENGTH]

                    try:
                        x_input = np.asarray(data_aux, dtype=float).reshape(1, -1)

                        # Vorhersage mit demselben Modell wie im Learn-Chat-Bot
                        prediction = config.model.predict(x_input)
                        prediction_proba = config.model.predict_proba(x_input)

                        predicted_class = int(prediction[0])
                        confidence = float(np.max(prediction_proba[0]))

                        # --- DGS-CHALLENGE-LOGIK ---
                        if confidence >= 0.3 and predicted_class == expected_class_id:
                            # Richtige Gebärde
                            predicted_character = (
                                f"{config.labels_dict[predicted_class]} ✅ "
                                f"({confidence:.2f})"
                            )
                            prediction_state.set_prediction(predicted_character)
                            prediction_state.increase_prediction_strength(confidence)

                        elif confidence >= 0.3:
                            # Falsche, aber relativ sichere Gebärde
                            predicted_character = (
                                f"{config.labels_dict[predicted_class]} ❌ "
                                f"({confidence:.2f})"
                            )
                            prediction_state.set_prediction(predicted_character)
                            prediction_state.decrease_prediction_strength()

                        else:
                            # Unsichere oder unbekannte Gebärde
                            prediction_state.set_prediction("Unbekannte Geste")
                            prediction_state.decrease_prediction_strength()
                        # ---------------------------

                    except Exception as e:
                        print(f"Prediction error: {e}")
                        prediction_state.set_prediction("ML Error")
                        prediction_state.decrease_prediction_strength()

                # Text in Bild zeichnen (wie im RAG-Processor, nur mit unserem prediction_state)
                current_prediction = prediction_state.get_prediction()
                if x_ and y_:
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
                # Keine Hand erkannt
                prediction_state.set_prediction("Keine Hand erkannt")
                prediction_state.decrease_prediction_strength()

            # zurück zu BGR für die Ausgabe
            out_bgr = cv2.cvtColor(img_rgb_draw, cv2.COLOR_RGB2BGR)
            return av.VideoFrame.from_ndarray(out_bgr, format="bgr24")

        except Exception as e:
            # Im Fehlerfall den Stream nicht killen, sondern Frame unverändert zurückgeben
            print(f"FATAL error in frame callback: {e}")
            return frame

    return callback
