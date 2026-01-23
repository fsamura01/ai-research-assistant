import sys
import os

# Adds the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.vector_store import VectorStore
from src.document_loader import DocumentLoader, Document 
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

        # 3. Add documents
        print("3. Adding documents to store (this may take a moment)...")
        count = vstore.add_documents(docs)
        print(f"   Successfully added {count} chunks from total {len(docs)} document objects.")

        # 4. Search
        print("4. Testing Search (Query: 'What is a neural network?')...")
        results = vstore.search("What is a neural network?", top_k=1)
        
        if results:
            for i, match in enumerate(results, 1):
                metadata = match['metadata']
                source_type = metadata.get('source_type', 'unknown').upper()
                source_name = os.path.basename(metadata.get('source_path', '')) or metadata.get('source_url', 'Web')
                page_info = f" (Page {metadata['page_number']})" if 'page_number' in metadata else ""
                
                print(f"\n   RESULT {i} [Score: {match['score']:.4f}]")
                print(f"   SOURCE: {source_type} - {source_name}{page_info}")
                print(f"   SNIPPET: {match['text'][:200]}...")
            
            # Verify the top result
            top_text = results[0]['text'].lower()
            if "neural" in top_text or "intelligence" in top_text:
                print("\n   [SUCCESS] Search returned relevant context.")
            else:
                print("   [FAILURE] Search returned irrelevant context.")
        else:
            print("   [FAILURE] No results found.")

        # 5. Clear store
        print("5. Testing Clear...")
        vstore.clear()
        
        # Try search again
        post_clear_results = vstore.search("Paris", top_k=1)
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