"""
CloudBasedGenerator - Adapter implementing LLMPort using Groq API.
"""
import os
from groq import Groq
from ports.llm_port import LLMPort


class CloudBasedGenerator(LLMPort):
    """Concrete implementation of LLMPort using Groq cloud API."""
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set!")
        
        self.client = Groq(api_key=api_key)

    def stream(self, prompt: str):
        """Stream text generation using Groq API."""
        print('start streaming ! ')

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300,
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content)
                    yield chunk.choices[0].delta.content

        except Exception as e:
            print(f"Error in CloudBasedGenerator: {str(e)}")
            yield f"[ERROR] {str(e)}"
