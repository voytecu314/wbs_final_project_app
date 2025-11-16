import streamlit as st
import random
import time
import pandas as pd
import pickle
import mediapipe as mp
import numpy as np

from streamlit_webrtc import WebRtcMode, webrtc_streamer
# KORREKTUR: Import der umbenannten Datei mit korrekter Signatur
from hand_signs_recognition_for_quiz.frame_processor_quiz import create_frame_callback 
from hand_signs_recognition_for_quiz.mediapipe_config import MediaPipeConfig
from hand_signs_recognition_for_quiz.prediction_state import PredictionState
# -------------------------------------------------------------


# --- 1. MEDIA PIPE KONFIGURATION (KORRIGIERT UND INTEGRIERT) ---
class MediaPipeConfig:
    """Configuration and initialization for MediaPipe hands detection."""

    def __init__(self):
        """Initialize MediaPipe components and configuration."""
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils 
        try:
            self.mp_styles = mp.solutions.drawing_styles
        except Exception:
            self.mp_styles = None

        # Initialize hands detector
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # Labels und Modell
        self.EXPECTED_LENGTH = 84
        # Vollständige DGS-Liste des Kollegen
        self.labels_dict = {
            0: "Zange", 1: "Lehrer", 2: "Lehrnen", 3: "Schule",
            4: "Anschmieren", 5: "Blech", 6: "Hammer", 7: "Hebelblechschere",
            8: "Meißel", 9: "Metall", 10: "Montieren", 11: "Schrauben",
            12: "Schweissautomat", 13: "Sicherheit", 14: "Schraubenschlüssel",
            15: "Körner", 16: "Maschinenschraubstock", 17: "Drehmaschine",
            18: "Gewindemeissel", 19: "Anreissplatte", 20: "Anreissnadel",
            21: "Bandsaege", 22: "Bohrmaschine", 23: "Drehmomentschlüssel",
            24: "Feile", 25: "Maulschlüssel", 26: "Messschieber",
            27: "Saege", 28: "Spiralbohrer",
        }
        self.model = self._load_model()

    def _load_model(self):
        """Load the trained model from pickle file."""
        # ANMERKUNG: Hier wird der Pfad zur ML-Modelldatei angenommen
        model_dict = pickle.load(
            open("hand_signs_recognition/hand_signs_model.p", "rb")
        )
        return model_dict["model"]


# --- 2. HILFSFUNKTIONEN UND KONSTANTEN ---

def toggle_language():
    """Schaltet die Sprache im Session State um."""
    if "language" not in st.session_state:
        st.session_state.language = "German" # Standard
        return
    
    if st.session_state.language == "German":
        st.session_state.language = "English"
    else:
        st.session_state.language = "German"

def translate(english_text, german_text):
    """Simple translation function based on session state."""
    # Wenn 'language' nicht gesetzt ist oder 'German' ist, gib Deutsch zurück (Standard)
    if st.session_state.get("language") == "German":
        return german_text
    # Ansonsten (wenn 'English' gesetzt ist), gib Englisch zurück
    return english_text

@st.cache_resource
def load_config():
    """Lädt die MediaPipe Config einmalig."""
    return MediaPipeConfig()


config = load_config()

# Zuordnung von Gebärdenname zur ML-Klasse (ID) für die DGS-Challenge
QUIZ_DGS_CLASSES = {
    "ANREISSNADEL": "20",
    "FEILE": "24",
    "KÖRNER": "15",
    "SPIRALBOHRER": "28",
    "BOHRMASCHINE": "22",
    "MESSCHIEBER": "26",
    "SCHRAUBENSCHLÜSSEL": "14",
    "SCHRAUBEN": "11",
    "SCHWEISSAUTOMAT": "12",
    "MAULSCHLÜSSEL": "25",
    "SICHERHEIT": "13",
}

# --- Lernfeld-Namen für die Überschrift ---
LF_NAMES = {
    1: "Bauelemente mit handgeführten Werkzeugen fertigen",
    2: "Bauelemente mit Maschinen fertigen",
    3: "Baugruppen herstellen und montieren",
    4: "Technische Systeme instand halten",
}
# ------------------------------------------

