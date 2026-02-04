
import json
from typing import Dict
from groq import Groq
from src.utils.config import Config

class LLMJudge:
    """Uses an LLM to evaluate the quality of RAG responses."""
    
    def __init__(self, model: str = None):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = model or Config.GROQ_MODEL

    def evaluate_correctness(self, question: str, ground_truth: str, generated_answer: str) -> Dict:
        """Evaluate how correct the generated answer is compared to the ground truth."""
        prompt = f"""
        Role: Expert Evaluator
        Task: Compare a "Generated Answer" against a "Ground Truth Answer" for a given "Question".
        
        Question: {question}
        Ground Truth Answer: {ground_truth}
        Generated Answer: {generated_answer}
        
        Scoring Criteria:
        1: Completely wrong or irrelevant.
        2: Major inaccuracies or missing key info.
        3: Partially correct but incomplete or has minor errors.
        4: Mostly correct with very minor omissions.
        5: Perfectly correct and complete.
        
        Return the result in JSON format:
        {{
            "score": <int 1-5>,
            "reasoning": "..."
        }}
        """
        
        return self._get_json_response(prompt)

    def evaluate_faithfulness(self, question: str, context: str, generated_answer: str) -> Dict:
        """Evaluate if the answer is derived ONLY from the provided context (no hallucinations)."""
        prompt = f"""
        Role: Fact-Checker
        Task: Evaluate if the "Generated Answer" is faithful to the "Context".
        
        Context: {context}
        Generated Answer: {generated_answer}
        
        Scoring Criteria:
        1: Answer contains significant information NOT present in the context.
        2: Answer is mostly faithful but adds external info.
        3: Partially correct but incomplete or has minor errors.
        4: Mostly correct with very minor omissions.
        5: Answer is entirely derived from and supported by the context.
        
        Return the result in JSON format:
        {{
            "score": <int 1-5>,
            "reasoning": "..."
        }}
        """
        return self._get_json_response(prompt)

    def _get_json_response(self, prompt: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an objective evaluation judge. Return ONLY JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error in LLM Judge: {e}")
            return {"score": 0, "reasoning": f"Error: {e}"}
