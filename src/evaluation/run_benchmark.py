
import sys
import os
import json
import asyncio
from typing import List, Dict
from tqdm import tqdm

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.config import Config
from src.utils.vector_store import VectorStore
from src.utils.document_loader import Document, DocumentLoader
from src.agents.research_agent import agent
from src.models.schemas import ResearchDeps
from src.evaluation.judges import LLMJudge

async def run_benchmark(testset_path: str):
    print(f"--- Starting Benchmark: {testset_path} ---")
    
    # 1. Load testset
    samples = []
    with open(testset_path, 'r', encoding='utf-8') as f:

        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    
    if not samples: 
        print("No samples found.")
        return

    # 2. Setup Vector Store with in-memory storage for the benchmark
    print("Pre-loading documents into vector store...")
    vs = VectorStore(collection_name="benchmark_collection", in_memory=True)
    loader = DocumentLoader()
    
    # Get unique sources from samples
    sources = list(set([s["source"] for s in samples]))
    for source in sources:
        if source.endswith(".pdf"):
            docs = loader.load_pdf(source)
            vs.add_documents(docs)
    
    # 3. Initialize Agent Dependencies
    deps = ResearchDeps(api_key=Config.GROQ_API_KEY, vector_store=vs)
    judge = LLMJudge()
    
    results = []
    
    # 4. Run Evaluation
    print(f"Evaluating {len(samples)} samples...")
    for sample in tqdm(samples):
        question = sample["question"]
        ground_truth = sample["answer"]
        context = sample["context"]
        
        # Get Agent Answer
        try:
            agent_result = await agent.run(question, deps=deps)
            generated_answer = agent_result.output
        except Exception as e:
            print(f"Error running agent for '{question}': {e}")
            generated_answer = "ERROR"
            
        # Run Judge
        correctness = judge.evaluate_correctness(question, ground_truth, generated_answer)
        faithfulness = judge.evaluate_faithfulness(question, context, generated_answer)
        
        results.append({
            "question": question,
            "ground_truth": ground_truth,
            "generated_answer": generated_answer,
            "correctness_score": correctness["score"],
            "correctness_reasoning": correctness["reasoning"],
            "faithfulness_score": faithfulness["score"],
            "faithfulness_reasoning": faithfulness["reasoning"]
        })

    # 5. Report Results
    avg_correctness = sum(r["correctness_score"] for r in results) / len(results)
    avg_faithfulness = sum(r["faithfulness_score"] for r in results) / len(results)
    
    print("\n--- Benchmark Results ---")
    print(f"Average Correctness: {avg_correctness:.2f}/5")
    print(f"Average Faithfulness: {avg_faithfulness:.2f}/5")
    
    # Save results
    output_path = "logs/eval/benchmark_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "average_correctness": avg_correctness,
            "average_faithfulness": avg_faithfulness,
            "detailed_results": results
        }, f, indent=2)
    print(f"Detailed results saved to {output_path}")

if __name__ == "__main__":
    testset = "logs/eval/testset.jsonl"
    if os.path.exists(testset):
        asyncio.run(run_benchmark(testset))
    else:
        print(f"Testset not found: {testset}")
