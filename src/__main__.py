"""CLI entry point"""

from chunkers.code import CodeChunker
from chunkers.text import TextChunker
import json

max_chunk_size = 100
code_chunker = CodeChunker("data/test.py", max_chunk_size)
text_chunker = TextChunker("data/test.md", max_chunk_size)

code_chunker.set_chunks()

with open("src/chunkers/chunks/code.json", "w") as file:
    file.write("[")
    i = 0
    length = len(code_chunker.chunks)
    for chunk in code_chunker.chunks:
        json.dump(chunk, file, indent=4)
        if i < length - 1:
            file.write(",")
        i+= 1
    file.write("]")  

text_chunker.set_chunks()

with open("src/chunkers/chunks/text.json", "w") as file:
    file.write("[")
    i = 0
    length = len(text_chunker.chunks)
    for chunk in text_chunker.chunks:
        json.dump(chunk, file, indent=4)
        if i < length - 1:
            file.write(",")
        i+= 1
    file.write("]")

