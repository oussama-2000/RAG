"""CLI entry point"""

from chunkers.code import CodeChunker
from chunkers.text import TextChunker
from models import MinimalSource
import json

max_chunk_size = 100

code_chunker = CodeChunker("data/test.py", max_chunk_size)
text_chunker = TextChunker("data/test.md", max_chunk_size)

code_chunker.set_chunks()

code_chunks = []

for chunk in code_chunker.chunks:
    code_chunks.append(chunk)



from indexer import BM25Indexer

index = BM25Indexer()

#ingest
index.ingest(code_chunks, "data/processed/code_chunks")

# retrival
index.load("data/processed/code_chunks")
chunks = index.search("test class", 1)
print(chunks)

for chunk in chunks:
    MinimalSource(**chunk)


