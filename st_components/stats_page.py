import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def render_stats_page():

    st.title("📊 Lernstatistik – Metalltechnik")

    # =============================================
    # 1) Load REAL quiz history from session state
    # =============================================
    quiz_history = st.session_state.get("quiz_history", [])

    if not quiz_history or len(quiz_history) == 0:
        st.info("Noch keine Quizdaten vorhanden. Bitte zuerst ein Quiz beantworten.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(quiz_history)

    # Convert timestamps
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # =============================================
    # 2) SUMMARY SECTION
    # =============================================
    st.subheader("📈 Gesamtübersicht")

    total_questions = len(df)
    correct_answers = df["correct"].sum()
    accuracy = round((correct_answers / total_questions) * 100, 1)

    avg_difficulty = df["difficulty"].mode()[0] if "difficulty" in df else "-"

    xp = st.session_state.get("xp", 0)
    level = st.session_state.get("level", 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📝 Beantwortete Fragen", total_questions)
    c2.metric("🎯 Genauigkeit", f"{accuracy}%")
    c3.metric("⭐ XP Gesamt", xp)
    c4.metric("🏆 Level", level)

    st.markdown("---")

    # =============================================
    # 3) Accuracy by Topic
    # =============================================
    st.subheader("🧩 Genauigkeit pro Thema")

    if "topic" in df:
        topic_summary = df.groupby("topic")["correct"].mean().reset_index()
        topic_summary["accuracy"] = (topic_summary["correct"] * 100).round(1)

        fig1, ax1 = plt.subplots(figsize=(7, 3))
        ax1.bar(topic_summary["topic"], topic_summary["accuracy"])
        ax1.set_ylabel("Genauigkeit (%)")
        ax1.set_ylim(0, 100)
        plt.xticks(rotation=25)
        st.pyplot(fig1)
    else:
        st.info("Keine Themenzuordnung vorhanden.")

    st.markdown("---")

    # =============================================
    # 4) Performance Over Time
    # =============================================
    st.subheader("⏱️ Entwicklung über die Zeit")

    df_time = df.sort_values("timestamp")

    fig2, ax2 = plt.subplots(figsize=(7, 3))
    ax2.plot(
        df_time["timestamp"],
        df_time["correct"].astype(int).rolling(5, min_periods=1).mean(),
        marker="o"
    )
    ax2.set_ylabel("Gleitende Genauigkeit")
    ax2.set_ylim(0, 1)
    plt.xticks(rotation=25)
    st.pyplot(fig2)

    st.markdown("---")

    # =============================================
    # 5) Difficulty Distribution
    # =============================================
    if "difficulty" in df:
        st.subheader("📘 Schwierigkeitsverteilung")

        diff_counts = df["difficulty"].value_counts()

        fig3, ax3 = plt.subplots(figsize=(5, 5))
        ax3.pie(diff_counts, labels=diff_counts.index, autopct="%1.1f%%")
        st.pyplot(fig3)

        st.markdown("---")

    # =============================================
    # 6) Recommendations
    # =============================================
    st.subheader("💡 Persönliche Empfehlungen")

    if "topic" in df:

        topic_accuracy = dict(zip(topic_summary["topic"], topic_summary["accuracy"]))
        weakest_topic = min(topic_accuracy, key=topic_accuracy.get)
        weakest_value = topic_accuracy[weakest_topic]

        if weakest_value < 70:
            st.warning(
                f"""📌 **Verbesserungspotenzial:** *{weakest_topic}*  
Deine Genauigkeit hier liegt bei **{weakest_value}%**.  
Übe dieses Thema im Quiz, um dein Level weiter zu steigern."""
            )
        else:
            st.success("🎉 Du hast in allen Themen gute Leistungen! Weiter so!")
    else:
        st.info("Noch keine Empfehlungen möglich – keine Themenzuordnung vorhanden.")

    st.markdown("---")

    # =============================================
    # 7) Raw Data (optional)
    # =============================================
    #with st.expander("📄 Rohdaten anzeigen"):
        #st.dataframe(df)
