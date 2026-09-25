"""CLI entry point"""

from chunkers.code import CodeChunker
from chunkers.text import TextChunker
from models import StudentSearchResults
from reader import Reader
from indexer import RagPipeline
from recall_evaluation import Recall


max_chunk_size = 2000

index = RagPipeline()

index.ingest("data/processed/indexed_chunks", max_chunk_size)

# retrival
index.load("data/processed/indexed_chunks")
k = 1
student_search: StudentSearchResults = index.get_search_result("data/datasets_public/public/UnansweredQuestions", k)

index.save_searching_output(student_search, k)

# evaluation = Recall()

# evaluation.evaluate("data/search_results/dataset_docs_public.json", "data/datasets_public/public/AnsweredQuestions/dataset_docs_public.json")

from llm import test

resources = []

i = 0
for result in student_search.search_results:
    if i == 1:
        break
    resources.append([source.text for source in result.retrieved_sources])
    i += 1

qeustion = "What HTTP endpoint is used to dynamically load a LoRA adapter in vLLM?"
print("====>",
    test(
        f"""
            you are a system that takes resources and question as a inputs, and you should answer the question from the provided resourced only.

            Resources:
            {{{resources}}}

            Qeustion:
            {{{qeustion}}}

            #Answer:

        """,
        max_new_tokens=100,
        do_sample=False,
        return_full_text=False
    )[0]['generated_text']
)





