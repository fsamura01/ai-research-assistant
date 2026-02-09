# 🔌 AI Research Assistant: API Reference

This document provides a detailed overview of the core classes and tools that power the assistant.

---

## 🛠️ Core Utilities

### `DocumentLoader`
*Location: `src/utils/document_loader.py`*

Handles the extraction of raw content from various sources.

- **`load_pdf(file_obj)`**: Extracts text and page metadata from a PDF byte stream.
- **`load_web_page(url)`**: Scrapes and cleans HTML content from the web.
- **`load_youtube_transcript(url)`**: Retrieves and formats subtitles from YouTube videos.
- **`load_github_repo(repo_url)`**: (Internal) Clones and parses Markdown files from a GitHub repository.

---

### `VectorStore`
*Location: `src/utils/vector_store.py`*

The persistent memory of the assistant, powered by **Qdrant**.

- **`add_documents(docs)`**: Processes a list of `Document` objects, applies (optional) intelligent chunking, and indexes them.
- **`search(query, top_k=5)`**: Performs a semantic search to find relevant snippets.
- **`get_all_sources()`**: Returns a list of all unique documents currently indexed.
- **`clear()`**: Resets the vector database.

---

## 🤖 Reasoning Engine

### `ResearchAgent`
*Location: `src/agents/research_agent.py`*

The core agent built with **PydanticAI**.

- **Architecture**: Follows the **ReAct (Reason + Act)** pattern.
- **Logic**: Orchestrates tool calls based on user intent and retrieved context.
- **Dependencies**: Uses `ResearchDeps` for type-safe access to API keys and storage clients.

---

## 🛠️ Research Tools

Modular functions that the agent can execute during a research session.

### `research_local_docs`
- **Purpose**: Queries the `VectorStore` for information within indexed documents.
- **Input**: `query` (string).
- **Output**: List of relevant text chunks with source metadata.

### `perform_web_search`
- **Purpose**: Accesses real-time data from the internet via **Tavily**.
- **Input**: `query` (string).
- **Output**: Curated list of search results with titles and snippets.

### `get_youtube_transcript`
- **Purpose**: Fetches transcripts for specific videos mentioned in chat.
- **Input**: `video_url` (string).

### `save_note`
- **Purpose**: Persists research findings into the `research_notes/` directory.
- **Input**: `title` (string), `content` (markdown string).

---

## 📊 Logging & Monitoring

### `AgentLogger`
*Location: `src/utils/agent_logger.py`*

- **SQLite Backend**: Stores every interaction for audit and performance tracking.
- **Cost Calculation**: Estimates API usage costs based on token counts.
- **Data Export**: Provides data to the Streamlit UI in standard Pandas formats.
