# 🎓 Learning Assistant (Week 1 Mini-Project)

A professional research tool designed to help you master any complex topic by analyzing multiple data sources and providing AI-generated answers with **precise citations**.

## 🚀 Key Features

- **Multi-Source Ingestion:** Seamlessly index knowledge from:
  - 📄 **PDFs:** Local technical documents & guides.
  - 🌐 **Web:** Articles, blog posts, and documentation.
  - 🎥 **YouTube:** Full transcripts extracted from video lessons.
  - 📂 **GitHub:** Entire documentation folders from public repositories (supporting `.md` and `.mdx`).
- **Citation Intelligence:** Every answer includes a list of sources used, including **PDF Page Numbers** and **Direct GitHub/Web URLs**.
- **Semantic Logic:** Uses **Intelligent Chunking** (via Groq/Llama 3.1) to split text at topic boundaries, ensuring the AI understands the "full thought."
- **Interactive Classroom:** A persistent loop interface for deep-dive research sessions.

## 🧠 How it Works (RAG Pipeline)

1.  **Load:** The `DocumentLoader` gathers text from your mixed sources.
2.  **Split:** The system performs semantic chunking to keep logical sections together.
3.  **Embed:** Text is converted into mathematical vectors using `multi-qa-distilbert-cos-v1`.
4.  **Index:** Vectors are stored in a local **Qdrant** database.
5.  **Retrieve:** When you ask a question, the assistant finds the top 3 most relevant "memory snippets."
6.  **Answer:** Groq (Llama 3.3) analyzes the snippets and generates a formatted report with citations.

## 🛠️ Quickstart

1.  **Open the Notebook:** `projects/week1_learning_assistant/learning_assistant.ipynb`
2.  **Select Kernel:** Ensure the `Python (AI Research Assistant)` kernel is selected.
3.  **Define your Topic:** Update the `SOURCES` dictionary in Step 3.
4.  **Run Ingestion:** Index your data.
5.  **Ask Questions:** Use the interactive loop to start learning!

## 📂 Architecture

- `learning_assistant.ipynb`: The main entry point and user interface.
- `../../src/document_loader.py`: The brain for data extraction.
- `../../src/vector_store.py`: The "long-term memory" engine.
- `../../docs/CORE_MODULES_SPEC.md`: Detailed module specifications.

---
*Built during Week 1: Foundation & RAG in the AI Learning Journey.*
