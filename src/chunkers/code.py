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

    def tree_parse(self):

        with open(self.file, "r") as f:
            source = f.read()

        self.source = source.encode("utf-8")
        self.tree = self.parser.parse(self.source)
        self.root = self.tree.root_node

    def byte_to_char_index(self, source, byte_index):
        return len(source[:byte_index].decode())

    def extract(self, node, level):

        for child in node.named_children:
            size = len(self.source[child.start_byte:child.end_byte].decode())

            if size <= self.max_chunk_size:
                start = self.byte_to_char_index(self.source, child.start_byte)
                end = self.byte_to_char_index(self.source, child.end_byte)
                text = self.source[child.start_byte:child.end_byte].decode()

                self.nodes.append(
                    {
                        "level": level,
                        "type": child.type,
                        "start_character_index": start,
                        "end_character_index": end,
                        "size": size,
                        "text": text
                    }
                )
            else:
                self.extract(child, level + 1)

    def chunks_generator(self):

        i = 0

        while i < len(self.nodes):

            storage = self.nodes[i]['size']

            current_chunk = {
                'start_character_index': self.nodes[i]['start_character_index'],
                'end_character_index': self.nodes[i]['end_character_index'],
                'text': self.nodes[i]['text']
            }

            j = i + 1
            while storage < self.max_chunk_size and j < len(self.nodes):

                tmp = storage + self.nodes[j]['size']

                if tmp > self.max_chunk_size:
                    break

                if self.nodes[i]['level'] == self.nodes[j]['level']:
                    storage += self.nodes[j]['size']
                    current_chunk['text'] += '\n' + self.nodes[j]['text']
                    current_chunk['end_character_index'] = self.nodes[j]['end_character_index']
                else:
                    break
                j += 1

            self.chunks.append(current_chunk)
            i = j
