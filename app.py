import streamlit as st

from st_components.home import render_home
from st_components.rag import render_rag_chat

# Shared sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "RAG Chat"])

# Page routing
if page == "Home":
    render_home()
elif page == "RAG Chat":
    render_rag_chat()
