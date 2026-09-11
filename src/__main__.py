"""CLI entry point"""

from chunkers.code import CodeChunker
from chunkers.text import TextChunker
from models import MinimalSource
from reader import Reader
from indexer import BM25Indexer
import json

reader = Reader("data/raw/vllm-0.10.1")
reader.read()
paths = reader.paths

max_chunk_size = 2000
code_chunker = CodeChunker()
text_chunker = TextChunker()


with open("chunks_storage", "w") as storage:
    index = 0
    for file in paths:
        if file.suffix.lower() == ".py":
            chunks = code_chunker.set_chunks(str(file), max_chunk_size)
            for chunk in chunks:
                chunk['id'] = index
                storage.write(str(chunk) + "\n")
                index += 1

        elif file.suffix.lower() in [".txt", ".md"]:
            chunks = text_chunker.set_chunks(str(file), max_chunk_size)
            for chunk in chunks:
                chunk['id'] = index
                storage.write(str(chunk) + "\n")
                index += 1       

# index = BM25Indexer()
# # with open("chunks_storage", "r") as storage:

#     #ingest
# index.ingest(chunks_storage, "data/processed/code_chunks")

# # retrival
# index.load("data/processed/code_chunks")
# chunks = index.search("test class", 1)
# print(chunks)


