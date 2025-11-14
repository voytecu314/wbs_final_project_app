import streamlit as st

from rag.chat_engine import create_chat_engine


def render_rag_chat(prompt = None):
    @st.cache_resource
    def init_bot():
        return create_chat_engine()

    rag_bot = init_bot()

    st.title("Metalltechnik")
    st.markdown(
        "![Alt Text](https://bbs-jever.de/files/content/fotos/fachbereich_technik/Metalltechnik/Metalltechnik.jpg)"
    )

    # Display chat messages from history on app rerun
    for message in rag_bot.chat_history:
        with st.chat_message(message.role):
            st.markdown(message.blocks[0].text)

    # React to user input
    if prompt := st.chat_input("Type your question here..."):
        # Display user message in chat message container
        st.chat_message("human").markdown(prompt)

        # Begin spinner before answering question so it's there for the duration
        with st.spinner("Searching for answer in documents..."):
            # send question to chain to get answer
            answer = rag_bot.chat(prompt)

            # extract answer from dictionary returned by chain
            response = answer.response

            # Display chatbot response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)

    return rag_bot
