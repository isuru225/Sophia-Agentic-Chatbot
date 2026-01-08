import streamlit as st
from client import ask_agent_sync
import pandas as pd

# ------------------------------
# Streamlit config
# ------------------------------
st.set_page_config(
    page_title="Agentic Chatbot",
    page_icon="🤖",
    layout="wide",
)
st.set_option("client.showErrorDetails", True)

# ------------------------------
# Styles
# ------------------------------
st.markdown(
    """
    <style>
    .user-bubble {
        background-color: #DCF8C6;
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 6px;
        width: fit-content;
        align-self: flex-end;
    }
    .bot-bubble {
        background-color: #F3F3F3;
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 6px;
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

# ------------------------------
# Header
# ------------------------------
st.title("💬 Sophia Agentic Chatbot")
st.caption("Ask anything — I can reason and call tools")

# ------------------------------
# Session state
# ------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------------
# Helper to render AI content
# ------------------------------
def render_bot_content(content):
    """Render assistant message based on type."""
    if isinstance(content, dict):
        msg_type = content.get("type")
        data = content.get("data")

        if msg_type == "table":
            st.markdown("<div class='bot-bubble'><b>Sophia:</b></div>", unsafe_allow_html=True)
            st.dataframe(data)
        elif msg_type == "bullet":
            st.markdown("<div class='bot-bubble'><b>Sophia:</b></div>", unsafe_allow_html=True)
            st.markdown("\n".join([f"- {item}" for item in data]))
        else:  # text
            st.markdown(
                f"<div class='bot-bubble'><b>Sophia:</b> {data}</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"<div class='bot-bubble'><b>Sophia:</b> {content}</div>",
            unsafe_allow_html=True,
        )

# ------------------------------
# Chat history
# ------------------------------
with st.container():
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(
                f"<div class='user-bubble'><b>You:</b> {msg['content']}</div>",
                unsafe_allow_html=True,
            )
        else:
            render_bot_content(msg["content"])

# ------------------------------
# Input form
# ------------------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Your message")
    submitted = st.form_submit_button("Send")

# ------------------------------
# Handle submission
# ------------------------------
if submitted and user_input.strip():
    # Add user message
    st.session_state.history.append({"role": "user", "content": user_input})

    # Ask AI
    with st.spinner("Thinking..."):
        try:
            response_raw = ask_agent_sync(user_input)

            # Convert AI response into structured format
            if isinstance(response_raw, dict) and "type" in response_raw:
                response_struct = response_raw
            else:
                # Detect type automatically
                if isinstance(response_raw, list) and all(isinstance(row, dict) for row in response_raw):
                    response_struct = {"type": "table", "data": pd.DataFrame(response_raw)}
                elif isinstance(response_raw, list):
                    bullets = [str(item) for item in response_raw]
                    response_struct = {"type": "bullet", "data": bullets}
                else:
                    response_struct = {"type": "text", "data": str(response_raw)}

        except Exception as e:
            response_struct = {"type": "text", "data": f"❌ Error: {e}"}

    # Add bot response
    st.session_state.history.append({"role": "assistant", "content": response_struct})

    st.rerun()
