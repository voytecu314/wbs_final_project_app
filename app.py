import streamlit as st

from st_components.hand_signs_recognition import render_hand_signs_recognition
from st_components.home import render_home
from st_components.quiz_hand_signs import render_quiz_hand_signs
from st_components.quiz_tools import render_quiz_tools
from st_components.rag import render_rag_chat

# Shared sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to", 
    [
        "Home", 
        "RAG Chat", 
        "Hand Signs Recognition", 
        "Tools Quiz", 
        "Hand Signs Quiz"
    ]
)

# Page routing
if page == "Home":
    render_home()
elif page == "RAG Chat":
    render_rag_chat()
elif page == "quiz_tools":
    render_quiz_tools()
elif page == "Hand Signs Recognition":
    render_hand_signs_recognition()
elif page == "Tools Quiz":
    render_quiz_tools()
elif page == "Hand Signs Quiz":
    render_quiz_hand_signs()
