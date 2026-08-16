"""CLI entry point"""
from tree_sitter import Language, Parser
import tree_sitter_python


PYTHON_LANGUAGE = Language(tree_sitter_python.language())

parser = Parser(PYTHON_LANGUAGE)

with open("data/test.py", "r") as file:
    source = file.read()

source = source.encode("utf-8")

tree = parser.parse(source)

root = tree.root_node

def extract(root, max_chunk_size):


    for child in root.named_children:

        # if child.type == "import_statement":
        #     continue

        size = child.end_byte - child.start_byte
        
        if size <= max_chunk_size:
            end = len(source[child.start_byte:child.end_byte].decode())
            print(
                {
                    "type": child.type,
                    "start_character_index": child.start_byte,
                    "end_character_index": end,
                    "size": end,
                    "text": source[child.start_byte:child.end_byte].decode()
                }
            )
        else:
            extract(child, max_chunk_size)


extract(root, 40)

