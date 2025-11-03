import streamlit as st

from rag.chat_engine import create_chat_engine


def render_martins_page():
    st.title("🏠 Welcome to My Streamlit App")
    st.markdown("""
    This is the starting page of your app.
    
    Use the sidebar to navigate through different sections:
    - **RAG Chat**: Ask questions about your documents.
    - **About**: Learn more about this app.
    """)

    @st.cache_resource
    def init_bot():
        return create_chat_engine()

    rag_bot = init_bot()

    st.title("Example: The Future Of The Water")
    st.markdown(
        "![Alt Text](https://i.postimg.cc/T2nB3n6W/Chat-GPT-Image-Oct-20-2025-02-18-04-PM.png)"
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