def get_image_url(keyword):
    """Gibt den lokalen Dateipfad für das situationsgerechte Bild zurück."""
    urls = {
        "ANREISSNADEL": "images/anreissnadel.jpeg",
        "FEILE": "images/feile.jpeg",
        "KÖRNER": "images/koerner.jpg",
        "SPIRALBOHRER": "images/spiralbohrer.jpeg",
        "BOHRMASCHINE": "images/bohrmaschine.jpg",
        "MESSCHIEBER": "images/messschieber.jpg",
        "SCHRAUBENSCHLÜSSEL": "images/schraubenschluessel.jpg",
        "SCHRAUBEN": "images/schrauben.jpg",
        "SCHWEISSAUTOMAT": "images/schweissautomat.jpeg",
        "MAULSCHLÜSSEL": "images/maulschluessel.jpg",
        "SICHERHEIT": "images/sicherheit.jpg",
    }
    return urls.get(keyword, None)


def init_quiz_state(username="Azubi"):
    """Initialisiert den Zustand des Quiz (Punkte, Index) und der DGS-Erkennung."""
    if "quiz_index" not in st.session_state:
        st.session_state.quiz_index = 0
    if "prediction_state" not in st.session_state:
        st.session_state.prediction_state = PredictionState()
    if "dgs_challenge_passed" not in st.session_state:
        st.session_state.dgs_challenge_passed = False
    if "mc_result" not in st.session_state: # ZUSTAND der letzten MC-Frage (CORRECT/INCORRECT)
        st.session_state.mc_result = None
    if "quiz_xp" not in st.session_state:
        st.session_state.quiz_xp = 0
    if "username" not in st.session_state:
        st.session_state.username = username
    # Initialisierung der Statistik-Tabelle für die Highscore-Page
    if "stats_data" not in st.session_state:
        st.session_state.stats_data = {
            "LF 1 XP": 0, "LF 2 XP": 0, "LF 3 XP": 0, "LF 4 XP": 0,
            "Gesamt-XP": 0, "Fehler in LF": {},
        }


def update_stats(lf_num, points_gained, error=False):
    """Aktualisiert die Statistiken und XP des Lernenden."""
    lf_key = f"LF {lf_num} XP"
    
    # Update XP
    st.session_state.stats_data[lf_key] = (
        st.session_state.stats_data.get(lf_key, 0) + points_gained
    )
    st.session_state.stats_data["Gesamt-XP"] += points_gained
    st.session_state.quiz_xp += points_gained

    # Update Fehler
    if error:
        lf_error_key = f"LF {lf_num}"
        st.session_state.stats_data["Fehler in LF"][lf_error_key] = (
            st.session_state.stats_data["Fehler in LF"].get(lf_error_key, 0) + 1
        )

# --- KORRIGIERTER check_answer BLOCK ---
def check_answer(question_type, user_input, expected_answer, current_lf, gebärde_thema, dgs_passed=False):
    """Überprüft die Antwort und aktualisiert Score/Stats/XP."""
    
    points = 20 # XP pro Block
    
    if question_type in ["A_TOOL", "B_HANDLUNG"]:
        if user_input == expected_answer:
            update_stats(current_lf, points)
            st.session_state.mc_result = "CORRECT" # Flag ist gesetzt!
            st.success(f"🎉 Richtig! Du hast das Werkzeug **{expected_answer}** richtig gewählt und {points} XP verdient.")
            
        else:
            # FALSCH: 0 XP, aber aktive Korrektur durch DGS-Challenge
            update_stats(current_lf, 0, error=True)
            st.session_state.mc_result = "INCORRECT" # Flag ist gesetzt!
            
            # Textanpassung:
            st.error(f"❌ Das war leider die falsche Antwort. Richtig wäre **{expected_answer}** gewesen.")
            
        # NEU: Index muss um 1 erhöht werden, um zum DGS-Block zu springen
        st.session_state.quiz_index += 1 # <-- WICHTIGE ZEILE HINZUGEFÜGT
        
        st.session_state.dgs_challenge_passed = False 
        time.sleep(1) 
        st.rerun() 
        
    elif question_type == "C_DGS":
        if dgs_passed:
            # DGS erfolgreich oder übersprungen (dgs_passed kommt vom Nächste-Frage-Button/Skip-Button)
            
            # Index-Erhöhung: Springe zur nächsten Hauptfrage (da MC+DGS-Block abgeschlossen)
            st.session_state.quiz_index += 1

            # 2. Feedback
            if st.session_state.mc_result == "CORRECT":
                st.success(f"🤟 DGS erkannt! Weiter zur nächsten Frage.")
            else:
                st.success(f"🤟 Korrektur erfolgreich! Weiter zur nächsten Frage.")
                
            # 3. Aufräumen des Zustands und XP-Vergabe
            st.session_state.dgs_challenge_passed = False # Zustand für nächste Challenge zurücksetzen
            st.session_state.mc_result = None # Reset
            # XP-Vergabe für die DGS-Challenge (z.B. 20 XP)
            update_stats(current_lf, 20) 
            
            time.sleep(1)
            st.rerun()
