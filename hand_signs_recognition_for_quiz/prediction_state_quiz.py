import threading
import time

class PredictionStateQuiz:
    """
    Spezifische Thread-safe Klasse für die DGS-Quiz-Challenge.
    Erweitert die Logik des Kollegen um explizite Increase/Decrease Methoden,
    die in der frame_processor_quiz.py benötigt werden.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.prediction = "No hand detected"
        self.prediction_strength = 0.0
        self.predictions_weights = []
        self.previous_landmarks = 84 * [0.0]
        self.last_prediction_time = 0
        self.frame_count = 0
        
        # NEUE ATTRIBUTE für kontrollierteren Decay/Increase
        self.required_strength = 1.0 
        self.decay_rate = 0.05
        self.increase_factor = 0.1 # Wie schnell Conf. die Stärke erhöht

    # --- Vorhandene Methoden (Unverändert vom Kollegen) ---

    def set_prediction(self, value):
        with self.lock:
            self.prediction = value

    def get_prediction(self):
        with self.lock:
            return self.prediction

    # WICHTIG: set_prediction_strength MUSS so bleiben, da es die Logik des 
    # Kollegen für die Stärken-Berechnung enthält. Wir verwenden hier nur 
    # die Logik zum Setzen des Werts/Resets.
    def set_prediction_strength(self, value):
        with self.lock:
            # Wenn value < 0: Reset-Logik (wird in render_dgs_challenge_ui verwendet)
            if value < 0:
                self.prediction_strength = 0
                self.predictions_weights = []
            
            # WENN SIE DIE IMPLIZITE LOGIK DES KOLLEGEN NUTZEN WOLLEN:
            # Die Original-Logik zur Stärkenanpassung des Kollegen ist komplex.
            # Für unser Quiz verwenden wir die neuen expliziten Methoden, aber 
            # falls sein set_prediction_strength irgendwo anders genutzt wird, 
            # müssen wir es vollständig beibehalten.
            
            # Wir verwenden die Original-Implementierung (Komplett):
            elif 0 <= value <= 0.1:
                new_strength = self.prediction_strength - 0.05
                if new_strength < 0:
                    self.prediction_strength = 0
                else:
                    self.prediction_strength = new_strength
            else:
                if 0 <= self.prediction_strength < 0.3:
                    new_strength = self.prediction_strength + 0.02
                elif 0.3 <= self.prediction_strength < 0.6:
                    new_strength = self.prediction_strength + 0.05
                else:
                    new_strength = self.prediction_strength + 0.1
                if new_strength > 1:
                    self.prediction_strength = 1
                else:
                    self.prediction_strength = new_strength
            "skip" if value < 0 else self.predictions_weights.append(value)
            # -------------------------------------------------------------------

    def get_prediction_strength(self):
        with self.lock:
            # Wir geben den Wert als float (0.0 bis 1.0) zurück.
            return self.prediction_strength 

    def set_previous_landmarks(self, landmarks):
        with self.lock:
            self.previous_landmarks = landmarks

    def get_previous_landmarks(self):
        with self.lock:
            return self.previous_landmarks

    def should_predict(self, skip_frames=5):
        with self.lock:
            self.frame_count += 1
            if self.frame_count % skip_frames == 0:
                # print("Predicting on this frame.", self.frame_count) # Logging entfernen
                return True
            return False

    # --- NEUE METHODEN FÜR DAS QUIZ (beheben den Fehler) ---
    
    def increase_prediction_strength(self, confidence: float):
        """Erhöht die Stärke bei korrekter Vorhersage."""
        with self.lock:
            # Hier nutzen wir unsere einfache Logik: Erhöhen basierend auf Konfidenz
            # und dem definierten Faktor.
            new_strength = self.prediction_strength + (confidence * self.increase_factor)
            
            if new_strength > self.required_strength:
                self.prediction_strength = self.required_strength
            else:
                self.prediction_strength = new_strength
            
            self.frame_count = 0 # Schnelle Reaktion

    def decrease_prediction_strength(self):
        """Senkt die Stärke (Decay), wenn die Geste unbekannt oder falsch ist."""
        with self.lock:
            # Hier nutzen wir unsere einfache Logik: Senken um die Decay Rate
            new_strength = self.prediction_strength - self.decay_rate
            self.prediction_strength = max(0.0, new_strength)
            self.frame_count = 0 # Schnelle Reaktion
