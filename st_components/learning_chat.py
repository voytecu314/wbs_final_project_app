import time
from collections import Counter

import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from hand_signs_recognition_for_rag.frame_processor import create_frame_callback
from hand_signs_recognition_for_rag.mediapipe_config import MediaPipeConfig
from hand_signs_recognition_for_rag.prediction_state import PredictionState

from st_components.sub_components.rag import render_rag_chat

from streamlit_tile import streamlit_tile

# Question database
QUESTIONS_DB = {
    "Zange": [
        "Welche Zangenarten gibt es in der Metallbearbeitung?",
        "Wann benutze ich eine Kombizange statt einer Spitzzange?",
        "Wie pflege ich Zangen richtig?",
        "Was ist der Unterschied zwischen Seitenschneider und Kneifzange?",
        "Welche Sicherheitsregeln gelten beim Arbeiten mit Zangen?",
        "Wie erkenne ich, ob eine Zange beschädigt ist?"
    ],
    "Lehrer": [
        "Welche Aufgaben hat mein Ausbilder im Betrieb?",
        "Was ist der Unterschied zwischen Ausbilder und Berufsschullehrer?",
        "Wie oft muss ich mit meinem Ausbilder sprechen?",
        "Welche Rechte und Pflichten hat mein Ausbilder?",
        "Was mache ich, wenn ich Probleme mit meinem Ausbilder habe?",
        "Wer bewertet meine praktischen Fertigkeiten?"
    ],
    "Lehrnen": [
        "Wie erstelle ich ein Berichtsheft richtig?",
        "Welche Lernmethoden helfen mir in der Ausbildung?",
        "Was muss ich für die Zwischenprüfung lernen?",
        "Wie bereite ich mich auf die Abschlussprüfung vor?",
        "Welche technischen Zeichnungen muss ich lesen können?",
        "Wo finde ich Lernmaterial für Metalltechnik?"
    ],
    "Schule": [
        "Welche Fächer habe ich in der Berufsschule?",
        "Wie oft muss ich zur Berufsschule gehen?",
        "Was lerne ich im Fach Fertigungstechnik?",
        "Wie funktioniert das duale Ausbildungssystem?",
        "Welche Noten zählen für meinen Abschluss?",
        "Was mache ich, wenn ich in der Berufsschule fehle?"
    ],
    "Anschmieren": [
        "Wofür brauche ich Anreißfarbe?",
        "Welche Farben werden zum Anreißen verwendet?",
        "Wie trage ich Tusche auf Metall auf?",
        "Was ist der Unterschied zwischen Tusche und Kreide?",
        "Auf welchen Materialien funktioniert Anreißfarbe?",
        "Wie entferne ich Anreißfarbe nach der Bearbeitung?"
    ],
    "Blech": [
        "Welche Blechstärken gibt es?",
        "Was bedeutet die Bezeichnung S235JR?",
        "Wie biege ich Blech ohne es zu beschädigen?",
        "Welche Werkzeuge brauche ich zur Blechbearbeitung?",
        "Was ist der Unterschied zwischen Fein- und Grobblech?",
        "Wie berechne ich die Biegelänge von Blech?"
    ],
    "Hammer": [
        "Welche Hammerarten gibt es in der Metallbearbeitung?",
        "Wann benutze ich einen Schonhammer?",
        "Wie halte ich einen Hammer richtig?",
        "Was ist der Unterschied zwischen Schlosser- und Vorschlaghammer?",
        "Welche Sicherheitsregeln gelten beim Hämmern?",
        "Wie pflege und warte ich einen Hammer?"
    ],
    "Hebelblechschere": [
        "Welche maximale Blechstärke kann ich schneiden?",
        "Wie stelle ich den Schnittwinkel richtig ein?",
        "Was muss ich bei der Sicherheit beachten?",
        "Wie verhindere ich Gratbildung beim Schneiden?",
        "Wann benutze ich eine Hebelblechschere statt einer Handschere?",
        "Wie warte und pflege ich die Hebelblechschere?"
    ],
    "Meißel": [
        "Welche Meißelarten gibt es?",
        "Wie halte ich einen Meißel beim Hämmern richtig?",
        "Welcher Schneidenwinkel ist für welches Material richtig?",
        "Wie schärfe ich einen stumpfen Meißel nach?",
        "Welche Schutzausrüstung brauche ich beim Meißeln?",
        "Was ist ein Kreuzmeißel und wofür wird er verwendet?"
    ],
    "Metall": [
        "Welche Metallarten werden in der Metalltechnik verwendet?",
        "Was ist der Unterschied zwischen Eisen und Stahl?",
        "Welche Eigenschaften hat Aluminium?",
        "Was bedeuten die Werkstoffnummern bei Metallen?",
        "Wie erkenne ich verschiedene Metalle?",
        "Welche Metalle rosten und welche nicht?"
    ],
    "Montieren": [
        "Was bedeutet Montage in der Metalltechnik?",
        "Welche Werkzeuge brauche ich für die Montage?",
        "Was ist eine Montagezeichnung?",
        "Wie lese ich einen Montageplan richtig?",
        "Welche Fügetechniken gibt es?",
        "Was muss ich bei der Reihenfolge der Montage beachten?"
    ],
    "Schrauben": [
        "Welche Schraubenarten gibt es?",
        "Was ist der Unterschied zwischen metrischen und Zoll-Gewinden?",
        "Wie bestimme ich die richtige Schraubengröße?",
        "Welche Festigkeitsklassen haben Schrauben?",
        "Wie funktioniert eine selbstsichernde Schraube?",
        "Was muss ich beim Anziehen von Schrauben beachten?"
    ],
    "Schweissautomat": [
        "Welche Schweißverfahren gibt es?",
        "Was ist der Unterschied zwischen MIG und MAG-Schweißen?",
        "Welche Schutzausrüstung brauche ich beim Schweißen?",
        "Wie stelle ich den Schweißstrom richtig ein?",
        "Was sind typische Schweißfehler und wie vermeide ich sie?",
        "Welche Nahtarten gibt es beim Schweißen?"
    ],
    "Sicherheit": [
        "Welche persönliche Schutzausrüstung (PSA) brauche ich?",
        "Was mache ich bei einem Arbeitsunfall?",
        "Welche Sicherheitszeichen muss ich kennen?",
        "Was ist der Unterschied zwischen Gefährdung und Risiko?",
        "Wie funktioniert eine Gefährdungsbeurteilung?",
        "Welche Erste-Hilfe-Maßnahmen sollte ich kennen?"
    ],
    "Schraubenschluessel": [
        "Welche Arten von Schraubenschlüsseln gibt es?",
        "Was ist der Unterschied zwischen Ring- und Maulschlüssel?",
        "Wie lese ich die Größenangabe auf einem Schraubenschlüssel?",
        "Wann benutze ich einen Drehmomentschlüssel?",
        "Was bedeutet die Norm DIN 3113?",
        "Wie verhindere ich das Abrutschen des Schraubenschlüssels?"
    ],
    "Koerner": [
        "Wofür wird ein Körner verwendet?",
        "Welche Körnerarten gibt es?",
        "Wie körne ich richtig an?",
        "Welcher Spitzenwinkel ist Standard beim Körner?",
        "Was ist der Unterschied zwischen Spitz- und Schlagkörner?",
        "Wie verhindere ich das Abrutschen beim Körnen?"
    ],
    "Maschinenschraubstock": [
        "Wie spanne ich ein Werkstück richtig ein?",
        "Was ist der Unterschied zwischen Maschinen- und Parallelschraubstock?",
        "Wie schütze ich das Werkstück vor Beschädigungen?",
        "Wie hoch darf das Werkstück aus dem Schraubstock ragen?",
        "Was muss ich bei der Wartung des Schraubstocks beachten?",
        "Welche Backenarten gibt es für Schraubstöcke?"
    ],
    "Drehmaschine": [
        "Welche Hauptbauteile hat eine Drehmaschine?",
        "Was ist der Unterschied zwischen Längs- und Plandrehen?",
        "Wie berechne ich die Schnittgeschwindigkeit?",
        "Welche Sicherheitsregeln gelten an der Drehmaschine?",
        "Was ist der Reitstock und wofür wird er verwendet?",
        "Wie wähle ich das richtige Drehwerkzeug aus?"
    ],
    "Gewindemeissel": [
        "Was ist der Unterschied zwischen Vor- und Nachschneider?",
        "Wie schneide ich ein Innengewinde richtig?",
        "Welches Kernlochmaß brauche ich für ein M8-Gewinde?",
        "Wie verhindere ich, dass der Gewindebohrer bricht?",
        "Welche Schneidöle verwende ich beim Gewindeschneiden?",
        "Wie erkenne ich metrische Gewindebohrer?"
    ],
    "Anreissplatte": [
        "Wofür wird eine Anreißplatte verwendet?",
        "Wie richte ich die Anreißplatte waagerecht aus?",
        "Was ist der Unterschied zwischen Guss- und Granit-Anreißplatte?",
        "Wie pflege ich die Anreißplatte richtig?",
        "Welches Zubehör gehört zur Anreißplatte?",
        "Wie genau ist eine Anreißplatte?"
    ],
    "Anreissnadel": [
        "Aus welchem Material ist eine Anreißnadel?",
        "Wie halte ich die Anreißnadel beim Anreißen?",
        "Was ist der Unterschied zwischen Anreißnadel und Reißnadel?",
        "Wie schärfe ich eine stumpfe Anreißnadel?",
        "Wann benutze ich einen Bleistift statt einer Anreißnadel?",
        "Wie vermeide ich Verletzungen durch die Anreißnadel?"
    ],
    "Bandsaege": [
        "Welche Sägebandarten gibt es?",
        "Wie stelle ich die Schnittgeschwindigkeit ein?",
        "Was bedeutet die Zahnteilung beim Sägeband?",
        "Welche Sicherheitseinrichtungen hat eine Bandsäge?",
        "Wie spanne ich ein neues Sägeband richtig?",
        "Was mache ich, wenn das Sägeband reißt?"
    ],
    "Bohrmaschine": [
        "Welche Bohrmaschinenarten gibt es?",
        "Wie spanne ich einen Bohrer richtig ein?",
        "Was ist der Unterschied zwischen Tisch- und Ständerbohrmaschine?",
        "Wie wähle ich die richtige Drehzahl beim Bohren?",
        "Welche Sicherheitsregeln gelten an der Bohrmaschine?",
        "Was ist ein Bohrmaschinenschraubstock?"
    ],
    "Drehmomentschlüssel": [
        "Wofür brauche ich einen Drehmomentschlüssel?",
        "Wie stelle ich das richtige Drehmoment ein?",
        "Was bedeutet die Einheit Nm (Newtonmeter)?",
        "Wie lagere ich einen Drehmomentschlüssel richtig?",
        "Wann muss ein Drehmomentschlüssel kalibriert werden?",
        "Was passiert, wenn ich zu fest anziehe?"
    ],
    "Feile": [
        "Welche Feilenhiebe gibt es?",
        "Was ist der Unterschied zwischen Schrupp- und Schlichtfeile?",
        "Wie feile ich richtig und effizient?",
        "Wie reinige ich eine zugesetzte Feile?",
        "Welche Feilenformen gibt es und wofür werden sie verwendet?",
        "Warum braucht eine Feile einen Feilenheft?"
    ],
    "Maulschlüssel": [
        "Was ist der Unterschied zwischen Maulschlüssel und Ringschlüssel?",
        "Warum ist das Maul meist um 15° abgewinkelt?",
        "Wie verhindere ich das Abrunden von Schraubenköpfen?",
        "Was bedeutet die Größenangabe SW13?",
        "Welche Norm gilt für Maulschlüssel?",
        "Wann benutze ich einen verstellbaren Schraubenschlüssel?"
    ],
    "Messschieber": [
        "Wie lese ich einen Messschieber richtig ab?",
        "Was ist der Nonius beim Messschieber?",
        "Welche Messgenauigkeit hat ein Messschieber?",
        "Wie messe ich Innendurchmesser mit dem Messschieber?",
        "Wie pflege ich einen Messschieber richtig?",
        "Was ist der Unterschied zwischen analog und digital?"
    ],
    "Saege": [
        "Welche Sägearten gibt es in der Metallbearbeitung?",
        "Wie wähle ich die richtige Zahnteilung?",
        "Wie säge ich mit einer Handbügelsäge richtig?",
        "Was bedeutet 'Zähne pro Zoll' bei Sägeblättern?",
        "Wie verhindere ich das Verklemmen des Sägeblatts?",
        "Welche Schnittgeschwindigkeit ist beim Sägen richtig?"
    ],
    "Spiralbohrer": [
        "Aus welchem Material sind Spiralbohrer?",
        "Wie wähle ich die richtige Drehzahl beim Bohren?",
        "Was bedeuten die Kennzeichnungen HSS und HSS-Co?",
        "Wie schleife ich einen stumpfen Spiralbohrer nach?",
        "Welche Kühlschmierstoffe verwende ich beim Bohren?",
        "Was ist der Unterschied zwischen Spiralbohrer Typ N, H und W?"
    ]
}


