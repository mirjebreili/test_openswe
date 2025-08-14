import yaml
import json
import logging
from typing import List, Dict, Any
from local_agent_sr.agents.llm_manager import LLMManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ScreeningAgent:
    """
    Loads screening criteria, evaluates document chunks, and makes inclusion decisions.
    """
    def __init__(self, llm_manager: LLMManager, criteria_path: str):
        """
        Initializes the ScreeningAgent.

        Args:
            llm_manager (LLMManager): The LLM manager to use for evaluations.
            criteria_path (str): Path to the YAML file with inclusion/exclusion criteria.
        """
        self.llm_manager = llm_manager
        self.criteria = self._load_criteria(criteria_path)

    def _load_criteria(self, criteria_path: str) -> Dict[str, Any]:
        """Loads the screening criteria from a YAML file."""
        try:
            with open(criteria_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Error loading criteria from {criteria_path}: {e}")
            raise

    def _evaluate_chunk(self, chunk: Dict, criterion: Dict) -> Dict:
        """Evaluates a single chunk against a single criterion."""
        prompt = f"""
        System: You are a rigorous evidence checker. Answer in JSON only.
        User: Criterion: "{criterion['description']}"
        Chunk (with page markers): {chunk['content']}

        Return:
        {{
          "status": "true|false|unknown",
          "reason": "<brief>",
          "evidence_sentence": "<verbatim from chunk>",
          "page": <int or [ints]>
        }}
        Rules: quote verbatim; if not explicit → "unknown".
        """
        response_str = self.llm_manager.invoke(prompt)
        try:
            return json.loads(response_str)
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON response: {response_str}")
            return {"status": "error", "reason": "Invalid JSON response"}

    def screen_document(self, chunks: List[Dict]) -> Dict:
        """Screens a document (represented by its chunks) against all criteria."""
        results = {"inclusion": [], "exclusion": []}
        for criterion in self.criteria.get('inclusion_criteria', []):
            for chunk in chunks:
                eval_result = self._evaluate_chunk(chunk, criterion)
                results["inclusion"].append({"criterion_id": criterion['id'], **eval_result})
        
        for criterion in self.criteria.get('exclude_criteria', []):
            for chunk in chunks:
                eval_result = self._evaluate_chunk(chunk, criterion)
                results["exclusion"].append({"criterion_id": criterion['id'], **eval_result})
