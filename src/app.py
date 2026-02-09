import os
import sys
from pathlib import Path

# --- IMPORTANT: Path Configuration must stay at the very top ---
# This ensures 'src' is findable whether running from root, from src/, or in Docker.
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import time
import pandas as pd
import streamlit as st

# Now that path is set, we can safely import from src
from src.utils.config import Config
from src.agents.research_agent import agent
from src.models.schemas import ResearchDeps
from src.utils.vector_store import VectorStore
from src.utils.document_loader import DocumentLoader
from src.utils.agent_logger import AgentLogger


# --- Configuration & Styling ---
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Sidebar text/titles */
    section[data-testid="stSidebar"] .stText, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #c9d1d9 !important;
    }

    /* Chat message styling */
    .stChatMessage {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #30363d;
    }
    
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #21262d;
    }
    
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #0d1117;
    }

    /* Metrics display improvement */
    div[data-testid="stMetricValue"] {
        color: #238636;
        font-weight: bold;
    }

    /* Source tags */
    .source-tag {
        font-size: 0.75em;
        padding: 3px 10px;
        border-radius: 20px;
        background-color: #238636;
        color: white;
        margin-right: 8px;
        font-weight: 600;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- Shared Resources (Cached) ---
@st.cache_resource
def get_vector_store():
    return VectorStore(in_memory=False)

@st.cache_resource
def get_logger():
    return AgentLogger()

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Get shared resources
vector_store = get_vector_store()
logger = get_logger()

# Store in session state for easy access in handlers if needed, 
# though we can just call the cached functions.
if "ingested_sources" not in st.session_state:
    st.session_state.ingested_sources = vector_store.get_all_sources()

# --- Helper Functions ---
def append_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def process_ingestion(file_objs=None, url=None):
    loader = DocumentLoader()
    docs = []
    
    with st.spinner("Processing sources..."):
        if file_objs:
            for file_obj in file_objs:
                st.write(f"Loading PDF: {file_obj.name}")
                docs.extend(loader.load_pdf(file_obj))
        
        if url:
            if "youtube.com" in url or "youtu.be" in url:
                st.write(f"Loading YouTube transcript: {url}")
                docs.append(loader.load_youtube_transcript(url))
            else:
                st.write(f"Loading Web Page: {url}")
                docs.append(loader.load_web_page(url))
        
        if docs:
            count = vector_store.add_documents(docs)
            st.success(f"Successfully indexed {count} chunks!")
            st.session_state.ingested_sources = vector_store.get_all_sources()
        else:
            st.warning("No documents found to index.")

# --- Sidebar: Source Management ---
with st.sidebar:
    st.title("🔍 Research Sources")
    
    # Direct processing of streamlit file uploaders
    st.subheader("Ingest New Data")
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
    source_url = st.text_input("Enter Web/YouTube URL")
    
    if st.button("Index Sources", use_container_width=True):
        if uploaded_files or source_url:
            process_ingestion(uploaded_files, source_url)
        else:
            st.error("Please provide a file or URL.")
    
    st.divider()
    
    st.subheader("Currently Indexed")
    if st.session_state.ingested_sources:
        for src in st.session_state.ingested_sources:
            s_type = src['source_type'].upper()
            s_name = src['source_name']
            if len(s_name) > 30:
                s_name = s_name[:27] + "..."
            st.text(f"[{s_type}] {s_name}")
    else:
        st.info("No sources indexed yet.")
        
    st.divider()
    
    if st.button("Clear Vector DB", type="secondary", use_container_width=True):
        vector_store.clear()
        st.session_state.ingested_sources = []
        st.success("Vector DB cleared!")
        st.rerun()

    if st.button("Clear Interaction Logs", type="secondary", use_container_width=True):
        logger.clear_logs()
        st.success("Logs cleared!")
        st.rerun()

    if st.button("Clear History", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main Interface ---
tab1, tab2, tab3, tab4 = st.tabs(["💻 Chat", "📊 Monitoring", "📝 Research Notes", "⚙️ Settings"])

with tab1:
    st.title("AI Research Assistant")
    st.caption("Ask questions about your uploaded documents or search the web.")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- Chat Input (Outside Tabs for stability) ---
if prompt := st.chat_input("What would you like to research?"):
    # Always show in Tab 1 (Chat)
    with tab1:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to history
        append_message("user", prompt)

        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            start_time = time.time()
            with st.status("Agent is thinking...", expanded=True) as status:
                try:
                    # Initialize dependencies
                    deps = ResearchDeps(
                        api_key=os.getenv("GROQ_API_KEY", "mock-key"),
                        vector_store=vector_store
                    )
                    
                    # Run the agent synchronously
                    # Note: For real-time tool updates, we'd need to use run_async 
                    # and handle the event stream, but st.status captures the spirit.
                    st.write("Checking sources and analyzing...")
                    result = agent.run_sync(prompt, deps=deps)
                    full_response = result.output
                    end_time = time.time()
                    
                    # Log interaction
                    tools_called = []
                    for msg in result.new_messages():
                        if hasattr(msg, 'parts'):
                            for part in msg.parts:
                                if hasattr(part, 'tool_name'):
                                    tools_called.append(part.tool_name)
                                    st.write(f"Used tool: `{part.tool_name}`")
                    
                    status.update(label="Research Complete!", state="complete", expanded=False)
                    
                    message_placeholder.markdown(full_response)
                    
                    logger.log_interaction(
                        query=prompt,
                        response=full_response,
                        usage=result.usage(),
                        latency=end_time - start_time,
                        tools=tools_called
                    )
                    
                    # Add assistant response to chat history
                    append_message("assistant", full_response)
                    st.rerun() # Ensure history renders correctly
                except Exception as e:
                    status.update(label="Error occurred", state="error")
                    error_msg = f"**Error:** {str(e)}"
                    message_placeholder.error(error_msg)
                    append_message("assistant", error_msg)
                    st.rerun()

with tab2:
    st.title("Performance & Monitoring")
    
    stats = logger.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Queries", stats["total_queries"])
    col2.metric("Total Tokens", f"{stats['total_tokens']:,}")
    col3.metric("Total Cost", f"${stats['total_cost']:.4f}")
    col4.metric("Avg Latency", f"{stats['avg_latency']:.2f}s")
    
    st.divider()
    
    st.subheader("Interaction Logs")
    logs_df = logger.get_logs()
    if not logs_df.empty:
        # Style the dataframe
        st.dataframe(
            logs_df[["timestamp", "query", "total_tokens", "cost", "latency", "tools_used"]],
            use_container_width=True,
            hide_index=True
        )
        
        # Performance Charts
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("Cost Trend")
            logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
            st.line_chart(logs_df.set_index('timestamp')['cost'])
        
        with col_chart2:
            st.subheader("Latency Trend")
            st.line_chart(logs_df.set_index('timestamp')['latency'])
    else:
        st.info("No logs available yet. Start chatting to see metrics!")

with tab3:
    st.title("📝 Research Notes")
    st.caption("Browse and read saved research findings.")
    
    notes_dir = Path("research_notes")
    if notes_dir.exists():
        note_files = list(notes_dir.glob("*.md"))
        if note_files:
            # Sort by modification time (most recent first)
            note_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            selected_note = st.selectbox(
                "Select a note to view", 
                options=[f.name for f in note_files],
                index=0
            )
            
            if selected_note:
                note_path = notes_dir / selected_note
                with open(note_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                st.divider()
                st.markdown(content)
                
                if st.button("Delete Note", type="secondary"):
                    note_path.unlink()
                    st.success(f"Deleted {selected_note}")
                    st.rerun()
        else:
            st.info("No research notes found. Use the agent to save findings!")
    else:
        st.warning("`research_notes` directory does not exist.")

with tab4:
    st.title("⚙️ System Settings")
    st.caption("Overview of the current system configuration.")
    
    from src.utils.config import Config
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Model Configuration")
        st.info(f"**LLM Provider:** `{Config.LLM_PROVIDER.upper()}`")
        st.info(f"**Primary Model:** `{Config.GROQ_MODEL}`")
        st.info(f"**Chunking Model:** `{Config.CHUNKING_LLM_MODEL}`")
        
    with col2:
        st.subheader("Knowledge Base")
        st.success(f"**Embedding Provider:** `{Config.EMBEDDING_PROVIDER.upper()}`")
        st.success(f"**Embedding Model:** `{Config.EMBEDDING_MODEL}`")
        st.success(f"**Vector Size:** `{Config.VECTOR_SIZE}`")
    
    st.divider()
    st.subheader("RAG Parameters")
    rag_col1, rag_col2, rag_col3 = st.columns(3)
    rag_col1.metric("Chunk Size", Config.CHUNK_SIZE)
    rag_col2.metric("Chunk Overlap", Config.CHUNK_OVERLAP)
    rag_col3.metric("Top K Results", Config.TOP_K_RESULTS)
    
    st.checkbox("Use Intelligent Chunking", value=Config.USE_INTELLIGENT_CHUNKING, disabled=True)