# --- ENDE KORRIGIERTER check_answer BLOCK ---

# --- 3. QUIZ DATENSTRUKTUR (24 BLÖCKE / 120 XP pro LF) ---

# 24 Blöcke (12 MC + 12 DGS)

QUIZ_DATA = [

    # --- LF 1: Bauelemente mit handgeführten Werkzeugen fertigen (120 CP) ---

    # 1. Block: Anreißen (A_TOOL) -> Gebärde (ANREISSNADEL)

    {

        "lf": 1, "scenario": (

            "Ein Azubi soll auf einem Metallblech eine Schnittlinie vorzeichnen. "

            "Er braucht ein präzises, spitzes Werkzeug."

        ),

        "question": "Welches Werkzeug wird zum Anreißen verwendet?",

        "type": "A_TOOL",

        "options": ["Messschieber", "Anreißnadel", "Körner", "Bleistift"],

        "answer": "Anreißnadel",

        "gebärde_thema": "ANREISSNADEL",

    },

    {

        "lf": 1, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: ANREISSNADEL",

        "type": "C_DGS", "expected_gebärde": "ANREISSNADEL",
        "gebärde_thema": "ANREISSNADEL", # Hinzugefügt

    },

    # 2. Block: Feilen (B_HANDLUNG) -> Gebärde (FEILE)

    {

        "lf": 1, "scenario": (

            "Das Werkstück ist geschnitten, aber die Oberfläche ist rau und die "

            "Kanten sind scharf. Es muss fertig bearbeitet werden."

        ),

        "question": "Welche Tätigkeit ist nötig, um die Oberfläche zu glätten?",

        "type": "B_HANDLUNG",

        "options": [

            "Feilen", "Schweißen", "Fräsen", "Hämmern"

        ],

        "answer": "Feilen",

        "gebärde_thema": "FEILE",

    },

    {

        "lf": 1, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: FEILE",

        "type": "C_DGS", "expected_gebärde": "FEILE",
        "gebärde_thema": "FEILE", # Hinzugefügt

    },

    # 3. Block: Körnen (A_TOOL) -> Gebärde (KÖRNER)

    {

        "lf": 1, "scenario": (

            "Bevor gebohrt wird, muss der Mittelpunkt des Loches gesichert "

            "werden, damit der Bohrer nicht verrutscht."

        ),

        "question": "Welches Werkzeugpaar wird zum Körnen benötigt?",

        "type": "A_TOOL",

        "options": [

            "Zange und Schraubstock", "Feile und Messschieber",

            "Körner und Hammer", "Meißel und Feile"

        ],

        "answer": "Körner und Hammer",

        "gebärde_thema": "KÖRNER",

    },

    {

        "lf": 1, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: KÖRNER",

        "type": "C_DGS", "expected_gebärde": "KÖRNER",
        "gebärde_thema": "KÖRNER", # Hinzugefügt

    },

    # 4. Block: Messen (B_HANDLUNG) -> Gebärde (MESSCHIEBER)

    {

        "lf": 1, "scenario": (

            "Die Länge des Werkstücks muss auf 100,5 mm genau überprüft "

            "werden, um die Qualität zu sichern."

        ),

        "question": "Welches Messinstrument ist für diese Genauigkeit ideal?",

        "type": "A_TOOL",

        "options": [

            "Lineal", "Messschieber", "Maßband", "Gliedermaßstab"

        ],

        "answer": "Messschieber",

        "gebärde_thema": "MESSCHIEBER",

    },

    {

        "lf": 1, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: MESSCHIEBER",

        "type": "C_DGS", "expected_gebärde": "MESSCHIEBER",
        "gebärde_thema": "MESSCHIEBER", # Hinzugefügt

    },

    

    # --- LF 2: Bauelemente mit Maschinen fertigen (120 CP) ---

    # 5. Block: Bohren/Werkzeug (A_TOOL) -> Gebärde (SPIRALBOHRER)

    {

        "lf": 2, "scenario": (

            "Ein Loch mit 8 mm Durchmesser soll in Stahl gebohrt werden. "

            "Der Azubi steht an der Standbohrmaschine."

        ),

        "question": "Welcher Bohrer-Typ wird standardmäßig verwendet?",

        "type": "A_TOOL",

        "options": [

            "Gewindebohrer", "Spiralbohrer", "Zapfensenker", "Stufenbohrer"

        ],

        "answer": "Spiralbohrer",

        "gebärde_thema": "SPIRALBOHRER",

    },

    {

        "lf": 2, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: SPIRALBOHRER",

        "type": "C_DGS", "expected_gebärde": "SPIRALBOHRER",
        "gebärde_thema": "SPIRALBOHRER", # Hinzugefügt

    },

    # 6. Block: Bohren/Handlung (B_HANDLUNG) -> Gebärde (BOHRMASCHINE)

    {

        "lf": 2, "scenario": (

            "Die Bohrmaschine ist eingeschaltet. Das Werkstück ist fest im "

            "Maschinenschraubstock gespannt."

        ),

        "question": "Was ist vor dem eigentlichen Bohren noch einzustellen?",

        "type": "B_HANDLUNG",

        "options": [

            "Die Vorschubgeschwindigkeit", "Die Drehzahl", 

            "Das Licht im Raum", "Die Werkstückposition"

        ],

        "answer": "Die Drehzahl",

        "gebärde_thema": "BOHRMASCHINE",

    },

    {

        "lf": 2, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: BOHRMASCHINE",

        "type": "C_DGS", "expected_gebärde": "BOHRMASCHINE",
        "gebärde_thema": "BOHRMASCHINE", # Hinzugefügt

    },

    # 7. Block: Messen (A_TOOL) -> Gebärde (MESSCHIEBER)

    {

        "lf": 2, "scenario": (

            "Nach dem Bohren muss der Durchmesser des Loches geprüft werden, "

            "um Passgenauigkeit sicherzustellen."

        ),

        "question": "Welches Messgerät ist zur Innenmessung geeignet?",

        "type": "A_TOOL",

        "options": [

            "Mikrometer", "Messschieber", "Endmaß", "Tiefenmaß"

        ],

        "answer": "Messschieber",

        "gebärde_thema": "MESSCHIEBER",

    },

    {

        "lf": 2, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: MESSCHIEBER",

        "type": "C_DGS", "expected_gebärde": "MESSCHIEBER",
        "gebärde_thema": "MESSCHIEBER", # Hinzugefügt

    },

    # 8. Block: Bohren/Handlung (B_HANDLUNG) -> Gebärde (SPIRALBOHRER)

    {

        "lf": 2, "scenario": (

            "Während des Bohrens entsteht viel Wärme und Reibung. Der Bohrer "

            "könnte stumpf werden."

        ),

        "question": "Was wird verwendet, um den Bohrer zu kühlen und zu schmieren?",

        "type": "B_HANDLUNG",

        "options": [

            "Wasser", "Kühlschmiermittel", "Speiseöl", "Druckluft"

        ],

        "answer": "Kühlschmiermittel",

        "gebärde_thema": "SPIRALBOHRER",

    },

    {

        "lf": 2, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: SPIRALBOHRER",

        "type": "C_DGS", "expected_gebärde": "SPIRALBOHRER",
        "gebärde_thema": "SPIRALBOHRER", # Hinzugefügt

    },

    

    # --- LF 3: Baugruppen herstellen und montieren (120 CP) ---

    # 9. Block: Montieren (A_TOOL) -> Gebärde (SCHRAUBENSCHLÜSSEL)

    {

        "lf": 3, "scenario": (

            "Zwei Teile müssen mit einer Sechskantmutter fest verschraubt "

            "werden. Es ist ein bestimmtes Drehmoment einzuhalten."

        ),

        "question": "Welches Werkzeug ist zum genauen Festziehen nötig?",

        "type": "A_TOOL",

        "options": [

            "Hammer", "Maulschlüssel", "Drehmomentschlüssel", "Zange"

        ],

        "answer": "Drehmomentschlüssel",

        "gebärde_thema": "SCHRAUBENSCHLÜSSEL",

    },

    {

        "lf": 3, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: SCHRAUBENSCHLÜSSEL",

        "type": "C_DGS", "expected_gebärde": "SCHRAUBENSCHLÜSSEL",
        "gebärde_thema": "SCHRAUBENSCHLÜSSEL", # Hinzugefügt

    },

    # 10. Block: Montieren (B_HANDLUNG) -> Gebärde (SCHRAUBEN)

    {

        "lf": 3, "scenario": (

            "Der Azubi muss eine Schraube in ein vorbereitetes Gewinde eindrehen."

        ),

        "question": "Welche Bewegung ist für das Festziehen einer Schraube korrekt?",

        "type": "B_HANDLUNG",

        "options": [

            "Linksdrehung", "Rechtsdrehung", "Hochziehen", "Herunterdrücken"

        ],

        "answer": "Rechtsdrehung",

        "gebärde_thema": "SCHRAUBEN",

    },

    {

        "lf": 3, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: SCHRAUBEN",

        "type": "C_DGS", "expected_gebärde": "SCHRAUBEN",
        "gebärde_thema": "SCHRAUBEN", # Hinzugefügt

    },

    

    # --- NEU HINZUGEFÜGT FÜR LF 3 (6 BLÖCKE GESAMT) ---

    # 11. Block: Montieren (A_TOOL) -> Gebärde (MAULSCHLÜSSEL)

    {

        "lf": 3, "scenario": (

            "Eine Sechskantmutter mit der Größe 17 mm soll gelöst werden, aber "

            "ohne die Notwendigkeit eines genauen Drehmoments."

        ),

        "question": "Welches Werkzeug wird für das einfache Lösen von Sechskantmuttern verwendet?",

        "type": "A_TOOL",

        "options": [

            "Drehmomentschlüssel", "Zange", "Maulschlüssel", "Inbusschlüssel"

        ],

        "answer": "Maulschlüssel",

        "gebärde_thema": "MAULSCHLÜSSEL",

    },

    {

        "lf": 3, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: MAULSCHLÜSSEL",

        "type": "C_DGS", "expected_gebärde": "MAULSCHLÜSSEL",
        "gebärde_thema": "MAULSCHLÜSSEL", # Hinzugefügt

    },

    # ---------------------------------------------------


    # --- LF 4: Technische Systeme instand halten (120 CP) ---

    # 13. Block: Instandhaltung (B_HANDLUNG) -> Gebärde (SCHWEISSAUTOMAT)

    {

        "lf": 4, "scenario": (

            "Eine Stahlschweißkonstruktion ist gerissen und muss repariert "

            "werden. Der Azubi bereitet das Schweißen vor."

        ),

        "question": (

            "Welche der folgenden Maßnahmen ist die wichtigste Sicherheits-Vorbereitung?"

        ),

        "type": "B_HANDLUNG",

        "options": [

            "Schutzkleidung und Schweißmaske anlegen", "Einen Eimer Wasser bereitstellen",

            "Licht ausschalten", "Fenster öffnen"

        ],

        "answer": "Schutzkleidung und Schweißmaske anlegen",

        "gebärde_thema": "SCHWEISSAUTOMAT",

    },

    {

        "lf": 4, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: SCHWEISSAUTOMAT",

        "type": "C_DGS", "expected_gebärde": "SCHWEISSAUTOMAT",
        "gebärde_thema": "SCHWEISSAUTOMAT", # Hinzugefügt

    },

    # 14. Block: Instandhaltung (B_HANDLUNG) -> Gebärde (SCHWEISSAUTOMAT)

    {

        "lf": 4, "scenario": (

            "Die Schweißarbeiten sind abgeschlossen. Der Azubi muss den "

            "Schweißbereich aufräumen und die Geräte abstellen."

        ),

        "question": (

            "Was muss zuerst vom Netz getrennt werden, um die Sicherheit "

            "zu gewährleisten?"

        ),

        "type": "B_HANDLUNG",

        "options": [

            "Die Lichtquelle", "Der Schweißbrenner", 

            "Der Schweißautomat", "Die Absauganlage"

        ],

        "answer": "Der Schweißautomat",

        "gebärde_thema": "SCHWEISSAUTOMAT",

    },

    {

        "lf": 4, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: SCHWEISSAUTOMAT",

        "type": "C_DGS", "expected_gebärde": "SCHWEISSAUTOMAT",
        "gebärde_thema": "SCHWEISSAUTOMAT", # Hinzugefügt

    },

    

    # --- NEU HINZUGEFÜGT FÜR LF 4 (6 BLÖCKE GESAMT) ---

    # 15. Block: Instandhaltung (B_HANDLUNG) -> Gebärde (SICHERHEIT)

    {

        "lf": 4, "scenario": (

            "Bei der Wartung einer Maschine muss die Energieversorgung unterbrochen "

            "werden, um elektrische Unfälle zu vermeiden."

        ),

        "question": "Welche allgemeine Regel gilt immer vor Beginn von Wartungsarbeiten?",

        "type": "B_HANDLUNG",

        "options": [

            "Maschine anlassen", "Ersatzteile bereitstellen",

            "Sicherheit herstellen (Freischalten/Absperren)", "Kühlschmiermittel nachfüllen"

        ],

        "answer": "Sicherheit herstellen (Freischalten/Absperren)",

        "gebärde_thema": "SICHERHEIT",

    },

    {

        "lf": 4, "scenario": "Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!",

        "question": "Gebärden Sie das Werkzeug: SICHERHEIT",

        "type": "C_DGS", "expected_gebärde": "SICHERHEIT",
        "gebärde_thema": "SICHERHEIT", # Hinzugefügt

    },

    # ---------------------------------------------------

]

