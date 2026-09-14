"""CLI entry point"""

from chunkers.code import CodeChunker
from chunkers.text import TextChunker
from models import StudentSearchResults
from reader import Reader
from indexer import RagPipeline
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
    if file.suffix.lower() == ".py":
        chunks = code_chunker.set_chunks(str(file), max_chunk_size)
        for chunk in chunks:
            all_chunks.append(chunk)


    elif file.suffix.lower() in [".txt", ".md"]:
        chunks = text_chunker.set_chunks(str(file), max_chunk_size)
        for chunk in chunks:
            all_chunks.append(chunk)

index = RagPipeline()

index.ingest(all_chunks, "data/processed/indexed_chunks")

# retrival
index.load("data/processed/indexed_chunks")

student_search: StudentSearchResults = index.get_search_result("data/datasets_public/public/UnansweredQuestions", 3)

os.makedirs("data/search_results", exist_ok=True)

content = {"search_results": [], "k": 3}


for result in student_search.search_results:
    sources = []

    for source in result.retrieved_sources:

            sources.append({
                "file_path": source.file_path,
                "first_character_index": source.first_character_index,
                "last_character_index": source.last_character_index
            })

    content['search_results'].append({
        "question_id": result.question_id,
        "question": result.question,
        "retrived_sources": sources
    })

      

        
with open("data/search_results/dataset_docs_public.json", "w") as file:
    json.dump(content, file, indent=4)


print(f"time: {time.time() - start}")
