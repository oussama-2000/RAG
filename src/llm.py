from transformers import pipeline
# from transformers.utils.logging import set_verbosity_error
# set_verbosity_error()
# import os


test = pipeline("text-generation", model="Qwen/Qwen3-0.6B")
os.system("clear")

class LLM:
    def __init__(self):
        self.pipeline = pipeline("text-generation", model="Qwen/Qwen3-0.6B")

    def answer(self, question, sources):

        prompt = [
            {
                "role": "system",
                "content": "Answer question using only context"
            },
            {
                "role": "user",
                "content": f"/no_think\ncontext:{sources}\nquestion:{question}"
            }
        ]

        result = test(
                prompt,
                return_full_text=False
            )[0]['generated_text']

        return result.split("</think>", 1)[1].strip()