# NEUE FUNKTION: Standardisiert alle DGS-Fragen-Texte in QUIZ_DATA
def standardize_dgs_questions(quiz_data):
    """
    Standardisiert die Szenario- und Fragen-Texte für alle DGS-Challenge-Fragen 
    (Typ C_DGS) in der Quiz-Datenstruktur.
    """
    for q in quiz_data:
        if q["type"] == "C_DGS":
            gebärde_name = q["expected_gebärde"]
            
            # 1. Szenario-Text vereinheitlichen
            q["scenario"] = (
                f"Du hast die letzte Frage beantwortet. Zeige jetzt die Gebärde!"
            )
            
            # 2. Fragen-Text vereinheitlichen
            q["question"] = f"Gebärden Sie das Werkzeug: {gebärde_name}"
            
            # 3. Das Feld 'gebärde_thema' hinzufügen (zur Sicherheit für die Bildanzeige)
            if "gebärde_thema" not in q:
                 q["gebärde_thema"] = gebärde_name

    return quiz_data

# *******************************************************************
# WICHTIG: Die Funktion einmal ausführen, um die Liste zu korrigieren.
QUIZ_DATA = standardize_dgs_questions(QUIZ_DATA) 
# *******************************************************************


# --- 4. DGS CHALLENGE MODUL (KORRIGIERT) ---

