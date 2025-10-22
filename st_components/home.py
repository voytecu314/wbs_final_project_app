import streamlit as st


def render_home():
    st.title("🏠 Welcome to My Streamlit App")
    st.markdown("""
    This is the starting page of your app.
    
    Use the sidebar to navigate through different sections:
    - **RAG Chat**: Ask questions about your documents.
    - **About**: Learn more about this app.
    """)
