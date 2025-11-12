import streamlit as st

from rag.chat_engine import create_chat_engine


def render_quiz_tools():
    st.title("🎮 Gamified Learning — Metalltechnik Quiz")
    st.markdown("""
    Test your knowledge with adaptive questions derived from your RAG documents.  
    Earn XP and level up as you master each topic! 🔧⚙️
    """)

    # ------------------
    # SESSION STATE
    # ------------------
    for key, default in {
        "xp": 0,
        "level": 1,
        "difficulty": "easy",
        "current_question": None,
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
    # GENERATE QUIZ QUESTION (parse text for correct answer)
    # ------------------
    def generate_quiz_question(topic, difficulty):
        prompt = f"""
        You are a quiz generator for a German metalworking (Metalltechnik).
        Create multiple-choice question of difficulty {difficulty} 
        on the topic "{topic}".
        Provide 4 options (A–D) and indicate the correct answer in this format:
        Q: <question>
        A) ...
        B) ...
        C) ...
        D) ...
        Correct: <letter>
        """
        response = rag_bot.chat(prompt)
        lines = str(response).splitlines()

        question_lines = []
        correct_letter = None
        for line in lines:
            if line.strip().startswith("Correct:"):
                correct_letter = line.split(":")[-1].strip().upper()
            else:
                question_lines.append(line)

        question_text = "\n".join(question_lines)
        if not correct_letter:
            correct_letter = "A"  # fallback in case parsing fails
        return question_text, correct_letter

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
    )

    if st.button("🎯 Generate Question"):
        question, correct = generate_quiz_question(topic, st.session_state.difficulty)
        st.session_state.current_question = question
        st.session_state.correct_letter = correct
        st.session_state.user_answer = None

    # Display current question
    if st.session_state.current_question:
        st.markdown("### 🧠 Your Question:")
        st.markdown(st.session_state.current_question)

        st.session_state.user_answer = st.radio(
            "Your Answer:", ["A", "B", "C", "D"], horizontal=True
        )

        # Submit answer
        if st.button("✅ Submit Answer"):
            if st.session_state.user_answer == st.session_state.correct_letter:
                st.success("🎉 Correct! +10 XP")
                st.session_state.xp += 10
            else:
                st.error(
                    f"""❌ Incorrect. The correct answer was 
                    **{st.session_state.correct_letter}**."""
                )

            # Update difficulty based on XP
            if st.session_state.xp >= 50:
                st.session_state.level = 2
                st.session_state.difficulty = "medium"
            if st.session_state.xp >= 100:
                st.session_state.level = 3
                st.session_state.difficulty = "hard"

        # Next question
        if st.button("🎯 Next Question"):
            question, correct = generate_quiz_question(
                topic, st.session_state.difficulty
            )
            st.session_state.current_question = question
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
