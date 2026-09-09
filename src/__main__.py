"""CLI entry point"""

from chunkers.code import CodeChunker
from chunkers.text import TextChunker
import json

max_chunk_size = 100
code_chunker = CodeChunker("data/test.py", max_chunk_size)
text_chunker = TextChunker("data/test.md", max_chunk_size)

# code_chunker.set_chunks()
# code_chunks = []
# with open("src/chunkers/chunks/code.json", "w") as file:
#     for chunk in code_chunker.chunks:
#         code_chunks.append(json.dumps(chunk))
#     json.dump(code_chunks, file, indent=4)   

text_chunker.set_chunks()
text_chunks = []
with open("src/chunkers/chunks/text.json", "w") as file:
    for chunk in text_chunker.chunks:
        text_chunks.append(chunk)
    #     text_chunks.append(json.dumps(chunk))
    # json.dump(text_chunks, file, indent=4)

from rank_bm25 import BM25Okapi

documents = [
    document['text']
    for document in text_chunks
]

tokenized_documents = [
    document['text'].lower().split()
    for document in text_chunks
]

bm25 = BM25Okapi(tokenized_documents)

query = "how to install "
tokenized_query = query.lower().split()

scores = bm25.get_scores(tokenized_query)

scores = bm25.get_top_n(tokenized_query, documents, n=1)
print(scores)