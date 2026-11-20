# Reddy AI Assistant

A Streamlit chatbot with text chat, push-to-talk voice input, spoken replies, and document uploads.

## Included
- AI text chat and conversation history
- Voice recording → OpenAI speech transcription → Reddy response → spoken reply
- PDF, DOCX and TXT uploads with text extraction for document Q&A
- Streamlit Cloud Secrets and local `.env` configuration

## Deploy to Streamlit Community Cloud
1. Extract this ZIP.
2. Push the contents of this folder to a GitHub repository.
3. In Streamlit Community Cloud, create an app from that repository and select `app.py`.
4. Open the app's **Settings → Secrets** and add:

```toml
OPENAI_API_KEY = "your_real_api_key"
OPENAI_MODEL = "gpt-4.1-mini"
```

For the official OpenAI API, omit `OPENAI_BASE_URL`. If you use a compatible custom endpoint, add its base URL as `OPENAI_BASE_URL = "https://your-provider.example/v1"`.

5. Save secrets and reboot the app.

**Never commit your real `.env` file or API key.** The `.gitignore` file excludes `.env`.

## Run locally
1. Copy `.env.example` to `.env`.
2. Add your API key to `.env`.
3. Install dependencies and start:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Voice notes
Voice is push-to-talk: record, stop, then click **Send voice message to Reddy**. The browser must be allowed to access the microphone. This does not provide continuous listening or automatic wake-word detection for “Hey Reddy”; the app must be open and the user must start a recording.

Transcription and text-to-speech call OpenAI audio APIs and may incur API charges. Your API account must have access to the selected models.

## File notes
Supported uploads: PDF, DOCX and TXT. Text is extracted locally and up to 60,000 characters are included as context in Reddy's instructions. Scanned/image-only PDFs may not yield readable text. Uploaded document text is processed as part of the model request.
