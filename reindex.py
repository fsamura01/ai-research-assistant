from src.vector_store import VectorStore
from src.document_loader import DocumentLoader, Document
from src.utils.config import Config
import os
from typing import List, Dict

def process_github_repos(loader: DocumentLoader, topic: str, github_sources: List[str]) -> List[Document]:
    """Downloads and processes markdown files from GitHub repositories."""
    all_docs = []
    if not github_sources:
        return all_docs

    print("\n--- 📂 Processing GitHub Repositories ---")
    for repo_info in github_sources:
        try:
            # Clean and parse owner/repo/branch
            clean_info = repo_info.replace("https://github.com/", "").strip("/")
            parts = clean_info.split('/')
            
            if len(parts) < 2:
                print(f"   ⚠️ Skipping invalid GitHub info: {repo_info}")
                continue
                
            owner, name = parts[0], parts[1]
            branch = parts[2] if len(parts) > 2 else "main" 
            
            print(f"   � Downloading {owner}/{name} (Branch: {branch})...")
            repo_docs = loader.load_github_repo(owner, name, branch)
            
            for d in repo_docs:
                d.metadata["topic"] = topic
            all_docs.extend(repo_docs)
        except Exception as e:
            print(f"   ❌ Error processing GitHub repo {repo_info}: {e}")
            
    return all_docs

def process_pdfs(loader: DocumentLoader, topic: str, pdf_sources: List[str]) -> List[Document]:
    """Loads and processes local PDF files."""
    all_docs = []
    if not pdf_sources:
        return all_docs

    print("\n--- 📄 Processing local PDFs ---")
    project_root = Config.PROJECT_ROOT
    for path in pdf_sources:
        try:
            full_path = os.path.join(project_root, path) if not os.path.isabs(path) else path
            if os.path.exists(full_path):
                print(f"   📄 Loading PDF: {os.path.basename(full_path)}")
                pdf_pages = loader.load_pdf(full_path)
                for p in pdf_pages:
                    p.metadata["topic"] = topic
                all_docs.extend(pdf_pages)
            else:
                print(f"   ⚠️ PDF not found: {full_path}")
        except Exception as e:
            print(f"   ❌ Error processing PDF {path}: {e}")
            
    return all_docs

def process_web_pages(loader: DocumentLoader, topic: str, web_sources: List[str]) -> List[Document]:
    """Loads and processes content from web URLs."""
    all_docs = []
    if not web_sources:
        return all_docs

    print("\n--- 🌐 Processing Web Pages ---")
    for url in web_sources:
        try:
            print(f"   🌐 Scraping {url}...")
            web_doc = loader.load_web_page(url)
            web_doc.metadata["topic"] = topic
            all_docs.append(web_doc)
        except Exception as e:
            print(f"   ❌ Error processing web page {url}: {e}")
            
    return all_docs

def process_youtube_videos(loader: DocumentLoader, topic: str, yt_sources: List[str]) -> List[Document]:
    """Loads and processes transcripts from YouTube videos."""
    all_docs = []
    if not yt_sources:
        return all_docs

    print("\n--- 🎥 Processing YouTube Transcripts ---")
    for url in yt_sources:
        try:
            print(f"   🎥 Fetching transcript for {url}...")
            yt_doc = loader.load_youtube_transcript(url)
            yt_doc.metadata["topic"] = topic
            all_docs.append(yt_doc)
        except Exception as e:
            print(f"   ❌ Error processing YouTube video {url}: {e}")
            
    return all_docs

def ingest_learning_material(topic: str, sources: Dict[str, List[str]]):
    """
    Coordinator function that ingests research materials for a specific topic across various sources.
    """
    print(f"\n{'='*50}")
    print(f"🚀 Starting Ingestion for Topic: {topic.upper()}")
    print(f"{'='*50}")

    loader = DocumentLoader()
    vector_store = VectorStore(in_memory=False)
    
    # 1. Clear previous data if needed (optional based on workflow)
    print("🧹 Cleaning previous index for fresh start...")
    vector_store.clear()
    
    # 2. Collect documents from all sources
    all_docs = []
    all_docs.extend(process_github_repos(loader, topic, sources.get("githubs", [])))
    all_docs.extend(process_pdfs(loader, topic, sources.get("pdfs", [])))
    all_docs.extend(process_web_pages(loader, topic, sources.get("webs", [])))
    all_docs.extend(process_youtube_videos(loader, topic, sources.get("youtubes", [])))
    
    # 3. Final Indexing
    if all_docs:
        print(f"\n🧠 Finalizing Indexing: Processing {len(all_docs)} unique documents...")
        count = vector_store.add_documents(all_docs) # Indexing the documents
        print(f"\n✅ Knowledge Base Updated!")
        print(f"   Topic: {topic}")
        print(f"   Total research chunks ready: {count}")
    else:
        print("\n⚠️ No materials found to index. Check your SOURCES configuration.")

# --- INGESTION CONFIGURATION ---
MY_TOPIC = "Docker Fundamentals"

SOURCES = {
    "pdfs": ["data/docker_cheatsheet.pdf"],
    "webs": ["https://docs.docker.com/get-started/overview/"],
    "youtubes": ["https://www.youtube.com/watch?v=fqMOX6JJhGo"],
    "githubs": ["docker/cli/master"], 
}

if __name__ == "__main__":
    ingest_learning_material(MY_TOPIC, SOURCES)
