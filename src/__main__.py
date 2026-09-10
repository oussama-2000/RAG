"""CLI entry point"""

from chunkers.code import CodeChunker
from chunkers.text import TextChunker
import json

max_chunk_size = 50

code_chunker = CodeChunker("data/test.py", max_chunk_size)
text_chunker = TextChunker("data/test.md", max_chunk_size)

code_chunker.set_chunks()

code_chunks = []
# with open("src/chunkers/chunks/code.json", "w") as file:

for chunk in code_chunker.chunks:
    # json.dump(chunk, file, indent=4)
    code_chunks.append(chunk)



from indexer import BM25Indexer

index = BM25Indexer()

#ingest
index.build(code_chunks)
index.save("databytes")


index.load("databytes")

print(index.chunks)
print(index.tokenized_chunks)
print(index.bm25)
index.search("sum function")

