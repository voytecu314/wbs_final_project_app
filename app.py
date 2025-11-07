import streamlit as st

from st_components.hand_signs_recognition import render_hand_signs_recognition
from st_components.home import render_home
from st_components.martins_page import render_martins_page
from st_components.quiz_tools import render_quiz_tools
from st_components.rag import render_rag_chat

# Shared sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "RAG Chat", "Martin's Page", "quiz_tools", "Hand Signs Recognition"],
)

# Page routing
if page == "Home":
    render_home()
elif page == "RAG Chat":
    render_rag_chat()
elif page == "quiz_tools":
    render_quiz_tools()
elif page == "Martin's Page":
    render_martins_page()
elif page == "Hand Signs Recognition":
    render_hand_signs_recognition()
