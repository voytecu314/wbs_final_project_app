import streamlit as st

# Initialisiere den Session State für die Navigation und Click-Zähler
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "clicks_chat" not in st.session_state:
    st.session_state.clicks_chat = 0  # Neu: Erste Spalte
if "clicks_quiz" not in st.session_state:
    st.session_state.clicks_quiz = 0  # Neu: Zweite Spalte
if "clicks_challenge" not in st.session_state:
    st.session_state.clicks_challenge = 0  # Neu: Dritte Spalte
if "clicks_stats" not in st.session_state:
    st.session_state.clicks_stats = 0  # Für Statistik-Seite


def render_home():
    # --- HEADER UND INTRO ---
    st.markdown("# 🤟", unsafe_allow_html=True)
    st.title("🛠️ DGS-Ausbildungswerkstatt: Lernen mit Gebärden")

    st.markdown("""
    Willkommen bei Deinem Lern-Chatbot, speziell entwickelt für 
                **gehörlose Auszubildende** 
                im ersten Lehrjahr der **Fachkraft für Metalltechnik**.
    
    Unsere App macht das Lernen von Fachvokabular und Arbeitsschritten für Dich einfach,
                ansprechend und interaktiv.
    """)

    st.info(
        """✅ **Ziel:** Die wichtigsten Werkzeuge und Arbeitsschritte des 1. Lehrjahres 
        sicher beherrschen – 
        mit Deiner eigenen Gebärdensprache!"""
    )

    st.divider()  # Visuelle Trennlinie

    # --- NUTZEN UND ZIELE (3 SPALTEN) ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("1. Schnelle Hilfe 💬")
        st.markdown("""
        Unser **RAG Chat** beantwortet Fragen zum Lernstoff und zur Berufsschule – 
                    basierend auf den aktuellen Curricula,
                    Rahmenrichtlinien und Lernmaterialien für inklusive Bildung.
        """)

    with col2:
        st.subheader("2. Interaktives Lernen 🕹️")
        st.markdown("""
        Übe in realistischen **Werkstatt-Quiz-Simulationen** 
                    basierend auf den Lernfeldern 
                    des 1. Ausbildungsjahres.
                    **Bleib dran**!
        """)

    with col3:
        st.subheader("3. DGS-Erkennung 🤟")
        st.markdown("""
        Lerne Gebärden für **aktuell 20 Fachbegriffe** des Metallgewerbes. 
                    Unsere **Kamera-Challenge** prüft Deine Gebärden in Echtzeit.
        """)

    st.divider()

    # --- CTA (Call to Action) ---
    st.subheader("🚀 Wähle deinen Startpunkt:")
    st.markdown(
        """Möchtest du jetzt direkt in das lernfeldbasierte **Werkstatt-Quiz**
        einsteigen, 
        mit der **Kamera-Challenge** beginnen oder den **Chat** nutzen,
        um deine Fragen zur Ausbildung zu klären?"""
    )

    cta_col1, cta_col2, cta_col3 = st.columns(3)

    with cta_col1:  # Entspricht "Schnelle Hilfe" (Chat)
        if st.button("**Chat** 💬", type="primary", use_container_width=True):
            st.session_state.clicks_chat += 1
            st.session_state.page = "Chat"
            st.rerun()

    with cta_col2:  # Entspricht "Interaktive Szenarien" (Quiz)
        if st.button("**Werkstatt-Quiz** 🛠️", use_container_width=True):
            st.session_state.clicks_quiz += 1
            st.session_state.page = "Quiz"
            st.rerun()

    with cta_col3:  # Entspricht "DGS-Erkennung" (Challenge)
        if st.button("**Kamera-Challenge** 🤟", use_container_width=True):
            st.session_state.clicks_challenge += 1
            st.session_state.page = "Challenge"
            st.rerun()

    st.markdown("Oder nutze die Seitenleiste für Chat und weitere Infos.")


# Führen Sie die Funktion aus, wenn die Seite geladen wird
if __name__ == "__main__":
    render_home()
