# AI Research Assistant

A multi-source RAG-based research assistant built with Python and OpenAI/Groq.

## Setup
1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Mac/Linux) or `.\.venv\Scripts\activate.ps1` (Windows-PowerShell)
3. Install dependencies: `uv sync` (or `pip install -r requirements.txt`)
4. Copy `.env.example` to `.env` and add your API keys (GROQ_API_KEY, TAVILY_API_KEY)

## Project Progress

### 🏗️ Day 3-4: Simple RAG Pipeline
- [x] **PDF Loader:** Integrated `pypdf` to extract text from multi-page documents.
- [x] **Vector Store:** Configured **Qdrant** (local mode) for fast similarity search.
- [x] **Embeddings:** Switched to high-quality local embeddings (`multi-qa-distilbert-cos-v1`) optimized for QA.
- [x] **Retrieval:** Implemented basic semantic search with score-based filtering.

### 🌐 Day 5-6: Multi-Source RAG
- [x] **Web Scraping:** Added `BeautifulSoup4` support for indexing websites (with Wikipedia bypass).
- [x] **YouTube Transcripts:** Integrated `youtube-transcript-api` to pull text from videos.
- [x] **Metadata Tracking:** Each chunk now tracks its source URL, filename, and **page number**.
- [x] **Intelligent Chunking:** Added LLM-powered semantic chunking via Groq (Llama 3.1) for logically coherent sections.
- [x] **Citation System:** Search results now include clear source attribution.

## Key Features
- **Hybrid Embedding System:** Easily switch between OpenAI and local Sentence Transformers.
- **Semantic Retrieval:** Find relevant information based on meaning, not just keywords.
- **Smart Citations:** Automatically links answers to specific PDF pages or URLs.
- **Robust Fallback:** If AI chunking fails, the system safely uses sliding-window counts.

## Project Structure
- `src/` - Core logic for document loading and vector storage.
- `notebooks/` - Experimental RAG workflows.
- `data/` - Personal library of PDFs and research materials.
- `tests/` - Comprehensive verification suite for embeddings, loaders, and end-to-end flow.