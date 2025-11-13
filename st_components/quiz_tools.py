import re
import streamlit as st

from rag.chat_engine import create_chat_engine


def render_quiz_tools():
    st.title("🎮 Gamified Learning — Metalltechnik Quiz")
    st.markdown(
        """
    Test your knowledge with adaptive questions derived from your RAG documents.  
    Earn XP and level up as you master each topic! 🔧⚙️
    """
    )

    # ------------------
    # SESSION STATE
    # ------------------
    for key, default in {
        "xp": 0,
        "level": 1,
        "difficulty": "easy",
        "current_question": None,
        "current_options": None,
        "user_answer": None,
        "correct_letter": None,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # ------------------
    # LOAD RAG ENGINE
    # ------------------
    @st.cache_resource
    def init_bot():
        return create_chat_engine()

    rag_bot = init_bot()

    # ------------------
    # GENERATE QUIZ QUESTION (parse text for correct answer + options)
    # ------------------
    def generate_quiz_question(topic, difficulty):
        prompt = f"""
        You are a quiz generator for German metalworking (Metalltechnik).
        Create a single multiple-choice question of difficulty {difficulty} 
        on the topic "{topic}".
        Provide exactly 4 options labeled A) ... B) ... C) ... D) ...
        At the end indicate the correct answer in this format:
        Correct: <letter>
        Example output format:

        Q: <question text>
        A) ...
        B) ...
        C) ...
        D) ...
        Correct: B
        """

        response = rag_bot.chat(prompt)
        text = str(response).strip()

        # Split into lines and parse
        lines = [ln.rstrip() for ln in text.splitlines() if ln.strip() != ""]

        question_lines = []
        options = []
        correct_letter = None

        # Detect lines for A/B/C/D (accept many formats like "A) text", "A. text", "A)text")
        option_regex = re.compile(r"^([A-Da-d])\s*[\)\.|:-]?\s*(.+)$")

        for line in lines:
            # Try to match the "Correct:" line first (robust)
            if line.strip().lower().startswith("correct:"):
                # keep only A-D, uppercase
                candidate = line.split(":", 1)[-1].strip().upper()
                candidate = re.sub(r"[^A-D]", "", candidate)
                if candidate:
                    correct_letter = candidate
                continue

            # Try to match options (A/B/C/D)
            m = option_regex.match(line.strip())
            if m:
                letter = m.group(1).upper()
                text_part = m.group(2).strip()
                # store as "A) text" so we can display full string in radio
                options.append(f"{letter}) {text_part}")
                continue

            # otherwise it's part of the question or extra text
            question_lines.append(line)

        # Fallback: If no options were found, try to parse inline "A)" occurrences
        if not options:
            # Try to find options in the whole text using a different split
            inline_matches = re.findall(r"([A-Da-d][\)\.]\s*[^A-D\)\.]+)", text)
            for m in inline_matches:
                m = m.strip()
                if len(m) > 2:
                    # normalize to "A) rest"
                    letter = m[0].upper()
                    rest = m[2:].strip()
                    options.append(f"{letter}) {rest}")

        # Final fallback for correct_letter if none parsed
        if not correct_letter:
            # attempt a last-ditch regex search
            m = re.search(r"Correct:\s*([A-Da-d])", text)
            if m:
                correct_letter = m.group(1).upper()

        # If still no correct_letter, choose A (keeps logic safe)
        if not correct_letter:
            correct_letter = "A"

        question_text = "\n".join(question_lines).strip()
        # If question_text empty, try to remove option lines from original text and use the remainder
        if not question_text:
            # Remove option lines from original text to build a question snippet
            question_text = re.sub(r"[A-Da-d]\s*[\)\.|:-]?\s*[^A-D\)\.]+", "", text).strip()
            # clean "Correct:" piece
            question_text = re.sub(r"Correct:\s*[A-Da-d]\)?\.?", "", question_text, flags=re.IGNORECASE).strip()

        return question_text, options, correct_letter

    # ------------------
    # QUIZ INTERFACE
    # ------------------
    topic = st.selectbox(
        "🔩 Choose a topic:",
        [
            "Werkzeuge",
            "Sicherheit",
            "Maschinen",
            "Schweißen",
            "Feilen",
            "Drehen",
            "Metallarten",
        ],
        key="topic_select",
    )

    if st.button("🎯 Generate Question", key="gen_question"):
        question, options, correct = generate_quiz_question(topic, st.session_state.difficulty)
        st.session_state.current_question = question
        st.session_state.current_options = options
        st.session_state.correct_letter = correct
        st.session_state.user_answer = None

    # Display current question
    if st.session_state.current_question:
        st.markdown("### 🧠 Your Question:")
        st.markdown(st.session_state.current_question)

        # show options vertically; if options are missing, show simple A,B,C,D
        opts = st.session_state.current_options or ["A) A", "B) B", "C) C", "D) D"]

        st.markdown("#### 📝 Choose your answer:")
        # radio shows full option strings like "A) text..."
        st.session_state.user_answer = st.radio("",
                                               opts,
                                               index=0,
                                               key="quiz_radio")

        # Submit answer
        if st.button("✅ Submit Answer", key="submit_answer"):
            # user_answer will be like "B) Some text..." --> get leading letter
            selected_letter = None
            if st.session_state.user_answer:
                m = re.match(r"^([A-Da-d])", st.session_state.user_answer.strip())
                if m:
                    selected_letter = m.group(1).upper()

            if not selected_letter:
                st.warning("Please select an answer before submitting.")
            else:
                if selected_letter == st.session_state.correct_letter:
                    st.success("🎉 Correct! +10 XP")
                    st.session_state.xp += 10
                else:
                    st.error(
                        f"❌ Incorrect. The correct answer was **{st.session_state.correct_letter}**."
                    )

                # Update difficulty based on XP
                if st.session_state.xp >= 100:
                    st.session_state.level = 3
                    st.session_state.difficulty = "hard"
                elif st.session_state.xp >= 50:
                    st.session_state.level = 2
                    st.session_state.difficulty = "medium"

        # Next question (separate button key)
        if st.button("🎯 Next Question", key="next_question"):
            question, options, correct = generate_quiz_question(topic, st.session_state.difficulty)
            st.session_state.current_question = question
            st.session_state.current_options = options
            st.session_state.correct_letter = correct
            st.session_state.user_answer = None

    # ------------------
    # XP PROGRESS
    # ------------------
    st.markdown("### 📊 XP Progress")
    st.progress(min(st.session_state.xp / 100, 1.0))
    st.info(
        f"""Level {st.session_state.level} — XP: 
        {st.session_state.xp} — Difficulty: 
        {st.session_state.difficulty.capitalize()}"""
    )


# Run directly for testing
if __name__ == "__main__":
    render_quiz_tools()
