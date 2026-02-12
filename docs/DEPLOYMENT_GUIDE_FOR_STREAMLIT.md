# Deploying to Streamlit Cloud

Follow these steps to deploy your AI Research Assistant from GitHub to Streamlit Cloud.

## 1. Prerequisites
- Your code must be pushed to a **GitHub Repository**.
- You need a **Streamlit Cloud** account (connected to GitHub).

## 2. Dependency Management
The project already includes:
- `pyproject.toml` (for building)
- `requirements.txt` (generated via `uv export` for Streamlit Cloud compatibility)

Streamlit Cloud will automatically detect `requirements.txt` and install all necessary packages.

## 3. Deployment Steps
1. Log in to [Streamlit Cloud](https://share.streamlit.io/).
2. Click **"New app"**.
3. Select your repository, branch, and set the main file path to: `src/app.py`.
4. Click **"Deploy"**.

## 4. Configuring Secrets
Streamlit Cloud uses a `secrets.toml` format via their UI instead of a `.env` file. 

1. In your Streamlit app dashboard, go to **Settings > Secrets**.
2. Paste the following template and fill in your keys:

```toml
GROQ_API_KEY = "your-groq-key"
TAVILY_API_KEY = "your-tavily-key"

# OPTIONAL: Vector Database (Choose one)

# Option A: Qdrant Cloud (Recommended for persistence)
QDRANT_URL = "https://your-cluster-url.qdrant.tech"
QDRANT_API_KEY = "your-api-key"

# Option B: In-Memory (No setup needed, but data is lost on app restart)
# Leave QDRANT_URL blank and the app will default to :memory:
```

## 5. Vector Database (Qdrant) Considerations
- **Local/Docker**: Uses `./qdrant_data`. This **cannot** be used on Streamlit Cloud directly as the filesystem is ephemeral.
- **Persistent Cloud**: Sign up for a free tier at [Qdrant Cloud](https://cloud.qdrant.tech/) to get a cluster URL and API key.
- **Quick Demo**: If you don't provide a `QDRANT_URL`, the app will automatically fall back to **In-Memory mode**, which works for testing but will clear indexed documents whenever Streamlit restarts the container.

## 6. Support
If you encounter a `ResponseHandlingException: timed out`, ensure your `QDRANT_URL` is correct or check the logs in the Streamlit Cloud dashboard.
