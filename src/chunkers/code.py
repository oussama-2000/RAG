from tree_sitter import Language, Parser
import tree_sitter_python


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

        with open(self.file, "r") as file:
            source = file.read()

        self.source = source.encode("utf-8")
        self.tree = self.parser.parse(self.source)
        self.root = self.tree.root_node

    def byte_to_char_index(self, source, byte_index):
        return len(source[:byte_index].decode())

    def set_nodes(self, node, level):

        nodes = []

        for child in node.named_children:
            # if child.type in ["identifier", "parameter"]:
            #     continue

            text = self.source[child.start_byte:child.end_byte].decode()
            size = len(text)

            if size <= self.max_chunk_size:


                start = self.byte_to_char_index(self.source, child.start_byte)
                end = self.byte_to_char_index(self.source, child.end_byte)

                nodes.append(
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

        return nodes

    def set_chunks(self, file_path, max_chunk_size):
        self.file = file_path
        self.max_chunk_size = max_chunk_size
        self.set_tree()
        nodes = self.set_nodes(self.root, 0)

        i = 0

        while i < len(nodes):

            buffer = nodes[i]['size']

            current_chunk = {
                'id': None,
                'file_path': self.file,
                'first_character_index': nodes[i]['first_character_index'],
                'last_character_index': nodes[i]['last_character_index'],
                'text': nodes[i]['text']
            }

            j = i + 1
            while buffer < self.max_chunk_size and j < len(nodes):

                tmp = buffer + nodes[j]['size']

                if tmp > self.max_chunk_size:
                    break

                if nodes[i]['level'] == nodes[j]['level'] and nodes[j]['type'] != 'identifier':
                    buffer += nodes[j]['size']
                    current_chunk['text'] += '\n' + nodes[j]['text']
                    current_chunk['last_character_index'] = nodes[j]['last_character_index']
                else:
                    break
                j += 1

            yield current_chunk
            i = j
