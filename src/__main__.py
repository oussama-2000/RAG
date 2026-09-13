"""CLI entry point"""

from chunkers.code import CodeChunker
from chunkers.text import TextChunker
from models import StudentSearchResults
from reader import Reader
from indexer import RagPipeline
import time


reader = Reader("data/raw/vllm-0.10.1")
reader.read()
paths = reader.paths

max_chunk_size = 200
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

student_search: StudentSearchResults = index.get_search_result("data/datasets_public/public", 1)
print(len(student_search.search_results))

print(f"time: {time.time() - start}")


