from transformers import pipeline
from transformers.utils.logging import set_verbosity_error
set_verbosity_error()
from .models import MinimalAnswer


class LLM:
    def __init__(self):
        self.pipeline = pipeline("text-generation", model="Qwen/Qwen3-0.6B")

    def answer(self, question, sources):

        prompt = [
            {
                "role": "system",
                "content": "Answer question using only context.\nIf there is no relation between question and contest say just'I do not know'"
            },
            {
                "role": "user",
                "content": f"\ncontext:{sources}\nquestion:{question}/no_think"
            }
        ]

        result: MinimalAnswer = self.pipeline(
                prompt,
                return_full_text=False
            )[0]['generated_text']

        return result.split("</think>", 1)[1].strip()

