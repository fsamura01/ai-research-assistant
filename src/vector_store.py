"""Vector store implementation using Qdrant"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from groq import Groq
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import os
from src.utils.config import Config
from src.document_loader import Document
import hashlib
from tqdm.auto import tqdm


    
class VectorStore:
    """Manages vector storage and retrieval using Qdrant"""
    
    def __init__(self, collection_name: str = None, in_memory: bool = True):
        """
        Initialize vector store
        
        Args:
            collection_name: Name of the collection
            in_memory: Use in-memory storage (True) or persistent (False)
        """
        self.collection_name = collection_name or Config.COLLECTION_NAME
        
        if in_memory:
            self.qdrant_client = QdrantClient(":memory:")
        else:
            self.qdrant_client = QdrantClient(path="./qdrant_data")
        
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
        
        # Initialize embedding provider
        if Config.EMBEDDING_PROVIDER == "openai":
            self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.local_model = None
        else:
            self.openai_client = None
            self.local_model = SentenceTransformer(Config.EMBEDDING_MODEL)
            
        self._initialize_collection()
    
    def _initialize_collection(self):
        print(f"Initializing collection: {self.collection_name}")

        """Create collection if it doesn't exist"""
        collections = self.qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=Config.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            print(f"[OK] Created collection: {self.collection_name}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text based on provider"""
        if Config.EMBEDDING_PROVIDER == "openai":
            response = self.openai_client.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        else:
            # Local embedding
            embedding = self.local_model.encode(text)
            return embedding.tolist()
    
    def _chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into chunks"""
        chunk_size = chunk_size or Config.CHUNK_SIZE
        overlap = overlap or Config.CHUNK_OVERLAP
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Don't create tiny final chunks
            if len(chunk) < 100 and chunks:
                chunks[-1] += " " + chunk
                break
            
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def _intelligent_chunk_text(self, text: str) -> List[str]:
        """Split text into logically coherent chunks using LLM"""
        print(f"   [AI] Performing intelligent chunking...")
        
        prompt = f"""
        Analyze the following text and split it into logically coherent sections or paragraphs.
        Each section should focus on a specific sub-topic or theme.
        
        Guidelines:
        1. Preserve the original text exactly.
        2. Aim for chunks of approximately {Config.CHUNK_SIZE} characters where possible.
        3. Return the chunks separated by a unique delimiter: [CHUNK_BOUNDARY]
        
        Text to split:
        ---
        {text}
        ---
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model=Config.CHUNKING_LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a document processing assistant that splits text into logical chunks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1 # Low temperature for consistency
            )
            
            content = response.choices[0].message.content
            print(f"   [AI] Raw response: {content}")
            chunks = content.split("[CHUNK_BOUNDARY]")
            
            # Clean and filter empty chunks
            cleaned_chunks = [c.strip() for c in chunks if c.strip()]

            #cleaned_chunks = []

            #for chunk in chunks:
            #    clean_text = chunk.strip()
            #    if clean_text:
            #        cleaned_chunks.append(clean_text)
            
            if len(cleaned_chunks) > 1:
                print(f"   [AI] Successfully created {len(cleaned_chunks)} semantic chunks.")
                return cleaned_chunks
            
        except Exception as e:
            print(f"   [WARNING] AI Chunking failed: {e}. Falling back to sliding window.")
            
        # Fallback to standard chunking
        return self._chunk_text(text)

    def add_documents(self, documents: List[Document]) -> int:
        """
        Add documents to vector store
        
        Returns:
            Number of chunks added
        """
        points = []
        point_id = 0
        
        for doc in tqdm(documents):
            # Choose chunking method
            if Config.USE_INTELLIGENT_CHUNKING:
                tqdm.write(f"   [AI Research Assistant] Using intelligent chunking for document: {Config.USE_INTELLIGENT_CHUNKING}")
                chunks = self._intelligent_chunk_text(doc.content)
            else:
                tqdm.write(f"   [AI Research Assistant] Using sliding window chunking for document: {Config.USE_INTELLIGENT_CHUNKING}")
                chunks = self._chunk_text(doc.content)
            
            for chunk_idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self._get_embedding(chunk)
                
                # Create unique ID for chunk
                chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
                
                # Prepare metadata
                payload = {
                    "text": chunk,
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks),
                    **doc.metadata,
                    "chunk_id": f"{doc.metadata.get('source_type', 'unknown')}_{chunk_hash}"
                }
                
                # Create point
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
                points.append(point)
                point_id += 1
        
        # Upload to Qdrant
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        print(f"[OK] Added {len(points)} chunks from {len(documents)} documents")
        return len(points)
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Search for relevant documents
        
        Returns:
            List of search results with text and metadata
        """
        top_k = top_k or Config.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self._get_embedding(query)
        
        # Search
        # Search using the modern 'query_points' API
        results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k
        ).points
        
        # Format results
        formatted_results = []
        for point in results:
            formatted_results.append({
                "text": point.payload["text"],
                "score": point.score,
                "metadata": {k: v for k, v in point.payload.items() if k != "text"}
            })
        
        return formatted_results
    
    def clear(self):
        """Clear all data from collection"""
        self.qdrant_client.delete_collection(self.collection_name)
        self._initialize_collection()
        print(f"[OK] Cleared collection: {self.collection_name}")


# Example usage
if __name__ == "__main__":
    from src.document_loader import DocumentLoader
    
    
    # Initialize
    vector_store = VectorStore(in_memory=True)
    loader = DocumentLoader()
    
    # Test with a simple document
    test_doc = Document(
        content="Python is a high-level programming language. It's great for beginners and experts alike.",
        metadata={"source_type": "test", "title": "Python Intro"}
    )
    
    vector_store.add_documents([test_doc])
    
    # Search
    results = vector_store.search("What is Python?", top_k=3)
    print("\nSearch Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   Text: {result['text'][:100]}...")