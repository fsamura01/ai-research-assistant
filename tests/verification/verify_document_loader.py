import sys
import os

# Adds the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.document_loader import DocumentLoader, Document

def verify_document_loader():
    print(f"--- DocumentLoader Verification ---")
    loader = DocumentLoader()

    # 1. Test PDF Loading
    print("\n1. Testing PDF Loader...")
    # Calculate project root (up two levels from this script)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    pdf_path = os.path.join(project_root, "data", "Martin FINDINGS CONCLUSIONS.pdf")
    if os.path.exists(pdf_path):
        try:
            pdf_docs = loader.load_pdf(pdf_path)
            print(f"   [SUCCESS] Loaded {len(pdf_docs)} pages from PDF.")
            if pdf_docs:
                print(f"   Sample content: {pdf_docs[0].content[:120]}...")
        except Exception as e:
            print(f"   [FAILURE] PDF loading failed: {e}")
    else:
        print(f"   [INFO] Skipping PDF test: {pdf_path} not found.")

    # 2. Test Web Page Loading
    print("\n2. Testing Web Page Loader...")
    web_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    try:
        web_doc = loader.load_web_page(web_url)
        print(f"   [SUCCESS] Loaded web page: {web_doc.metadata['title']}")
        print(f"   Content length: {len(web_doc.content)} characters.")
    except Exception as e:
        print(f"   [FAILURE] Web loading failed: {e}")

    # 3. Test YouTube Transcript Loading
    print("\n3. Testing YouTube Transcript Loader...")
    youtube_url = "https://www.youtube.com/watch?v=aircAruvnKk" # 3Blue1Brown Neural Networks
    try:
        yt_doc = loader.load_youtube_transcript(youtube_url)
        print(f"   [SUCCESS] Loaded YouTube transcript.")
        print(f"   Content length: {len(yt_doc.content)} characters.")
        print(f"   Sample: {yt_doc.content[:100]}...")
    except Exception as e:
        print(f"   [FAILURE] YouTube loading failed: {e}")

    print("\n--- Verification Complete! ---")

if __name__ == "__main__":
    verify_document_loader()
