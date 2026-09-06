"""CLI entry point"""

from chunkers.code import CodeChunker

# chunker = CodeChunker("data/test.py", 50)
# chunker.tree_parse()
# chunker.extract(chunker.root, 0)
# chunker.chunks_generator()

# for chunk in chunker.chunks:
#     print(chunk)

from chunkers.text import process


process()