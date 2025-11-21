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
        @st.dialog(translate("Provide your username","Geben Sie Ihren Benutzernamen ein"))
        def register_username():
            username = st.text_input(translate("Type your username here:","Geben Sie hier Ihren Benutzernamen ein:"))
            #language = st.selectbox("Select your spoken language:", ["English", "German"])
            if st.button(translate("Submit","Absenden")):
                if username.strip() == "":
                    st.warning(translate("Nickname cannot be empty.","Der Spitzname darf nicht leer sein."))
                    return
                else:
                    st.session_state.username = username
                    #st.session_state.language = language
                    st.rerun()
                    
        register_username()

    else:    
        st.title(translate("Metal Technic Quiz", "Metalltechnik – Quizmodul"))
        st.markdown(
            translate("Test your knowledge with automatically generated questions","Testen Sie Ihr Wissen mit automatisch generierten Fragen")
            + translate("based on your RAG documents.","basierend auf Ihren RAG-Dokumenten.")
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
                    translate(f"Please wait {remaining} seconds,",f"Bitte warten Sie {remaining} Sekunden,")
                    +translate("before a new question is generated.","bevor eine neue Frage generiert wird.")
                )
                return None, None, None

            # 3) Build prompt
            prompt = f"""
            You are a quiz generator for German metalworking (Metalltechnik).
            Create ONE multiple-choice question in
            {"English" if st.session_state.get("language_toggle", False) else "German"}
            language of difficulty {difficulty}
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
                st.error(translate("RAG not available – fallback question is used.","RAG nicht verfügbar – Fallback-Frage wird verwendet."))
                fallback_q = (
                    translate("What protective equipment is mandatory when grinding metal?","Welche Schutzausrüstung ist beim Schleifen von Metall Pflicht?")
                )
                fallback_opts = [
                    f'A) {translate("Safety goggles","Schutzbrille")}',
                    f'B) {translate("Work sandals","Arbeits-Sandalen")}',
                    f'C) {translate("Sun hat","Sonnenhut")}',
                    f'D) {translate("Headphones","Kopfhörer")}',
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
                or translate("What is a basic rule of metalworking?","Was ist eine Grundregel der Metalltechnik?")
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
            translate("Select topic:","Thema auswählen:"),
            [
                translate("Tools","Werkzeuge"),
                translate("Safety","Sicherheit"),
                translate("Machines","Maschinen"),
                translate("Welding","Schweißen"),
                translate("Filing","Feilen"),
                translate("Turning","Drehen"),
                translate("Types of metal","Metallarten"),
            ],
        )

        # Generate Question Button
        if st.button(translate("Generate question","Frage generieren")):
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
            st.markdown(translate('### Question',"### Frage:"))
            st.markdown(st.session_state.current_question)

            # FIX: ensure options are always list[str]
            options = st.session_state.current_options or []

            st.session_state.user_answer = st.radio(
                translate("Choose an answer:","Antwort auswählen:"),
                options,
                key="quiz_answer_radio",
            )

            # Submit Button
            if st.button(translate("Confirm","Antwort bestätigen")):
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
                    st.success(translate("Correct!","Richtig!") +"10 XP")
                    st.session_state.xp += 10
                else:
                    st.error(f"{translate('Wrong. Correct answer: ','Falsch. Richtige Antwort:')} {st.session_state.correct_letter}")

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
            if st.button(translate("Next question","Nächste Frage")):
                q, opts, corr = generate_quiz_question(topic, st.session_state.difficulty)
                if q:
                    st.session_state.current_question = q
                    st.session_state.current_options = opts or []  # FIX
                    st.session_state.correct_letter = corr
                    st.session_state.user_answer = None

        # --------------------------------------
        # XP BAR
        # --------------------------------------
        st.markdown("### XP-"+translate("Progress","Fortschritt"))
        st.progress(st.session_state.xp / 100)
        st.info(
            f"Level: {st.session_state.level} — XP: {st.session_state.xp} — {translate('Difficulty:','Schwierigkeit:')} "
            f"{st.session_state.difficulty}"
        )
