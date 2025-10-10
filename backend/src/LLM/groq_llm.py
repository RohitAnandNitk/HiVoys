# src/LLM/groq_llm.py
import os
from groq import Groq

class GroqLLM:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        # Use fastest model for lowest latency
        self.model_name = "llama-3.1-8b-instant"
    
    def get_model(self):
        return self
    
    def stream(self, user_message):
        """
        Stream response token by token for ultra-low latency.
        Yields each chunk as it arrives.
        """
        messages = [
            {
                "role": "system",
                "content": "You are a professional interviewer nad your name is Kavita. Keep responses concise and conversational. Name of the interviewee is Rohit and your are going to ask about his educataion background. and you will start the conversation first."

            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=120,
                stream=True  # Enable streaming
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"❌ Groq streaming error: {e}")
            raise
    
    def invoke(self, messages):
        """
        Non-streaming fallback for compatibility.
        """
        formatted_messages = [
            {
                "role": "system",
                "content": "You are a professional interviewer. Keep responses concise, clear, and conversational. Aim for 2-3 sentences maximum."
            }
        ]
        
        for msg in messages:
            if isinstance(msg, dict):
                formatted_messages.append(msg)
            else:
                formatted_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", str(msg))
                })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=120,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            raise