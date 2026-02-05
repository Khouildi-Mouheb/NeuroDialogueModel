import os
import sys

# Fix paths before any imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from groq import Groq

from infrastructure.agents.agent import Agent  # Changed from relative import

class GeneratorAgent(Agent):
    def __init__(self, model_name: str = "deepseek-r1-distill-llama-70b"):
        self.model_name = model_name
        api_key = os.getenv("GROQ_API_KEY", "REDACTED")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set!")
        
        self.client = Groq(api_key=api_key)

    def stream(self, prompt: str):



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
                    yield chunk.choices[0].delta.content

        except Exception as e:
            print(f"Error in GeneratorAgent: {str(e)}")
            yield f"[ERROR] {str(e)}"


if __name__ == "__main__":
    # Quick test
    print("🧪 Testing GeneratorAgent with Groq API...\n")
    
    try:

        agent = GeneratorAgent()
        
        print("🤖 Response: ", end="", flush=True)
        for token in agent.stream(prompt="What is AI? Answer in one sentence."):
            print(token, end="", flush=True)
        
        print("\n\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")