def render_learning_chat():
    """Main Streamlit UI for hand signs recognition."""

    # Header
    #st.title("MediaPipe Hands - Landmarks Overlay with Inference Classifier")
    
    # Load MediaPipe config and model (cached)
    @st.cache_resource
    def load_config():
        return MediaPipeConfig()

    config = load_config()

    # Initialize prediction state in session
    if "prediction_state" not in st.session_state:
        st.session_state.prediction_state = PredictionState()
    if 'prediction_history' not in st.session_state:
        st.session_state.prediction_history = []
    if 'stable_prediction' not in st.session_state:
        st.session_state.stable_prediction = "No hand detected"
    if 'chat_query' not in st.session_state:
        st.session_state.chat_query = None

    
    rag_bot = render_rag_chat() 
    # Show chatbot if a question was clicked
    if st.session_state.chat_query:
        st.markdown("---")
        st.markdown(f"### 💬 You asked: *{st.session_state.chat_query}*")
        
        # Your chatbot logic here
        # send question to chain to get answer
        answer = rag_bot.chat(st.session_state.chat_query)
        # extract answer from dictionary returned by chain
        response = answer.response
        st.write(response)
        st.session_state.chat_query = None  # Reset after displaying answer
        
        if st.button("🔙 Back to sign detection"):
            st.session_state.chat_query = None
            st.session_state.prediction_history = []
            st.rerun()

    st.markdown("---")    

    prediction_state = st.session_state.prediction_state

    # Create callback function
    callback = create_frame_callback(config, prediction_state)

    def get_stable_prediction(current_pred, history, window_size=10, threshold=0.6):
        """
        Stabilize prediction by requiring consistency over multiple frames
        """
        history.append(current_pred)
        if len(history) > window_size:
            history.pop(0)
        
        if len(history) >= window_size:
            # Get most common prediction in window
            counter = Counter(history)
            most_common, count = counter.most_common(1)[0]
            # Only update if it appears in threshold% of frames
            if count >= window_size * threshold:
                return most_common
        
        return st.session_state.stable_prediction
    

    right_col, left_col = st.columns([1, 1], vertical_alignment="center")
    with left_col:
        # WebRTC Streamer
        webrtc_ctx = webrtc_streamer(
            key="dgs-rec",
            mode=WebRtcMode.SENDRECV,
            video_frame_callback=callback,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
        
        if webrtc_ctx.state.playing:
            # Add a "Detect New Sign" button
            if st.button("🔄 Detect New Sign"):
                st.session_state.stable_prediction = "No hand detected"
                st.session_state.prediction_history = []
                st.rerun()

    # Display current prediction with live updates

    # Update display while streaming
    if webrtc_ctx.state.playing:
        # Get raw prediction from current frame
        current_pred = prediction_state.get_prediction()
        
        # Stabilize the prediction
        stable_pred = get_stable_prediction(
            current_pred, 
            st.session_state.prediction_history,
            window_size=10,
            threshold=0.6  # 40% consistency required
        )
        
        if stable_pred and stable_pred != st.session_state.stable_prediction:
            st.session_state.stable_prediction = stable_pred
            st.session_state.chat_query = None  # Reset chat when prediction changes
        
        # Show questions as buttons if we have a stable prediction
        if st.session_state.stable_prediction and st.session_state.stable_prediction in QUESTIONS_DB:
            #st.markdown("#### Ask me:")
            questions = QUESTIONS_DB[st.session_state.stable_prediction]
            
            # Display questions in rows of 2 columns
            with right_col:
                # Display current detection
                st.write(f"Detected Sign: **{st.session_state.stable_prediction or 'Waiting...'}**")
                for i in range(0, len(questions), 2):
                    cols = st.columns(2)
                    for idx, col in enumerate(cols):
                        question_idx = i + idx
                        if question_idx < len(questions):
                            with col:
                                if st.button(questions[question_idx], key=f"q_{question_idx}"):
                                    st.session_state.chat_query = questions[question_idx]
                                    # Stop the prediction loop to focus on chat
                                    st.session_state.prediction_history = []
                                    st.rerun()
                                    
        if st.session_state.stable_prediction=="No hand detected" or st.session_state.stable_prediction not in QUESTIONS_DB:
            time.sleep(0.1)
            st.rerun()
