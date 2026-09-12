"""CLI entry point"""

from chunkers.code import CodeChunker
from chunkers.text import TextChunker
from models import RagDataset, StudentSearchResults, MinimalSearchResults
from reader import Reader
from indexer import BM25Indexer
import json
import time
from pathlib import Path


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



index = BM25Indexer()

index.ingest(all_chunks, "data/processed/code_chunks")

# retrival
index.load("data/processed/code_chunks")


student_search: StudentSearchResults = index.get_search_result("data/datasets_public/public", 1)

print(f"time: {time.time() - start}")


