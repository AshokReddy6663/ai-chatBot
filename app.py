
import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# --------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="Reddy AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# --------------------------------
# 2. LOAD ENVIRONMENT VARIABLES
# --------------------------------

load_dotenv()


def get_setting(key, default=""):
    """Read settings from environment or Streamlit Cloud Secrets."""
    value = os.getenv(key)

    if value:
        return value.strip()

    try:
        value = st.secrets.get(key, default)
        return str(value).strip()
    except Exception:
        return default


api_key = get_setting("OPENAI_API_KEY")
base_url = get_setting("OPENAI_BASE_URL")
model = get_setting("OPENAI_MODEL", "gpt-4.1-mini")

# --------------------------------
# 3. CHATBOT INTERFACE
# --------------------------------

st.title("🤖 Reddy")
st.caption("Your personal AI assistant, powered by OpenAI API")

# --------------------------------
# 4. CHECK API KEY
# --------------------------------

if not api_key:
    st.warning(
        "OpenAI API key not found. "
        "Please configure your Streamlit Secrets."
    )
    st.stop()

# --------------------------------
# 5. CONNECT TO OPENAI
# --------------------------------

try:
    client_settings = {
        "api_key": api_key
    }

    if base_url:
        client_settings["base_url"] = base_url

    client = OpenAI(**client_settings)

except Exception as error:
    st.error(f"Connection error: {error}")
    st.stop()

# --------------------------------
# 6. CHAT HISTORY
# --------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------
# 7. SIDEBAR
# --------------------------------

with st.sidebar:
    st.header("🤖 Reddy AI")
    st.write("Your personal AI assistant.")

    st.caption(f"Model: {model}")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --------------------------------
# 8. DISPLAY CHAT HISTORY
# --------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --------------------------------
# 9. USER INPUT
# --------------------------------

prompt = st.chat_input("Ask Reddy anything...")

if prompt:

    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("Reddy is thinking..."):

            try:

                response = client.responses.create(
                    model=model,
                    instructions=(
                        "Your name is Reddy. "
                        "You are a friendly, intelligent and helpful AI assistant. "
                        "Answer questions clearly and accurately. "
                        "Explain difficult topics in simple language."
                    ),
                    input=st.session_state.messages
                )

                answer = response.output_text

                st.markdown(answer)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:

                st.error(
                    f"Sorry! Reddy encountered an API error:\n\n{error}"
                )

                # Remove unanswered user message
                if st.session_state.messages[-1]["role"] == "user":
                    st.session_state.messages.pop()
