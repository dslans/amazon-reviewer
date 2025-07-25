
import streamlit as st
from multi_agent import runnable
from st_copy_to_clipboard import st_copy_to_clipboard

st.title("Amazon Review Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to review? Enter product name or URL"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = runnable.invoke({"messages": st.session_state.messages})
        review = response["messages"][-1].content
        st.markdown(review)
        st_copy_to_clipboard(review)
    st.session_state.messages.append({"role": "assistant", "content": review})
