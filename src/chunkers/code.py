from tree_sitter import Language, Parser
import tree_sitter_python


class CodeChunker:

    def __init__(self, file, max_chunk_size):
        self.file = file
        self.max_chunk_size = max_chunk_size
        self.python_language = Language(tree_sitter_python.language())
        self.parser = Parser(self.python_language)
        self.source = None
        self.tree = None
        self.root = None
        self.nodes = []
        self.chunks = []

    def set_tree(self):

        with open(self.file, "r") as file:
            source = file.read()

        self.source = source.encode("utf-8")
        self.tree = self.parser.parse(self.source)
        self.root = self.tree.root_node

    def byte_to_char_index(self, source, byte_index):
        return len(source[:byte_index].decode())

    def set_nodes(self, node, level):

        for child in node.named_children:
            text = self.source[child.start_byte:child.end_byte].decode()
            size = len(text)

            if size <= self.max_chunk_size:
                start = self.byte_to_char_index(self.source, child.start_byte)
                end = self.byte_to_char_index(self.source, child.end_byte)

                self.nodes.append(
                    {
                        "level": level,
                        "type": child.type,
                        "first_character_index": start,
                        "last_character_index": end,
                        "size": size,
                        "text": text
                    }
                )
            else:
                self.set_nodes(child, level + 1)

    def set_chunks(self):
        self.set_tree()
        self.set_nodes(self.root, 0)
        i = 0

        chunk_id = 0
        while i < len(self.nodes):

            buffer = self.nodes[i]['size']

            current_chunk = {
                'id': chunk_id,
                'file_path': self.file,
                'first_character_index': self.nodes[i]['first_character_index'],
                'last_character_index': self.nodes[i]['last_character_index'],
                'text': self.nodes[i]['text']
            }

            j = i + 1
            while buffer < self.max_chunk_size and j < len(self.nodes):

                tmp = buffer + self.nodes[j]['size']

                if tmp > self.max_chunk_size:
                    break

                if self.nodes[i]['level'] == self.nodes[j]['level'] and self.nodes[j]['type'] != 'function_definition':
                    buffer += self.nodes[j]['size']
                    current_chunk['text'] += '\n' + self.nodes[j]['text']
                    current_chunk['last_character_index'] = self.nodes[j]['last_character_index']
                else:
                    break
                j += 1

            self.chunks.append(current_chunk)
            i = j
            chunk_id += 1
