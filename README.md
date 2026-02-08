# 🔍 AI Research Assistant

A multi-source RAG-based research assistant built with Python, PydanticAI, and Qdrant.

## 🚀 Quick Start (Docker - Recommended)

The easiest way to run the assistant is using Docker Compose:

1. **Configure Keys:** `cp .env.example .env` and add your `GROQ_API_KEY` and `TAVILY_API_KEY`.
2. **Launch:** `docker-compose up -d --build`
3. **Explore:** Open [http://localhost:8501](http://localhost:8501)

For manual setup instructions, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## ✨ Key Features

- **🌐 Multi-Source Ingestion:** Process PDFs, Web Pages, YouTube Transcripts, and GitHub Repos.
- **🧠 Intelligent Chunking:** Semantic text splitting using LLMs (Llama 3.1) for better context preservation.
- **📝 Research Notes:** Save findings directly from the chat and browse them in the dedicated viewer.
- **📊 Operational Monitoring:** Real-time tracking of token usage, costs, and response latency via a built-in dashboard.
- **🔗 Smart Citations:** Automatic source attribution with clickable links and page numbers.
- **🐳 Containerized:** Ready for easy deployment with Docker and a persistent Qdrant backend.

## 📁 Project Structure

- `src/agents/` - The "Brain" of the assistant powered by PydanticAI.
- `src/tools/` - Modular tools for web search, local doc research, and note-taking.
- `src/utils/` - Core utilities for vector storage, document loading, and logging.
- `projects/week4_monitoring_ui/` - Streamlit-based user interface.
- `research_notes/` - Persistent storage for your research findings.
- `docs/` - Spec documents and deployment guides.

## 🛠️ Verification

Run the end-to-end verification script to ensure the pipeline is healthy:
```bash
uv run python tests/verification/end_to_end_verification.py
```

See [docs/CORE_MODULES_SPEC.md](docs/CORE_MODULES_SPEC.md) for technical deep-dives into each module.
