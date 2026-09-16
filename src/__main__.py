"""CLI entry point"""

from chunkers.code import CodeChunker
from chunkers.text import TextChunker
from models import StudentSearchResults
from reader import Reader
from indexer import RagPipeline
from recall_evaluation import Recall
import time
import os
import json



reader = Reader("data/raw/vllm-0.10.1")
reader.read()
paths = reader.paths

max_chunk_size = 2000
code_chunker = CodeChunker()
text_chunker = TextChunker()

all_chunks = []

start = time.time()

for file in paths:
    # if file.suffix.lower() == ".py":
    #     chunks = code_chunker.set_chunks(str(file), max_chunk_size)
    #     for chunk in chunks:
    #         all_chunks.append(chunk)


    if file.suffix.lower() in [".txt", ".md"]:
        chunks = text_chunker.set_chunks(str(file), max_chunk_size)
        for chunk in chunks:
            # all_chunks.append(chunk)
            print(chunk)

exit()
index = RagPipeline()

index.ingest(all_chunks, "data/processed/indexed_chunks")

# retrival
index.load("data/processed/indexed_chunks")
k = 5
student_search: StudentSearchResults = index.get_search_result("data/datasets_public/public/UnansweredQuestions", k)

index.save_searching_output(student_search, k)

evaluation = Recall()

recalls = 0
questions_number = 0

with open("data/datasets_public/public/AnsweredQuestions/dataset_docs_public.json", "r") as reference:
    with open("data/search_results/dataset_docs_public.json", "r") as retrived:

        reference_content = json.load(reference)
        retrived_content = json.load(retrived)

        questions_number = len(reference_content['rag_questions'])
        for r_question in reference_content['rag_questions']:
            for r_result in retrived_content['search_results']:
                if r_question['question_id'] == r_result['question_id']:
                    recalls += evaluation.recall_calculation(r_question['sources'], r_result['retrived_sources'])

print(f"{(recalls / questions_number) * 100} %")


print(f"time: {time.time() - start}")
