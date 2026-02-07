# Environment Setup Guide

This document explains how to configure API keys for the GeoAgent Streamlit app.

## Three Methods to Set Your API Key

### Method 1: Environment Variables (Recommended for Local Development)

Set the environment variable in your terminal before running Streamlit:

**PowerShell:**
```powershell
$env:GOOGLE_API_KEY="your-api-key-here"
streamlit run app.py
```

**Windows Command Prompt:**
```cmd
set GOOGLE_API_KEY=your-api-key-here
streamlit run app.py
```

**Linux/macOS (Bash/Zsh):**
```bash
export GOOGLE_API_KEY="your-api-key-here"
streamlit run app.py
```

**Using .env file (with python-dotenv):**
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your-api-key-here
OPENAI_API_KEY=your-openai-key-if-switching
```

Then in Python:
```python
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
```

---

### Method 2: Streamlit Secrets (Recommended for Production)

This is Streamlit's built-in secure secrets management system.

**Local Development:**
1. Edit `.streamlit/secrets.toml` in the project root:
```toml
GOOGLE_API_KEY = "your-google-api-key-here"
```

2. The app automatically reads from this file:
```python
api_key = st.secrets.get("GOOGLE_API_KEY")
```

**Streamlit Cloud Deployment:**
1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Deploy your app
3. In the app settings, add secrets under "Secrets":
```
GOOGLE_API_KEY=your-api-key-here
```

---

### Method 3: Manual Input (for Testing)

If no key is found in environment or secrets, the app shows a text input in the sidebar:
```python
api_key = st.text_input("API Key", type="password")
```

---

## Current Implementation in app.py

The app now tries all three methods in this order:

```python
# 1. Try Streamlit secrets first
api_key = st.secrets.get("GOOGLE_API_KEY")

# 2. Fall back to environment variable
if not api_key:
    api_key = os.getenv("GOOGLE_API_KEY")

# 3. Fall back to manual input
if not api_key:
    api_key = st.text_input("API Key", type="password")
```

---

## Getting Your API Keys

### Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key and add to `.streamlit/secrets.toml` or environment variable

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Create a new secret key
3. Copy and add to environment

---

## Security Best Practices

⚠️ **NEVER commit secrets to Git!**

The `.streamlit/` folder should be added to `.gitignore`:
```
.streamlit/secrets.toml
.env
.venv/
__pycache__/
```

**What's safe to commit:**
- `.streamlit/config.toml` (public configuration)
- `.streamlit/secrets.toml` (template, not actual secrets)

---

## Testing Your Setup

Run this script to verify your API key is accessible:

```python
import os
import streamlit as st

print("Environment Variable:", os.getenv("GOOGLE_API_KEY"))
print("Streamlit Secrets:", st.secrets.get("GOOGLE_API_KEY"))
```

Then run:
```bash
streamlit run test_api_key.py
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Check `.streamlit/secrets.toml` exists and has correct key name |
| Secrets not loading | Restart Streamlit after editing `secrets.toml` |
| Key not set in environment | Use `echo $GOOGLE_API_KEY` (Linux/Mac) or `echo %GOOGLE_API_KEY%` (Windows) to verify |
| Still using manual input? | Verify the key name matches in the code (`GOOGLE_API_KEY`) |

---

## Running the App

```bash
# With environment variable
GOOGLE_API_KEY="your-key" streamlit run app.py

# With .streamlit/secrets.toml
streamlit run app.py

# With manual input (fallback)
streamlit run app.py
```
