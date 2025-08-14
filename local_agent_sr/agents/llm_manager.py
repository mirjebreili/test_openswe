import ollama
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LLMManager:
    """
    Manages interactions with the Ollama model, including setup and invocation.
    """
    def __init__(self, model_name: str):
        """
        Initializes the LLMManager.

        Args:
            model_name (str): The name of the Ollama model to use.
        """
        self.model_name = model_name
        self.context_length = None
        self._setup_model()

    def _is_model_available(self) -> bool:
        """Checks if the specified model is available locally."""
        try:
            models = ollama.list().get('models', [])
            return any(model['name'] == self.model_name for model in models)
        except Exception as e:
            logging.error(f"Error checking for model availability: {e}")
            return False

    def _pull_model(self):
        """Pulls the model from the Ollama registry if it's not available locally."""
        logging.info(f"Model '{self.model_name}' not found locally. Pulling...")
        try:
            ollama.pull(self.model_name)
            logging.info(f"Successfully pulled model '{self.model_name}'.")
        except Exception as e:
            logging.error(f"Failed to pull model '{self.model_name}': {e}")
            raise

    def _get_context_length(self) -> int:
        """Retrieves the context length of the model, defaulting to 4096 if not found."""
        try:
            model_info = ollama.show(self.model_name)
            params = model_info.get('parameters', '')
            for line in params.split('\n'):
                if 'context_length' in line:
                    return int(line.split()[-1])
            logging.warning("Could not determine context length. Defaulting to 4096.")
            return 4096
        except Exception as e:
            logging.error(f"Error getting model info: {e}. Defaulting to 4096.")
            return 4096

    def _setup_model(self):
        """Ensures the model is available and retrieves its context length."""
        if not self._is_model_available():
            self._pull_model()
        self.context_length = self._get_context_length()
        logging.info(f"Model '{self.model_name}' is ready. Context length: {self.context_length}")

    def invoke(self, prompt: str) -> str:
        """Invokes the LLM with a given prompt and returns the response."""
        try:
