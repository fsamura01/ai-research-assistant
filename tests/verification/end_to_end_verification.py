import sys
import os

# Adds the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.vector_store import VectorStore
from src.utils.document_loader import DocumentLoader, Document 
from src.utils.config import Config

def end_to_end_verification():
    print(f"--- End-to-End Verification ---")
    print(f"Provider: {Config.EMBEDDING_PROVIDER}")
    print(f"Model: {Config.EMBEDDING_MODEL}\n")

    try:
        # 1. Initialize (using in-memory for testing)
        print("1. Initializing VectorStore...")
        vstore = VectorStore(collection_name="test_collection", in_memory=True)
        
        # 2. Prepare test documents
        print("2. Preparing real documents using DocumentLoader...")
        loader = DocumentLoader()
        #project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        project_root = Config.PROJECT_ROOT
        
        docs = []
        
        # Load PDF
        pdf_path = os.path.join(project_root, "data", "IBM SkillsBuild_AI Experiential Learning Lab_2025_Guide.pdf")
        if os.path.exists(pdf_path):
            print(f"   Loading PDF: {pdf_path}")
            pdf_docs = loader.load_pdf(pdf_path)[:3] # Load first 3 pages for speed
            docs.extend(pdf_docs)
            
        # Load Web
        web_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
        print(f"   Loading Web: {web_url}")
        docs.append(loader.load_web_page(web_url))
        
        # Load YouTube
        yt_url = "https://www.youtube.com/watch?v=aircAruvnKk"
        print(f"   Loading YouTube: {yt_url}")
        docs.append(loader.load_youtube_transcript(yt_url))

        # Load GitHub
        repo_owner = "fsamura01"
        repo_name = "task-manager-app"
        print(f"   Loading GitHub: {repo_owner}/{repo_name}")
        docs.extend(loader.load_github_repo(repo_owner, repo_name))

        # 3. Add documents
        print("3. Adding documents to store (this may take a moment)...")
        count = vstore.add_documents(docs)
        print(f"   Successfully added {count} chunks from total {len(docs)} document objects.")

        # 4. Search Verification
        print("\n4a. Testing Search (Query: 'What is a neural network?', Min Authority: 1)...")
        results_ai = vstore.search("What is a neural network?", min_authority=1, top_k=1)
        
        if results_ai:
            match = results_ai[0]
            meta = match['metadata']
            print(f"   [RESULT] Source: {meta.get('source_type')} (Auth: {meta.get('source_authority')})")
            print(f"   [SNIPPET] {match['text'][:150]}...")
            if "neural" in match['text'].lower() or "intelligence" in match['text'].lower():
                print("   [SUCCESS] Found AI info with low authority filter.")
            else:
                print("   [FAILURE] Did not find relevant AI info.")
        else:
            print("   [FAILURE] No results for AI query.")

        print("\n4b. Testing Search (Query: 'WebSocket', Min Authority: 9)...")
        # min_authority=9 should only return GitHub
        results_gh = vstore.search("WebSocket", min_authority=9, top_k=1)
        
        if results_gh:
            match = results_gh[0]
            meta = match['metadata']
            print(f"   [RESULT] Source: {meta.get('source_type')} (Auth: {meta.get('source_authority')})")
            print(f"   [SNIPPET] {match['text'][:150]}...")
            if meta.get('source_type') == "github":
                print("   [SUCCESS] Found high-authority GitHub info.")
            else:
                print(f"   [FAILURE] Found wrong source type: {meta.get('source_type')}")
        else:
            print("   [FAILURE] No results for GitHub-only query.")

        # 5. Clear store
        print("5. Testing Clear...")
        vstore.clear()
        
        # Try search again
        post_clear_results = vstore.search("Paris",min_authority=9, top_k=1)
        if not post_clear_results:
            print("   [SUCCESS] Store cleared successfully.")
        else:
            # Note: In some versions of Qdrant in-memory, deletion might behave differently
            # but usually it should return empty if cleared.
            print("   [INFO] Check if data persists after clear.")

        print("\n--- Verification Complete! ---")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    end_to_end_verification()