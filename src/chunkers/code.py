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
        self.python_language = Language(tree_sitter_python.language())
        self.parser = Parser(self.python_language)
        self.source = None
        self.tree = None
        self.root = None

    def set_tree(self, file_path):

        with open(file_path, "r", encoding="utf-8") as file:
            source = file.read()

        self.source = source.encode("utf-8")
        self.tree = self.parser.parse(self.source)
        self.root = self.tree.root_node


    def byte_to_char_index(self, source, byte_index):
        return len(source[:byte_index].decode("utf-8"))


    def extract_nodes(self, node, max_chunk_size):
        nodes = []

        for child in node.named_children:

            text = self.source[child.start_byte:child.end_byte].decode("utf-8")
            size = len(text)

            if size <= max_chunk_size:

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
                        "first_character_index": start,
                        "last_character_index": end,
                        "text": text
                    }
                )

            else:
                nodes.extend(
                    self.extract_nodes(child, max_chunk_size)
                )

        return nodes


    def extract_chunks(self, file_path, max_chunk_size):

        self.set_tree(file_path)

        nodes = self.extract_nodes(self.root, max_chunk_size)
    
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

                new_size = next_node['last_character_index'] - first_index

                if new_size > max_chunk_size - 1:
                    break

                text += " " + next_node["text"]

                size = new_size
                last_index = next_node["last_character_index"]

                j += 1
            
            yield {
                "size": size,
                "file_path": file_path,
                "first_character_index": first_index,
                "last_character_index": last_index,
                "text": text
            }

            i = j


