import requests
import json
from core.context.generatorContext import GeneratorContext
from core.domain.agent import Agent
from .generatorAgent import GeneratorAgent

class LocalBasedGenerator(Agent):
    def __init__(self, model_name: str = "deepseek-r1:7b"):
        self.model_name = model_name
        self.base_url = "http://127.0.0.1:11434/api/generate"

    def stream(self, context: GeneratorContext):
        print('starting the stream')
        prompt = context.format_context_for_prompt()

        try:
            with requests.post(
                self.base_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": True,
                    "options": {"num_predict": 300},
                },
                stream=True,
                timeout=600,
            ) as response:

                # 🔴 DO NOT raise_for_status()
                if response.status_code != 200:
                    yield "[ERROR] Ollama returned an error."
                    return

                for line in response.iter_lines():
                    if not line:
                        continue

                    try:
                        data = json.loads(line.decode("utf-8"))
                    except json.JSONDecodeError:
                        continue

                    if data.get("done"):
                        break

                    yield data.get("response", "")

        except Exception as e:
            yield f"[ERROR] {str(e)}"