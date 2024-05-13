import streamlit as st
from decomposer import Decomposer
st.title("Maritime insights :baloon:")
decomposer=Decomposer()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = decomposer.decompose_question(prompt)
    with st.chat_message("assistant"):
        st.json(response.model_dump_json(indent=4))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response.model_dump_json(indent=4)})