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


def byte_to_char_index(source, byte_index):
    return len(source[:byte_index].decode())


def extract(root, max_chunk_size):

    for child in root.named_children:

        size = len(source[child.start_byte:child.end_byte].decode())

        if size <= max_chunk_size:
            start = byte_to_char_index(source, child.start_byte)
            end = byte_to_char_index(source, child.end_byte)
            text = source[child.start_byte:child.end_byte].decode()

            print(
                {
                    "type": child.type,
                    "start_character_index": start,
                    "end_character_index": end,
                    "size": size,
                    "text": text
                }
            )

        else:
            extract(child, max_chunk_size)

extract(root, 20)