def render_dgs_challenge_ui(expected_gebärde, current_lf):
    """
    Rendert die Kamera-UI und die Klassifizierung, wenn der Fragetyp C_DGS ist.
    """
    prediction_state = st.session_state.prediction_state

    # Angepasster Hinweis basierend auf der Richtigkeit der MC-Frage
    if st.session_state.mc_result == "CORRECT":
        st.warning("🤟 Zeige die Gebärde, um den Block abzuschließen und weiterzukommen!")
    else:
        st.error("⚠️ Korrekturübung: Du hattest die MC-Frage falsch. Zeige jetzt die Gebärde zur Festigung.")

    st.info(f"Ziel-Gebärde: **{expected_gebärde}**")

    quiz_container, cam_webrtc = st.columns([1, 1], vertical_alignment="top")

    correct_class_id = QUIZ_DGS_CLASSES.get(expected_gebärde)

    if correct_class_id is None:
        st.error(
            f"Fehler: Die Gebärde '{expected_gebärde}' ist im Quiz-Katalog "
            "nicht definiert."
        )
        return

    # Korrekter Aufruf mit DREI Argumenten
    callback = create_frame_callback(config, prediction_state, correct_class_id)

    # VORSCHLAG FÜR NEUE CONSTRAINTS ZUR AUFLÖSUNGSSENKUNG
    video_constraints = {
        "video": {
            "width": {"ideal": 640},
            "height": {"ideal": 360},
        }, 
        "audio": False
    }

    # WebRTC Streamer
    with cam_webrtc:
        webrtc_ctx = webrtc_streamer(
            key="quiz_dgs_challenge",
            mode=WebRtcMode.SENDRECV,
            video_frame_callback=callback,
            media_stream_constraints=video_constraints, # Nutzt die reduzierten Constraints
            async_processing=True,
        )

    with quiz_container:
        image_url = get_image_url(expected_gebärde)
        st.image(
            image_url,
            caption=None, 
            use_container_width=True, # Behebt die Warnung: use_column_width durch use_container_width ersetzt
        )

        prediction_placeholder = st.empty()
        progress = st.empty()
        progress.progress(0)

        # Update display while streaming
        if webrtc_ctx.state.playing and not st.session_state.dgs_challenge_passed:
            while (
                webrtc_ctx.state.playing
                and not st.session_state.dgs_challenge_passed
            ):
                current_strength = prediction_state.get_prediction_strength()
                
                bar_percent = (
                    current_strength if 0.05 < current_strength <= 1 else 0
                )
                progress.progress(bar_percent)
                prediction_placeholder.markdown(
                    f"**Erkennung läuft:** {int(bar_percent * 100)}%"
                )

                # Erfolgreiche Erkennung
                if current_strength >= 1:
                    prediction_state.set_prediction_strength(-1) # Reset
                    st.session_state.dgs_challenge_passed = True
                    time.sleep(1)
                    st.rerun() 

                # WICHTIG: DIESEN WERT AUF 2.0 ERHÖHEN, um CPU/GPU zu entlasten
                time.sleep(2.0) 

    # --- NEUE, BESSERE PLATZIERUNG DER BUTTONS (UNTERHALB DER SPALTEN) ---
    st.divider()
    col1, col2, _ = st.columns([1, 1, 3])
    
    with col1:
         # Funktionalität: Springt zum Ende des Quiz
         if st.button("🚫 Challenge beenden (Quiz abbrechen)", type="secondary"): 
             st.session_state.quiz_index = len(QUIZ_DATA)
             st.rerun()

    with col2:
        if st.button("⏩ Gebärde überspringen (0 Punkte)", type="secondary"):
            st.session_state.quiz_index += 1
            
            # NEU: Zustand für die nächste MC-Frage zurücksetzen!
            st.session_state.mc_result = None 
            st.session_state.dgs_challenge_passed = False 
            
            st.info("Challenge übersprungen. 0 Punkte.")
            time.sleep(0.5) 
            st.rerun() 
            
    # --- ENDE BUTTONS ---

    if st.session_state.dgs_challenge_passed:
        st.success("✅ Challenge bestanden! Weiter zur nächsten Frage.")
        if st.button("Nächste Frage", type="primary"):
            # Ruft check_answer auf, um den Score zu erhöhen und den Index zu erhöhen.
            check_answer("C_DGS", None, None, dgs_passed=True)


