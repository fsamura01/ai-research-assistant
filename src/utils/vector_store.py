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
from src.utils.config import Config
from src.utils.document_loader import Document
import hashlib
import uuid
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
            print(f"Created new collection '{self.collection_name}'")
        else:
            count = self.qdrant_client.count(self.collection_name).count
            print(f"Loaded existing collection '{self.collection_name}' with {count} documents.")
            print(f"[OK] Created collection: {self.collection_name}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self._get_embeddings([text])[0]

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts in a single batch for performance."""
        if Config.EMBEDDING_PROVIDER == "openai":
            response = self.openai_client.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=texts
            )
            return [r.embedding for r in response.data]
        else:
            # Local embedding - SentenceTransformers is optimized for lists
            embeddings = self.local_model.encode(texts, batch_size=32, show_progress_bar=False)
            return embeddings.tolist()
    
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

    def _sanitize_metadata(self, metadata: Dict) -> Dict:
        """
        Ensures metadata contains only Qdrant-friendly types (str, int, float, bool, list).
        Uses JSON serialization as a forced bottleneck to break circular references 
        and flatten complex structures.
        """
        import json
        try:
            # Force a round-trip to JSON to flatten everything to basic types
            # and break any circular references or custom objects
            clean_json = json.dumps(metadata, default=str)
            sanitized = json.loads(clean_json)
            return sanitized
        except Exception as e:
            print(f"   [WARNING] Metadata sanitization issue: {e}. Using emergency stringify.")
            return {str(k): str(v) for k, v in metadata.items()}

    def add_documents(self, documents: List[Document]) -> int:
        """
        Add documents to vector store with batched embeddings, batch upserts, and metadata sanitization.
        """
        all_chunks_data = [] # List of tuples: (text, metadata, point_id)
        
        # 1. Collect all chunks and prepare metadata
        for doc in tqdm(documents, desc="📂 Chunking Documents"):
            if Config.USE_INTELLIGENT_CHUNKING:
                chunks = self._intelligent_chunk_text(doc.content)
            else:
                chunks = self._chunk_text(doc.content)
            
            sanitized_meta = self._sanitize_metadata(doc.metadata)
            
            for chunk_idx, chunk in enumerate(chunks):
                # Create unique UUID for point
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc.content[:100]}_{chunk_idx}_{chunk[:50]}"))
                
                # Prepare metadata
                payload = {
                    "text": chunk,
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks),
                    **sanitized_meta
                }
                all_chunks_data.append({
                    "text": chunk,
                    "payload": payload,
                    "id": point_id
                })

        if not all_chunks_data:
            return 0

        # 2. Generate embeddings in large batches (optimized for Speed)
        texts_to_embed = [item["text"] for item in all_chunks_data]
        print(f"🧠 Generating embeddings for {len(texts_to_embed)} chunks...")
        all_embeddings = self._get_embeddings(texts_to_embed)

        # 3. Create Points
        all_points = []
        for i, item in enumerate(all_chunks_data):
            point = PointStruct(
                id=item["id"],
                vector=all_embeddings[i],
                payload=item["payload"]
            )
            all_points.append(point)

        # 4. Upload to Qdrant in batches (optimized for Stability)
        batch_size = 50 # Even smaller batches for diagnostic safety
        total_added = 0
        import traceback
        
        try:
            for i in range(0, len(all_points), batch_size):
                batch = all_points[i : i + batch_size]
                try:
                    self.qdrant_client.upsert(
                        collection_name=self.collection_name,
                        points=batch
                    )
                    total_added += len(batch)
                except RecursionError:
                    print(f"\n❌ [CRITICAL] RecursionError detected in batch starting at {i}!")
                    # In case of recursion error, try to identify the offending point
                    for p in batch:
                        try:
                            import pickle
                            pickle.dumps(p)
                        except RecursionError:
                            print(f"   Found problematic point ID: {p.id}")
                            print(f"   Metadata keys: {list(p.payload.keys())}")
                            # Skip this point and continue
                            continue
                except Exception as e:
                    print(f"   [Batch Error] {e}")
                    continue
        except Exception as e:
            print(f"   [Ingestion Failed] {e}")
            traceback.print_exc()
        
        print(f"[OK] Successfully indexed {total_added} chunks across {len(documents)} documents.")
        return total_added
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Search for relevant documents
        
        Returns:
            List of search results with text and metadata
        """
        top_k = top_k or Config.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self._get_embedding(query)
        
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