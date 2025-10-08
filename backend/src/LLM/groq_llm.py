import os
from dotenv import load_dotenv
from base import BaseLLM

from langchain_groq import ChatGroq  # Assuming langchain-groq is installed

# Load environment variables from .env
load_dotenv()

class GroqLLM(BaseLLM):
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"): # llama3-70b-8192 ,  llama3-70b-4096 , llama-3.3-70b-versatile
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        super().__init__(model_name)
        self.api_key = api_key

    def get_model(self):
        return ChatGroq(
            api_key=self.api_key,
            model_name=self.model_name,
            temperature=0
        )

if __name__ == "__main__":
    print("🧠 HiVoys (LangChain + Groq)")
    groq =  GroqLLM()
    groq_model = groq.get_model()
    user_input = input("Ask HiVoys: ")
    response = groq_model.invoke(user_input)
    print("\nHiVoys:", response.content)