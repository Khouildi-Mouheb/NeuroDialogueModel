import os
import sys
from groq import Groq
from dotenv import load_dotenv  

load_dotenv()  

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from infrastructure.agents.agent import Agent  # Changed from relative import
from infrastructure.agents.generatorAgent import GeneratorAgent

class CloudBasedGenerator(GeneratorAgent):
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set!")
        
        self.client = Groq(api_key=api_key)

    def stream(self, prompt: str):
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
            print(f"Error in GeneratorAgent: {str(e)}")
            yield f"[ERROR] {str(e)}"


