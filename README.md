# Reddy - AI Chatbot

A simple Streamlit chatbot using the OpenAI API.

## 1. Requirements

- Python 3.9 or newer
- An OpenAI API key with API access and available usage/billing
- Internet connection

## 2. Install

Open a terminal in this folder and run:

```bash
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt**
```bat
.venv\Scripts\activate.bat
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 3. Add your API key

Copy `.env.example` and name the copy `.env`.

On Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

Open `.env` in a text editor and replace `paste_your_api_key_here` with your API key.

- Keep the key private.
- Do not upload `.env` to GitHub or share it.
- The official OpenAI API uses the default endpoint automatically.
- If you use an OpenAI-compatible third-party endpoint, set `OPENAI_BASE_URL` to its base URL (usually ending in `/v1`).
- Set `OPENAI_MODEL` to a model your API account can access.

## 4. Start Reddy

```bash
streamlit run app.py
```

Streamlit will show a local address, usually `http://localhost:8501`. Open it in your browser.

## Troubleshooting

- **Authentication error:** Check that the API key is correct and active.
- **Model not found / access error:** Change `OPENAI_MODEL` to a model enabled for your API account.
- **Insufficient quota / billing error:** Check your API account's usage and billing.
- **Custom endpoint error:** Confirm the provider's base URL, supported API format, and model name.

ChatGPT subscriptions and OpenAI API billing are separate. API usage may incur charges.
