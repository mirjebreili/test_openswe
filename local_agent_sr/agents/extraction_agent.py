import yaml
import json
import logging
from typing import List, Dict, Any
from local_agent_sr.agents.llm_manager import LLMManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExtractionAgent:
    """
    Loads data extraction schema and extracts structured data from documents.
    """
    def __init__(self, llm_manager: LLMManager, schema_path: str):
        """
        Initializes the ExtractionAgent.

        Args:
            llm_manager (LLMManager): The LLM manager to use for extractions.
            schema_path (str): Path to the YAML file with the data extraction schema.
        """
        self.llm_manager = llm_manager
        self.schema = self._load_schema(schema_path)

    def _load_schema(self, schema_path: str) -> Dict[str, Any]:
        """Loads the data extraction schema from a YAML file."""
        try:
            with open(schema_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Error loading schema from {schema_path}: {e}")
            raise

    def _extract_from_chunk(self, chunk: Dict, feature: Dict) -> Dict:
        """Extracts a single feature from a single chunk."""
        prompt = f"""
        System: You extract structured facts with citations. Answer in JSON only.
        User: Feature "{feature['feature_name']}": {feature['description']}
        Chunk (with page markers): {chunk['content']}

        Return:
        {{
          "candidates": [
            {{"value": ..., "unit": "...?", "evidence_sentence": "<verbatim>", "page": <int or [ints]>}}
          ]
        }}
        Rules: only explicit facts; no inference; return empty list if absent.
        """
        response_str = self.llm_manager.invoke(prompt)
        try:
            return json.loads(response_str)
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON response: {response_str}")
            return {"candidates": []}

    def extract_data(self, chunks: List[Dict]) -> Dict:
        """Extracts data for all features from a document (represented by its chunks)."""
        extracted_data = {}
        for feature in self.schema.get('extraction_features', []):
            feature_name = feature['feature_name']
            extracted_data[feature_name] = []
            for chunk in chunks:
                candidates = self._extract_from_chunk(chunk, feature)
