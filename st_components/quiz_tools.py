import random

import plotly.graph_objects as go
import streamlit as st


def render_quiz_tools():
    st.title("🎮 Gamified Feedback — Sign to Learn")
    st.markdown("""
    ### 🧠 Learn by Doing — Interactive Quiz
    This page helps you test your understanding of different tools 
    or concepts related to sign language gestures.  
    Earn XP points for correct answers and level up as you progress!
    """)

    # Initialize XP and level tracking
    if "xp" not in st.session_state:
        st.session_state.xp = 0
    if "level" not in st.session_state:
        st.session_state.level = 1

    # Quiz setup
    st.subheader("🧰 Choose a Topic")
    selected_tool = st.selectbox(
        "Select a tool to start your quiz:",
        ["Screwdriver", "Hammer", "Wrench", "Pliers"],
    )

    if selected_tool == "Screwdriver":
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/3/3b/Screwdriver.jpg",
            caption="Screwdriver 🪛",
        )
        question = "What is the main purpose of a screwdriver?"
        options = ["Tighten or loosen screws", "Cut wires", "Hammer nails"]
        correct = "Tighten or loosen screws"

    elif selected_tool == "Hammer":
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/8/8c/Hammer.jpg",
            caption="Hammer 🔨",
        )
        question = "Which material is best hammered with this tool?"
        options = ["Wood", "Glass", "Rubber"]
        correct = "Wood"

    elif selected_tool == "Wrench":
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/2/2b/Wrench.jpg",
            caption="Wrench 🔧",
        )
        question = "What is a wrench mainly used for?"
        options = ["Tighten bolts and nuts", "Measure distances", "Mix paint"]
        correct = "Tighten bolts and nuts"

    else:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/2/28/Pliers.jpg",
            caption="Pliers 🔗",
        )
        question = "What action are pliers best for?"
        options = ["Grip or bend wires", "Paint surfaces", "Drill holes"]
        correct = "Grip or bend wires"

    # Quiz Question
    st.subheader("🧩 Quick Quiz")
    user_answer = st.radio(question, options)

    if st.button("Submit Answer"):
        if user_answer == correct:
            st.success("✅ Correct! +10 XP")
            st.session_state.xp += 10

            if st.session_state.xp % 50 == 0:
                st.session_state.level += 1
                st.balloons()
                st.success(f"🎉 Level Up! You are now Level {st.session_state.level}")
        else:
            st.error("❌ Oops! That’s not correct. Try again!")

        feedback = random.choice(
            [
                "Great job 👏",
                "You're improving fast 🚀",
                "Keep up the good work 💪",
                "Nice progress 🌟",
            ]
        )
        st.info(feedback)

    # XP Progress Section
    st.subheader("📊 XP Progress Tracker")

    # Linear progress bar
    st.progress(min(st.session_state.xp % 100, 100) / 100)
    st.metric("Total XP", st.session_state.xp)
    st.metric("Level", st.session_state.level)

    # Plotly XP Gauge
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=st.session_state.xp % 100,
            delta={"reference": 50, "increasing": {"color": "green"}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "royalblue"},
                "steps": [
                    {"range": [0, 50], "color": "lightgray"},
                    {"range": [50, 100], "color": "lightgreen"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 100,
                },
            },
            title={"text": "XP Gauge"},
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # Encouragement message
    if st.session_state.xp < 30:
        st.caption("✨ Keep learning! You’re just getting started.")
    elif st.session_state.xp < 100:
        st.caption("🔥 Nice! You’re building strong understanding.")
    else:
        st.caption("🏆 You’re a pro learner!")
