# 🛠️ Research Assistant: Core Modules Spec v1.0

This document provides a technical reference for the foundational modules of the AI Research Assistant. It covers data ingestion, vector storage, and the retrieval pipeline.

---

## 📂 1. Document Loader (`src/utils/document_loader.py`)
Responsible for extracting raw text and structured metadata from diverse sources.

### Capabilities:
- **PDF Processing:** 
  - Uses `pypdf` to extract text page-by-page.
  - Returns a list of `Document` objects (one per page).
- **Web Scraping:** 
  - Extracts main content using `BeautifulSoup4`.
  - Includes a custom `User-Agent` to bypass security blocks (e.g., Wikipedia).
- **YouTube Transcripts:** 
  - Fetches transcripts using `youtube-transcript-api`.
  - Automatically stitches snippets into a coherent text body.
- **GitHub Ingestion (NEW):**
  - Downloads public repositories via the Codeload API.
  - Automatically parses and indexes all `.md` and `.mdx` files.
  - extracts and preserves **Frontmatter** metadata (title, tags, etc.).

### Metadata Schema:
Every document extracted contains:
- `source_type`: (pdf | web | youtube | github)
- `source_path` / `source_url`
- `source_authority`: (1-10) assigned based on origin.
- `page_number`: (Specific to PDFs)
- `repo`: (Specific to GitHub sources)

---

## 🧠 2. Vector Store (`src/utils/vector_store.py`)
Manages the "long-term memory" of the assistant using **Qdrant**.

### Core Engine:
- **Database:** Qdrant (Runs in-memory for testing, persistent mode for production).
- **Embeddings:** 
  - **Model:** `multi-qa-distilbert-cos-v1` (768 dimensions).
  - **Optimization:** Fine-tuned specifically for Semantic Search & QA.

### Intelligent Chunking (The "Smart Split"):
- **Standard:** Sliding-window approach (fixed size + overlap).
- **AI-Powered:** Uses **Groq (Llama 3.1)** to analyze sentence structure and split text at logical topic boundaries instead of mid-sentence.
- **Fail-Safe:** Automatically falls back to standard chunking if the AI service is unavailable.

---

## ⚙️ 3. Configuration (`src/utils/config.py`)
Centralized settings for the entire pipeline.

| Setting | Purpose |
| :--- | :--- |
| `LLM_PROVIDER` | Choose between `groq` (default) or `openai`. |
| `EMBEDDING_PROVIDER` | Switch between `local` (free) or `openai` (premium). |
| `CHUNK_SIZE` | Target size for text snippets (default: 800). |
| `USE_INTELLIGENT_CHUNKING`| Toggle LLM-based semantic splitting. |

---

## 🧪 4. Verification Suite (`tests/verification/`)
Tools to ensure the system is working correctly.

| Script | What it tests |
| :--- | :--- |
| `verify_document_loader.py` | Validates extraction from PDF, Web, and YouTube. |
| `verify_vector_store.py` | Tests basic addition and retrieval. |
| `verify_intelligent_chunking.py` | Specifically tests LLM-based semantic breaks. |
| `end_to_end_verification.py` | Runs a full cycle: Load -> Index -> Search -> Cite. |

---

## 🤖 5. Agentic Framework (`src/agents/research_agent.py`)
The brain of the assistant that orchestrates tools and follows the ReAct pattern.

### Agent Logic:
- **Main Agent (`src/agents/research_agent.py`):**
  - Powered by **PydanticAI** and **Llama 3.1 8B**.
  - **Dynamic System Prompt**: Injects the user's current `min_authority` constraint into every request.
  - **Strict Enforcement**: Explicitly forbids hallucinations or using internal knowledge in "High Authority" mode.
  - **Type Validation**: Uses Pydantic models for tool arguments.
  - **Dependency Injection**: Uses `ResearchDeps` to pass `min_authority` and `vector_store` to tools.

---

## 🛠️ 6. Research Tools (`src/tools/`)
Live tools that provide the agent with external information.

### Tools:
- **Vector Search (`src/tools/research_local_docs.py`):**
  - Connects to the **Qdrant Vector Store**.
  - Performs semantic search across all indexed PDFs, web pages, and GitHub repos.
- **Web Search (`src/tools/perform_web_search.py`):**
  - Uses the **Tavily API**.
  - Provides real-time news, current events, and general internet browsing capabilities.
- **YouTube Transcripts (`src/tools/get_youtube_transcript.py`):**
  - Uses `youtube-transcript-api`.
  - Extracts and summarizes contents from provided video URLs.
- **Save Note (`src/tools/save_note.py`):**
  - Saves research findings to the `research_notes/` directory.

---

## 📓 7. Note Management & Persistence
Allows the agent to save findings and generate reports.

### Features:
- **Local Storage (`save_note`):**
  - Saves research findings to the `research_notes/` directory.
  - Formats content as structured **Markdown** files with auto-generated titles.

---

## 📊 8. Evaluation & Benchmarking (Week 3)
Systematic measurement of agent performance and response quality.

### Components:
- **Test Data Generation (`src/evaluation/generate_eval_data.py`):**
  - Uses **Groq (Llama 3.1)** to generate synthetic Question-Answer-Context (QAC) triplets from indexed documents.
- **Benchmarking Engine (`src/evaluation/run_benchmark.py`):**
  - Runs the agent against the synthetic dataset.
  - Measures latency and success rate.
- **LLM Judges:**
  - Uses G-Eval patterns to grade responses on Accuracy, Citations, and Completeness.
- **Observability with Logfire:**
  - Integrated into the agent pipeline for real-time tracing of tool calls and LLM prompts.

---

## 📈 9. Monitoring & Dashboard (Week 4)
Operational oversight and cost tracking via Streamlit.

### Features:
- **`AgentLogger` (`src/utils/agent_logger.py`):**
  - SQLite database for persistent storage of interaction history.
  - Automatically calculates estimated token costs based on Llama 3 rates.
- **Monitoring Tab (`projects/week4_monitoring_ui/app.py`):**
  - Summary metrics (Total queries, accuracy, average latency).
  - Cost analysis charts and latency trend visualizations.
  - Searchable interaction logs with tool call details.

---

## 🚀 10. Upcoming Focus
- **Final Polish:** UI refinements and final system integration.
- **Deployment:** Packaging for deployment.
