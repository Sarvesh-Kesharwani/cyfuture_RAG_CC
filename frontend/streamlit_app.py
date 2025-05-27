import streamlit as st
import requests

# API base URL
API_URL = "http://127.0.0.1:8000"

st.title("📞 AI Customer Service Assistant")

# Session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User text input
user_input = st.text_input("You:", key="input")

if st.button("Send"):
    if user_input:
        # Send query to backend chatbot endpoint
        response = requests.post(f"{API_URL}/chatbot", json={"user_input": user_input})

        if response.status_code == 200:
            bot_reply = response.json()["response"]
        else:
            bot_reply = "Error communicating with backend."

        # Append to chat history
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", bot_reply))

# Display chat history
for speaker, message in st.session_state.chat_history:
    st.write(f"**{speaker}:** {message}")
