import streamlit as st
from client import ask_agent_sync
import asyncio

# ------------------------------
# Page setup & styles
# ------------------------------
st.set_page_config(page_title="Agentic Chatbot", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    .user-bubble {
        background-color: #DCF8C6;
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 2px;
        width: fit-content;
        align-self: flex-end;
    }
    .bot-bubble {
        background-color: #F3F3F3;
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 2px;
        width: fit-content;
        align-self: flex-start;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💬 Sophia Agentic Chatbot")
st.caption("Ask anything, I'll connect to your LLM and tools!")

# ------------------------------
# Initialize chat history
# ------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------------
# Display chat history
# ------------------------------
chat = st.container()
with chat:
    for entry in st.session_state.history:
        if entry["role"] == "user":
            st.markdown(f"<div class='user-bubble'><b>You:</b> {entry['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-bubble'><b>Sophia:</b> {entry['content']}</div>", unsafe_allow_html=True)

# ------------------------------
# User input
# ------------------------------
with st.form("chat_input", clear_on_submit=True):
    user_input = st.text_input("Your message", "", key="chatbox")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        # Call the agent
        agent_response = ask_agent_sync(user_input)

        # Handle Future returned inside Streamlit loop
        if isinstance(agent_response, asyncio.Future):
            agent_response = asyncio.get_event_loop().run_until_complete(agent_response)

    st.session_state.history.append({"role": "assistant", "content": agent_response})
    st.rerun()
