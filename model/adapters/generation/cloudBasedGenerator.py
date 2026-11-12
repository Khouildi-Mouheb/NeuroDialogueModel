import os
from typing import Iterator, Optional
from groq import Groq
from dotenv import load_dotenv
from domain.context.generatorContext import GeneratorContext
from domain.context.titleGenerationContext import TitleGenerationContext
from adapters.generation.generatorAgent import GeneratorAgent

load_dotenv()


class CloudBasedGenerator(GeneratorAgent):

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set!")

        self.client = Groq(api_key=api_key)

    # ------------------------------------------------------------------ #
    # Streaming                                                            #
    # ------------------------------------------------------------------ #

    def stream(self, context: GeneratorContext) -> Iterator[str]:
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
                    yield token
        except Exception as e:
            print(f"Error in stream: {str(e)}")
            yield f"[ERROR] {str(e)}"

    # ------------------------------------------------------------------ #
    # RAG response                                                         #
    # ------------------------------------------------------------------ #

    def generateFullResponse(self, context: GeneratorContext) -> str:
        prompt = context.format_context_for_prompt()
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3000,
                stream=False,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in generateFullResponse: {str(e)}")
            return f"[ERROR] {str(e)}"

    # ------------------------------------------------------------------ #
    # Greetings / simple social messages                                   #
    # ------------------------------------------------------------------ #

    def generateSimpleResponse(self, user_message: str, queryType: Optional[str] = None) -> str:
        prompt = (
            f"Generate a concise and friendly response to the following "
            f"{queryType} message: \"{user_message}\". Keep it under 20 words."
        )
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

    # ------------------------------------------------------------------ #
    # Internal utility: summarization and structured extraction            #
    # ------------------------------------------------------------------ #

    def generateFromPrompt(self, prompt: str, max_tokens: int = 1000) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=max_tokens,
                stream=False,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in generateFromPrompt: {str(e)}")
            return f"[ERROR] {str(e)}"

    # ------------------------------------------------------------------ #
    # Chat title generation                                                #
    # ------------------------------------------------------------------ #

    def generateTitle(self, context: TitleGenerationContext) -> str:
        prompt = context.format_context_for_prompt()
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=20,
                stream=False,
            )
            return completion.choices[0].message.content.strip().strip('"').strip("'")
        except Exception as e:
            print(f"Error in generateTitle: {str(e)}")
            return "New Conversation"