# --- 5. HAUPTFUNKTION ZUR WIEDERGABE (KORRIGIERT) ---

def render_quiz_simulation():
    """Rendert die aktuelle Quiz-Frage in Streamlit (MC oder DGS-Challenge)."""
    
    # --- Benutzer-Login (Einfache Eingabe) ---
    if "username" not in st.session_state or st.session_state.username == "Azubi":
        st.title("Willkommen zur Lern-Challenge! 👋")
        st.markdown(
            "Bitte gib deinen Namen ein, um deine Lern-Erfolge zu speichern und mit XP zu sammeln."
        )
        user_input = st.text_input("Dein Name/Nickname:")
        if st.button("Starten!", type="primary") and user_input:
            init_quiz_state(user_input)
            st.rerun()
        return
        
    init_quiz_state(st.session_state.username) # Lade den gespeicherten Namen

    current_index = st.session_state.quiz_index

    # --- HIER IST DER NEUE SPRACHWECHSEL BUTTON ---
    _, col_lang_button = st.columns([10, 1])
    
    with col_lang_button:
        # Initialisiere die Sprache, falls sie beim ersten Laden noch nicht existiert
        if "language" not in st.session_state:
             st.session_state.language = "German"
             
        current_lang = st.session_state.language
        
        # Text auf dem Button: Nur Flagge
        if current_lang == "German":
            # Wenn Deutsch aktiv ist, zeige die Flagge für die Zielsprache (Englisch)
            button_label = "🇬🇧"
            button_tooltip = "Switch to English"
        else:
            # Wenn Englisch aktiv ist, zeige die Flagge für die Zielsprache (Deutsch)
            button_label = "🇩🇪"
            button_tooltip = "Zurück zu Deutsch"
            
        # Den Button mit der Umschaltfunktion
        st.button(
            button_label, 
            on_click=toggle_language, 
            help=button_tooltip,
            key="language_toggle_button"
        )

    # 3. PRÜFEN: ENDE DES QUIZ ERREICHT?
    if current_index >= len(QUIZ_DATA):
        st.balloons()
        st.success(f"🥳 **Glückwunsch, {st.session_state.username}!** Du hast alle Fragen beantwortet.")
        st.markdown(f"**Gesamt-XP: {st.session_state.quiz_xp}**")
        st.button("Quiz neu starten", on_click=lambda: st.session_state.clear() or st.rerun())
        return

    current_q = QUIZ_DATA[current_index]
    
    # Extrahieren der LF-Nummer und Berechnung des Fortschritts
    lf_num = current_q["lf"]
    lf_name = LF_NAMES.get(lf_num, "Unbekanntes Lernfeld")
    
    # Berechne den Fortschritt innerhalb des aktuellen Lernfeldes (LF)
    lf_total_steps = len([q for q in QUIZ_DATA if q["lf"] == lf_num])
    lf_start_index = next(
        (i for i, q in enumerate(QUIZ_DATA) if q["lf"] == lf_num), 0
    )
    lf_current_step = current_index - lf_start_index + 1

    st.title(f"🕹️ Werkstatt-Simulation: Lernfeld {lf_num} -- {lf_name}")
    
    st.subheader(
        f"Schritt {lf_current_step} von {lf_total_steps} in LF {lf_num}"
    )
    st.markdown(f"**Aktuelle XP: {st.session_state.quiz_xp}** (Hallo, **{st.session_state.username}**)")

    st.divider()
    
    # --- Szenario und Bild ---
    st.markdown(f"### {current_q['scenario']}")
    
    # Korrektur der Bildanzeige: use_column_width durch use_container_width ersetzen
    if current_q["type"] in ["A_TOOL", "B_HANDLUNG"] or (current_q["type"] == "C_DGS" and st.session_state.mc_result):
        st.image(
            get_image_url(current_q["gebärde_thema"]),
            caption=None,
            use_container_width=True, # Korrektur
        )

    # --- Darstellung basierend auf Fragentyp ---
    st.markdown(f"### {current_q['question']}")

    # HIER IST DIE WICHTIGE ANPASSUNG: Rendere MC-Elemente NUR, WENN NOCH KEINE ANTWORT VERARBEITET WURDE.
    if current_q["type"] in ["A_TOOL", "B_HANDLUNG"]:
        if not st.session_state.mc_result: # <<-- KRITISCHE BEDINGUNG
            
            options = current_q["options"]
            correct_answer = current_q["answer"]
        
            # Placeholder wird hier nur zum Umschließen der Elemente verwendet
            with st.container():
                
                user_choice = st.radio(
                    "Wähle die richtige Antwort:",
                    options,
                    key=f"mc_options_{current_index}",
                )

                if st.button("Antwort prüfen", key=f"check_{current_index}", type="primary"):
                    check_answer(
                        current_q["type"],
                        user_choice,
                        correct_answer,
                        current_q["lf"],
                        current_q["gebärde_thema"],
                    )

    elif current_q["type"] == "C_DGS":
        # KORREKTUR: DGS-Challenge IMMER rendern, wenn der Index darauf zeigt. 
        # Die Buttons sind HIER. Die Warnmeldungen in render_dgs_challenge_ui 
        # kümmern sich um den Zustand (MC_RESULT).
        render_dgs_challenge_ui(current_q["expected_gebärde"], current_q["lf"])