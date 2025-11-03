import streamlit as st

from st_components.home import render_home
from st_components.martins_page import render_martins_page
from st_components.rag import render_rag_chat

# Shared sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "RAG Chat", "Martin's Page"])

# Page routing
if page == "Home":
    render_home()
elif page == "RAG Chat":
    render_rag_chat()
elif page == "Martin's Page":
    render_martins_page()
