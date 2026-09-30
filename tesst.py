from src.chunkers.code import CodeChunker

chunker = CodeChunker()

chunks  = chunker.set_chunks("data/raw/vllm-0.10.1/setup.py", 2000)

for chunk in chunks:
    print(chunk['first_character_index'] , chunk['last_character_index'],chunk['last_character_index']- chunk['first_character_index'], chunk['size'])