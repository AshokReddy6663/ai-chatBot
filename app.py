import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Reddy - AI Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Reddy")
st.caption("Your personal AI assistant, powered by the OpenAI API")

api_key = os.getenv("OPENAI_API_KEY", "").strip()
base_url = os.getenv("OPENAI_BASE_URL", "").strip()
model = os.getenv("OPENAI_MODEL", "gpt-5.5").strip()

if not api_key or api_key == "paste_your_api_key_here":
    st.warning(
        "Add your OpenAI API key to the `.env` file, then restart Reddy."
    )
    st.code("OPENAI_API_KEY=your_actual_api_key\nOPENAI_MODEL=gpt-5.5")
    st.stop()

try:
    client_args = {"api_key": api_key}
    if base_url:
        client_args["base_url"] = base_url
    client = OpenAI(**client_args)
except Exception as exc:
    st.error(f"Could not initialize the API client: {exc}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Reddy settings")
    st.write(f"Model: `{model}`")
    st.caption("Your API key is read from the local .env file.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Message Reddy...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Reddy is thinking..."):
            try:
                response = client.responses.create(
                    model=model,
                    instructions=(
                        "Your name is Reddy. You are a helpful, friendly AI "
                        "assistant. Give accurate, clear answers. Explain "
                        "technical topics in simple steps when useful."
                    ),
                    input=st.session_state.messages,
                )
                answer = response.output_text or "I couldn't generate a text response."
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as exc:
                st.error(
                    "The API request failed. Check your API key, endpoint, "
                    "model name, account access, and billing/usage limits.\n\n"
                    f"Details: {exc}"
                )
                # Remove the unanswered user turn so it can be retried cleanly.
                if st.session_state.messages and st.session_state.messages[-1] == {
                    "role": "user", "content": prompt
                }:
                    st.session_state.messages.pop()
