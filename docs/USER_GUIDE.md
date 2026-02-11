# 📖 AI Research Assistant: User Guide

Welcome to the AI Research Assistant! This guide will walk you through the core features and how to make the most of your research sessions.

---

## 1. 📂 Ingesting Data

Before you can research your documents, you need to index them.

1. **PDFs**: Upload one or more PDF files via the sidebar. The system will extract text and page numbers.
2. **Web Pages**: Enter a URL (e.g., a Wikipedia page or a blog post) in the text input.
3. **YouTube**: Paste a YouTube video link. The assistant will fetch the transcript automatically.
4. **Processing**: Click **"Index Sources"**. You'll see status updates as the system chunks and embeds your data.

> [!TIP]
> Use the sidebar's "Currently Indexed" section to verify which sources are loaded into the assistant's memory. You can also see the **Point Count** in the sidebar to monitor the database size.

---

## 2. 🛡️ Source Authority Control

New to this version is the **Source Authority** trust-layer.

- **Slider**: Use the "Min. Source Authority" slider in the sidebar to set your trust threshold.
- **Trust Scores**:
    - **9 (GitHub)**: Official repositories and dev docs.
    - **7 (Local PDF)**: Your uploaded scholarly or professional files.
    - **5 (Web)**: Live internet results (news, blogs).
    - **4 (YouTube)**: Unstructured transcripts.
- **Strict Mode**: Setting the slider to 7 or above activates "Strict Mode." The agent will refuse to answer using internal knowledge and will only provide information from authorized high-trust sources.
- **Results**: Each search result displayed in the chat will show its authority score, helping you gauge the info's reliability.

Once your data is indexed, you can start asking questions.

- **Natural Language**: Type questions like "What are the main findings of the paper I just uploaded?" or "Compare the views on AI in the two web articles I provided."
- **Web Search**: If the answer isn't in your indexed documents, the agent will automatically use **Tavily Web Search** to find the latest information online.
- **Smart Citations**: Every response includes citations. Clickable links will take you directly to the web source, and page numbers are provided for PDFs.

---

## 3. 📝 Managing Research Notes

Found something important? You can ask the agent to save it for you!

- **Command**: Just say "Save a note about..." or "Create a research note for X."
- **Viewing**: Navigate to the **"Research Notes"** tab in the main interface to browse and read your saved Markdown files.
- **Management**: You can delete old notes directly from the viewer.

---

## 4. 📊 Monitoring & Performance

Keep an eye on how the assistant is performing.

- **Metrics**: The **"Monitoring"** tab shows total queries, token usage, estimated costs, and average response latency.
- **Logs**: Review individual interactions, including which tools the agent used (e.g., `research_local_docs`, `perform_web_search`).
- **Trends**: View charts for cost and latency to track performance over time.

---

## 5. ⚙️ System Settings

Check the underlying technology powering your assistant.

- **Models**: See which LLM (e.g., Llama 3.1) and Embedding models are currently active.
- **RAG Parameters**: Review the `Chunk Size`, `Overlap`, and `Top K` settings that determine how your documents are retrieved.

---

## 🛠️ Troubleshooting

- **No Results?**: Ensure you've clicked "Index Sources" after uploading or entering a URL.
- **API Errors**: Check your `.env` file to ensure `GROQ_API_KEY` and `TAVILY_API_KEY` are correct.
- **Slow Responses**: Complex queries requiring multiple web searches or large document scans may take longer. Monitor the "Agent is thinking..." status for progress.
