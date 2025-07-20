
import streamlit as st
from agent import runnable

st.title("Amazon Review Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to review?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = runnable.invoke({"messages": [("user", prompt)]})
        st.markdown(response["messages"][-1].content)
    st.session_state.messages.append({"role": "assistant", "content": response["messages"][-1].content})
