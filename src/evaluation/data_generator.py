
import sys
import os
import json
from typing import List, Dict
from tqdm import tqdm
from groq import Groq
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.config import Config
from src.utils.document_loader import Document, DocumentLoader
from src.utils.vector_store import VectorStore

class EvalDataGenerator:
    """Generates synthetic evaluation data from documents."""
    
    def __init__(self, model: str = None):
        load_dotenv()
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = model or Config.GROQ_MODEL
        self.loader = DocumentLoader()
        self.vector_store = VectorStore(in_memory=True) # Used for chunking logic if needed

    def generate_qa_pair(self, context: str) -> Dict[str, str]:
        """Generate a Question-Answer pair from a given context."""
        prompt = f"""
        Given the following context from a document, generate a high-quality question and its corresponding answer.
        The question should be specific and answerable solely based on the context.
        The answer should be concise but complete.
        
        Context:
        ---
        {context}
        ---
        
        Return the result in JSON format:
        {{
            "question": "...",
            "answer": "..."
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that generates evaluation data for RAG systems. Return ONLY JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating QA pair: {e}")
            return None

    def generate_from_file(self, file_path: str, num_samples: int = 5) -> List[Dict]:
        """Load a file, chunk it, and generate samples."""
        print(f"Loading {file_path}...")
        docs = self.loader.load_pdf(file_path)
        
        # Combine and re-chunk for more context per sample if needed
        # Or just use pages. Let's use the VectorStore's chunking logic.
        full_text = " ".join([doc.content for doc in docs])
        chunks = self.vector_store._chunk_text(full_text, chunk_size=2000, overlap=200)
        
        samples = []
        # Limit to num_samples or available chunks
        num_to_generate = min(num_samples, len(chunks))
        
        print(f"Generating {num_to_generate} QA pairs...")
        for i in tqdm(range(num_to_generate)):
            context = chunks[i]
            qa = self.generate_qa_pair(context)
            if qa:
                qa["context"] = context
                qa["source"] = file_path
                samples.append(qa)
                
        return samples

    def save_to_jsonl(self, samples: List[Dict], output_path: str):
        """Save samples to a JSONL file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(json.dumps(sample) + "\n")
        print(f"Saved {len(samples)} samples to {output_path}")

if __name__ == "__main__":
    if not Config.GROQ_API_KEY:
        print("GROQ_API_KEY not found. Please set it in .env")
        sys.exit(1)
        
    generator = EvalDataGenerator()
    
    # Example: generate from the docker cheatsheet
    data_path = os.path.join("data", "docker_cheatsheet.pdf")
    if os.path.exists(data_path):
        eval_samples = generator.generate_from_file(data_path, num_samples=3)
        
        output_dir = "logs/eval"
        os.makedirs(output_dir, exist_ok=True)
        generator.save_to_jsonl(eval_samples, os.path.join(output_dir, "testset.jsonl"))
    else:
        print(f"File not found: {data_path}")
