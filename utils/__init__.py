import streamlit as st

# === Utility Functions ===


def translate(english_text, german_text):
    """Simple translation function based on session state."""
    if "language" in st.session_state and st.session_state.language == "German":
        return german_text
    return english_text
