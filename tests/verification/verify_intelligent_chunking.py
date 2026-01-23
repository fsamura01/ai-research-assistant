import sys
import os

# Adds the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.vector_store import VectorStore
from src.document_loader import Document
from src.utils.config import Config

def verify_intelligent_chunking():
    project_root = Config.PROJECT_ROOT
    log_file = os.path.join(project_root, "tests", "verification", "chunking_results.log")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"--- Intelligent Chunking Verification ---\n")
        
        # Force intelligent chunking on for this test
        Config.USE_INTELLIGENT_CHUNKING = True
        f.write(f"Intelligent Chunking Enabled: {Config.USE_INTELLIGENT_CHUNKING}\n")
        f.write(f"Model: {Config.CHUNKING_LLM_MODEL}\n\n")

        vstore = VectorStore(collection_name="chunking_test", in_memory=True)
        
        test_text = """
        Artificial Intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans. 
        AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals.
        
        Machine learning (ML) is a field of inquiry devoted to understanding and building methods that 'learn', that is, methods that leverage data to improve performance on some set of tasks. 
        It is seen as a part of artificial intelligence. Machine learning algorithms build a model based on sample data, known as training data, in order to make predictions or decisions without being explicitly programmed to do so.
        
        Deep learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning. 
        Learning can be supervised, semi-supervised or unsupervised.
        """
        
        doc = Document(content=test_text, metadata={"source_type": "test", "topic": "AI Overview"})
        
        f.write("Adding document with intelligent chunking...\n")
        count = vstore.add_documents([doc])
        
        f.write(f"\nCreated {count} chunks.\n")
        
        # Retrieve and show chunks
        results = vstore.search("AI vs Machine Learning", top_k=5)
        f.write("\nChunks retrieved:\n")
        for i, res in enumerate(results, 1):
            f.write(f"\n--- Chunk {i} ---\n")
            f.write(res['text'].strip() + "\n")
    
    print(f"Verification complete. Results written to {log_file}")

if __name__ == "__main__":
    verify_intelligent_chunking()
