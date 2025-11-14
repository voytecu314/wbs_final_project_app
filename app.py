import streamlit as st

from st_components.learning_chat import render_learning_chat
from st_components.home import render_home
from st_components.quiz_hand_signs import render_quiz_hand_signs
from st_components.quiz_tools import render_quiz_tools
from st_components.martins_page import render_martins_page


# --- CSS: make sidebar buttons look like links/text ---
st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<style>
div[data-testid="stSidebarContent"] button[data-testid="stBaseButton-secondary"] {
    background-color: transparent !important;
    color: inherit !important;
    border: none !important;
    text-align: left !important;
    padding-left: 0 !important;
}

div[data-testid="stSidebarContent"] button[data-testid="stBaseButton-secondary"]:hover {
    text-decoration: underline;
    opacity: 0.8;
}
div[data-testid="stSidebarContent"] div[role='radiogroup'] label:nth-child(1) {
    display: none; 
}            
div[data-testid="stSidebarContent"] div[role='radiogroup'] label:nth-child(2) {
    margin-top: -40px; 
}
</style>
""", unsafe_allow_html=True)

# --- MEMORY: selected page ---
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = True

# --- Helper to render a menu item ---
def menu_item(label, page_name):
    if st.sidebar.button(label, key=f"btn_{page_name}"):
        st.session_state.page = page_name
        st.session_state.button_clicked = True


# --- MAIN NAV ITEMS (no radio bubbles) ---
menu_item("Home", "Home")
menu_item("Learn Chat", "Learn Chat")

# --- QUIZ SECTION ---
with st.sidebar.expander("Challenges"):
    quiz_page = st.radio(
        "",
        ["Choose a quiz:","Hand Signs Quiz", "Tools Quiz", "Martins Page"],
        on_change=lambda: st.session_state.__setitem__("button_clicked", False),
        key="quiz_nav"
    )

    st.session_state.page = quiz_page if not st.session_state.button_clicked else st.session_state.page

menu_item("STATS", "STATS")

# --- ROUTING ---
if st.session_state.page == "Home":
    render_home()
elif st.session_state.page == "Learn Chat":
    render_learning_chat()
elif st.session_state.page == "Martins Page":
    render_martins_page()
elif st.session_state.page == "Tools Quiz":
    render_quiz_tools()
elif st.session_state.page == "Hand Signs Quiz":
    render_quiz_hand_signs()
elif st.session_state.page == "STATS":
    pass