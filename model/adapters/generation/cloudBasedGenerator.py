import os
from typing import Iterator
from groq import Groq
from dotenv import load_dotenv
from domain.context.generatorContext import GeneratorContext
from adapters.generation.generatorAgent import GeneratorAgent
from typing import Optional

load_dotenv()


class CloudBasedGenerator(GeneratorAgent):

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set!")

        self.client = Groq(api_key=api_key)

    # ------------------------------------------------------------------ #
    # GenerationPort implementation                                        #
    # ------------------------------------------------------------------ #

    def stream(self, context: GeneratorContext) -> Iterator[str]:
        print("start streaming!")
        prompt = context.format_context_for_prompt()

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
                stream=True,
            )

            for chunk in completion:
                token = chunk.choices[0].delta.content
                if token:
                    print(token)
                    yield token

        except Exception as e:
            print(f"Error in CloudBasedGenerator: {str(e)}")
            yield f"[ERROR] {str(e)}"

    def generateFullResponse(self, context: GeneratorContext) -> str:
        """Generate a complete response in one shot (no streaming)."""
        print("start generating full response!")
        prompt = context.format_context_for_prompt()

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
                stream=False,
            )
            return completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error in CloudBasedGenerator: {str(e)}")
            return f"[ERROR] {str(e)}"
        

    def generateSimpleResponse(self, user_message: str, queryType: Optional[str] = None) -> str:
            prompt = f"Generate a concise and friendly response to the following {queryType} message: \"{user_message}\". Keep it under 20 words."
            try:
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=50,
                    stream=False,
                )
                return completion.choices[0].message.content.strip()

            except Exception as e:
                print(f"Error in generateSimpleResponse: {str(e)}")
                return f"[ERROR] {str(e)}"