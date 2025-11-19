import re
import time
from datetime import datetime

import streamlit as st

from rag.chat_engine import create_chat_engine
from utils import translate


# ==========================================
# QUIZ PAGE
# ==========================================
def render_quiz_tools():
    if "username" not in st.session_state:
        @st.dialog("Provide your username")
        def register_username():
            username = st.text_input("Type your username here:")
            #language = st.selectbox("Select your spoken language:", ["English", "German"])
            if st.button("Submit"):
                if username.strip() == "":
                    st.warning("Nickname cannot be empty.")
                    return
                else:
                    st.session_state.username = username
                    #st.session_state.language = language
                    st.rerun()
                    
        register_username()

    else:    
        st.title(translate("Metal Technic Quiz", "Metalltechnik – Quizmodul"))
        st.markdown(
            "Testen Sie Ihr Wissen mit automatisch generierten Fragen "
            "basierend auf Ihren RAG-Dokumenten."
        )

        # --------------------------------------
        # SESSION STATE SETUP
        # --------------------------------------
        defaults = {
            "xp": 0,
            "level": 1,
            "difficulty": "easy",
            "current_question": None,
            "current_options": [],
            "user_answer": None,
            "correct_letter": None,
            "last_generation_time": 0,
            "cached_questions": {},
            "quiz_history": [],
        }

        for key, default in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default

        # --------------------------------------
        # INIT RAG BOT
        # --------------------------------------
        @st.cache_resource
        def init_bot():
            return create_chat_engine()

        rag_bot = init_bot()

        # --------------------------------------
        # COOLDOWN + CACHE
        # --------------------------------------
        COOLDOWN_SECONDS = 25

        def can_generate():
            return time.time() - st.session_state.last_generation_time >= COOLDOWN_SECONDS

        def update_generation_time():
            st.session_state.last_generation_time = time.time()

        # --------------------------------------
        # QUIZ GENERATION
        # --------------------------------------
        def generate_quiz_question(topic, difficulty):
            cache_key = f"{topic}_{difficulty}"

            # 1) Return cached question
            if cache_key in st.session_state.cached_questions:
                return st.session_state.cached_questions[cache_key]

            # 2) Cooldown check
            if not can_generate():
                remaining = int(
                    COOLDOWN_SECONDS - (time.time() - st.session_state.last_generation_time)
                )
                st.warning(
                    f"Bitte warten Sie {remaining} Sekunden, "
                    f"bevor eine neue Frage generiert wird."
                )
                return None, None, None

            # 3) Build prompt
            prompt = f"""
            You are a quiz generator for German metalworking (Metalltechnik).
            Create ONE multiple-choice question of difficulty {difficulty}
            on the topic "{topic}".
            Provide exactly 4 options labeled A) B) C) D).
            End your answer with: Correct: <letter>.
            """

            # 4) Call RAG engine safely
            try:
                update_generation_time()
                response = rag_bot.chat(prompt)
                text = str(response).strip()
            except Exception:
                st.error("RAG nicht verfügbar – Fallback-Frage wird verwendet.")
                fallback_q = (
                    "Welche Schutzausrüstung ist beim Schleifen von Metall Pflicht?"
                )
                fallback_opts = [
                    "A) Schutzbrille",
                    "B) Arbeits-Sandalen",
                    "C) Sonnenhut",
                    "D) Kopfhörer",
                ]
                return fallback_q, fallback_opts, "A"

            # --------------------------------------
            # Parse LLM Output Robustly
            # --------------------------------------
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            question_lines = []
            options = []
            correct_letter = None

            option_regex = re.compile(r"^([A-Da-d])[\)\.: -]?\s*(.+)$")

            for line in lines:
                # Detect correct-answer line
                if line.lower().startswith("correct:"):
                    raw = line.split(":", 1)[-1].strip().upper()
                    letters = re.findall(r"[A-D]", raw)
                    correct_letter = letters[0] if letters else "A"
                    continue

                # Detect options A–D
                m = option_regex.match(line)
                if m:
                    letter = m.group(1).upper()
                    txt = m.group(2).strip()
                    options.append(f"{letter}) {txt}")
                    continue

                # Otherwise it's question text
                question_lines.append(line)

            # Construct final question text
            question_text = (
                " ".join(question_lines).strip()
                or "Was ist eine Grundregel der Metalltechnik?"
            )

            # Ensure 4 options
            if len(options) != 4:
                options = [
                    "A) Option A",
                    "B) Option B",
                    "C) Option C",
                    "D) Option D",
                ]

            correct_letter = correct_letter or "A"

            result = (question_text, options, correct_letter)

            # Save in cache
            st.session_state.cached_questions[cache_key] = result

            return result

        # --------------------------------------
        # QUIZ UI
        # --------------------------------------
        topic = st.selectbox(
            "Thema auswählen:",
            [
                "Werkzeuge",
                "Sicherheit",
                "Maschinen",
                "Schweißen",
                "Feilen",
                "Drehen",
                "Metallarten",
            ],
        )

        # Generate Question Button
        if st.button("Frage generieren"):
            q, opts, corr = generate_quiz_question(topic, st.session_state.difficulty)
            if q:
                st.session_state.current_question = q
                st.session_state.current_options = opts or []  # FIX: never None
                st.session_state.correct_letter = corr
                st.session_state.user_answer = None

        # ------------------------------
        # Display Active Question
        # ------------------------------
        if st.session_state.current_question:
            st.markdown("### Frage:")
            st.markdown(st.session_state.current_question)

            # FIX: ensure options are always list[str]
            options = st.session_state.current_options or []

            st.session_state.user_answer = st.radio(
                "Antwort auswählen:",
                options,
                key="quiz_answer_radio",
            )

            # Submit Button
            if st.button("Antwort bestätigen"):
                if st.session_state.user_answer:
                    selected_letter = (
                        re.match(r"^([A-Da-d])", st.session_state.user_answer)
                        .group(1)
                        .upper()
                    )
                else:
                    selected_letter = None

                is_correct = selected_letter == st.session_state.correct_letter

                if is_correct:
                    st.success("Richtig! +10 XP")
                    st.session_state.xp += 10
                else:
                    st.error(f"Falsch. Richtige Antwort: {st.session_state.correct_letter}")

                # --------------------------------------
                # SAVE REAL QUIZ HISTORY ENTRY
                # --------------------------------------
                st.session_state.quiz_history.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "topic": topic,
                        "selected": selected_letter,
                        "correct_letter": st.session_state.correct_letter,
                        "correct": is_correct,
                        "difficulty": st.session_state.difficulty,
                    }
                )

                # Level-up logic
                if st.session_state.xp >= 100:
                    st.session_state.level = 3
                    st.session_state.difficulty = "hard"
                elif st.session_state.xp >= 50:
                    st.session_state.level = 2
                    st.session_state.difficulty = "medium"

            # Next Question Button
            if st.button("Nächste Frage"):
                q, opts, corr = generate_quiz_question(topic, st.session_state.difficulty)
                if q:
                    st.session_state.current_question = q
                    st.session_state.current_options = opts or []  # FIX
                    st.session_state.correct_letter = corr
                    st.session_state.user_answer = None

        # --------------------------------------
        # XP BAR
        # --------------------------------------
        st.markdown("### XP-Fortschritt")
        st.progress(st.session_state.xp / 100)
        st.info(
            f"Level: {st.session_state.level} — XP: {st.session_state.xp} — Schwierigkeit: "
            f"{st.session_state.difficulty}"
        )
