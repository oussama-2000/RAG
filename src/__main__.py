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
k = 5
student_search: StudentSearchResults = index.get_search_result("data/datasets_public/public/UnansweredQuestions", k)

# index.save_searching_output(student_search, k)

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

qeustion = "Where can I find vLLM setup and installation instructions for Google TPU?"
print(
    test(
        f"""
            you are given a list of resources.
            you are given a question.
            
            answer the question from the resources lis.

            resources:
            {{{resources}}}

            #Task:
            {{{qeustion}}}

            #Answer:

        """,
        max_new_tokens=40,
        do_sample=False,
        return_full_text=False
    )[0]['generated_text']
)





