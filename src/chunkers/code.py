from tree_sitter import Language, Parser
import tree_sitter_python
"""
tree_sitter: incremental parsing library, parses source code into concrete syntax trees.
Parser: the object that takes source code and produces a CST based on the assigned grammar. 
Language: object that provides the parsing rules for specific programming language.
tree_sitter_python: python grammar for tree_sitter
"""


class CodeChunker:

    def __init__(self):
        self.file = None
        self.max_chunk_size = 0
        self.python_language = Language(tree_sitter_python.language())
        self.parser = Parser(self.python_language)
        self.source = None
        self.tree = None
        self.root = None

    def set_tree(self):

        with open(self.file, "r", encoding="utf-8") as file:
            source = file.read()

        self.source = source.encode("utf-8")
        self.tree = self.parser.parse(self.source)
        self.root = self.tree.root_node

    def byte_to_char_index(self, source, byte_index):
        return len(source[:byte_index].decode("utf-8"))

    def set_nodes(self, node, level):

        nodes = []

        for child in node.named_children:

            text = self.source[child.start_byte:child.end_byte].decode("utf-8")
            size = len(text)

            if size <= self.max_chunk_size:

                start = self.byte_to_char_index(
                    self.source,
                    child.start_byte
                )

                end = self.byte_to_char_index(
                    self.source,
                    child.end_byte
                )

                nodes.append(
                    {
                        "size": size,
                        "level": level,
                        "type": child.type,
                        "file_path": self.file,
                        "first_character_index": start,
                        "last_character_index": end,
                        "text": text
                    }
                )

            else:
                nodes.extend(
                    self.set_nodes(child, level + 1)
                )

        return nodes

    def set_chunks(self, file_path, max_chunk_size):

        self.file = file_path
        self.max_chunk_size = max_chunk_size

        self.set_tree()

        nodes = self.set_nodes(self.root, 0)

        i = 0

        while i < len(nodes):

            first_node = nodes[i]

            text = first_node["text"]
            size = first_node["size"]

            first_index = first_node["first_character_index"]
            last_index = first_node["last_character_index"]

            j = i + 1

            while j < len(nodes):

                next_node = nodes[j]

                new_size = size + next_node["size"]

                if new_size > self.max_chunk_size:
                    break


                text += "\n" + next_node["text"]

                size = new_size
                last_index = next_node["last_character_index"]

                j += 1

            yield {
                "size": size,
                "file_path": self.file,
                "first_character_index": first_index,
                "last_character_index": last_index,
                "text": text
            }

            i = j


