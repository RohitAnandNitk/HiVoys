from abc import ABC, abstractmethod

class BaseLLM(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def get_model(self):
        """Return the LLM model instance."""
        pass