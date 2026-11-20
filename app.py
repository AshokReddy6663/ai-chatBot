import io
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
from pypdf import PdfReader
from docx import Document

load_dotenv()

st.set_page_config(page_title="Reddy AI Assistant", page_icon="🤖", layout="wide")


def get_setting(name: str, default: str = "") -> str:
    """Read Streamlit Cloud Secrets first, then local environment variables."""
    try:
        value = st.secrets.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    except Exception:
        pass
    return os.getenv(name, default).strip()


api_key = get_setting("OPENAI_API_KEY")
base_url = get_setting("OPENAI_BASE_URL")
model = get_setting("OPENAI_MODEL", "gpt-4.1-mini")

st.title("🤖 Reddy")
st.caption("Your AI assistant for chat, voice conversations and documents")

if not api_key:
    st.error("OpenAI API key not found. Add OPENAI_API_KEY in Streamlit → App settings → Secrets.")
    st.code('OPENAI_API_KEY = "your_api_key"\nOPENAI_MODEL = "gpt-4.1-mini"')
    st.stop()

try:
    client_args = {"api_key": api_key}
    if base_url:
        client_args["base_url"] = base_url
    client = OpenAI(**client_args)
except Exception as exc:
    st.error(f"Could not initialize the OpenAI client: {exc}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_context" not in st.session_state:
    st.session_state.document_context = ""
if "document_name" not in st.session_state:
    st.session_state.document_name = ""

with st.sidebar:
    st.header("Reddy controls")
    st.caption(f"Model: `{model}`")
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("📎 Upload a file")
    upload = st.file_uploader("PDF, DOCX or TXT", type=["pdf", "docx", "txt"])
    if upload is not None:
        try:
            raw = upload.getvalue()
            if upload.name.lower().endswith(".pdf"):
                pdf = PdfReader(io.BytesIO(raw))
                extracted = "\n".join(page.extract_text() or "" for page in pdf.pages)
            elif upload.name.lower().endswith(".docx"):
                doc = Document(io.BytesIO(raw))
                extracted = "\n".join(p.text for p in doc.paragraphs)
            else:
                extracted = raw.decode("utf-8", errors="replace")

            st.session_state.document_context = extracted[:60000]
            st.session_state.document_name = upload.name
            st.success(f"Loaded {upload.name}")
            st.caption(f"Using up to 60,000 extracted characters.")
        except Exception as exc:
            st.error(f"Could not read the file: {exc}")

    if st.session_state.document_name:
        st.info(f"Active document: {st.session_state.document_name}")
    if st.button("Remove uploaded file", use_container_width=True):
        st.session_state.document_context = ""
        st.session_state.document_name = ""
        st.rerun()

    st.divider()
    st.caption("Voice uses push-to-talk. Allow microphone access in your browser.")

def build_instructions():
    instructions = (
        "Your name is Reddy. You are a friendly, helpful AI assistant. "
        "Answer clearly and accurately. When a document context is provided, "
        "use it to answer questions about that document. If the answer is not "
        "in the document, say so rather than inventing it."
    )
    if st.session_state.document_context:
        instructions += (
            "\n\nThe user uploaded a document named "
            + st.session_state.document_name
            + ". Its extracted text follows:\n"
            + st.session_state.document_context
        )
    return instructions

def get_reply():
    # The current user message is already in session history; do not append it twice.
    response = client.responses.create(
        model=model,
        instructions=build_instructions(),
        input=st.session_state.messages[-20:],
    )
    return response.output_text or "I couldn't generate a text response."

def send_message(text):
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.markdown(text)

    with st.chat_message("assistant"):
        with st.spinner("Reddy is thinking..."):
            try:
                answer = get_reply()
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                return answer
            except Exception as exc:
                st.error(f"Reddy couldn't answer: {exc}")
                if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                    st.session_state.messages.pop()
                return None

# Render previous conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Text chat
prompt = st.chat_input("Message Reddy...")
if prompt:
    send_message(prompt)

st.divider()
st.subheader("🎙️ Talk to Reddy")
st.write("Press Start recording, speak, stop recording, then send your message.")

audio = mic_recorder(
    start_prompt="🎙️ Start recording",
    stop_prompt="⏹️ Stop recording",
    just_once=True,
    use_container_width=True,
    key="reddy_voice_recorder",
)

if audio and audio.get("bytes"):
    st.audio(audio["bytes"])
    if st.button("Send voice message to Reddy", type="primary"):
        try:
            audio_file = io.BytesIO(audio["bytes"])
            # MediaRecorder commonly returns WebM audio in browsers.
            audio_file.name = "reddy_voice.webm"
            with st.spinner("Reddy is listening..."):
                transcript = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=audio_file,
                )
            spoken_text = transcript.text.strip()
            if not spoken_text:
                st.warning("No speech was detected. Please record again.")
            else:
                reply = send_message(spoken_text)
                if reply:
                    with st.spinner("Reddy is preparing a spoken reply..."):
                        speech = client.audio.speech.create(
                            model="tts-1",
                            voice="alloy",
                            input=reply[:4000],
                        )
                    st.audio(speech.content, format="audio/mp3")
        except Exception as exc:
            st.error(
                "Voice processing failed. Check that your API account has access "
                "to the transcription and speech models, then try again.\n\n"
                f"Details: {exc}"
            )

st.caption(
    "This is push-to-talk, not an always-listening wake-word assistant. "
    "Say “Reddy” after starting a recording if you want to address it by name. "
    "The app must be open and microphone permission enabled."
)
