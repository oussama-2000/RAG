
class TextChunker:
    def __init__(self):
        self.file = None
        self.max_chunk_size = 0
        self.source = None

    def set_nodes(self):
        with open(self.file) as file:
            self.source = file.readlines()

        nodes = []
        i = 0

        while i < len(self.source):

            state = "par"

            buffer = self.source[i]

            if self.source[i].startswith("#"):
                state = "title"

            j = i + 1
            while j < len(self.source):

                if len(buffer) > self.max_chunk_size:
                    cut_index = 0
                    t = buffer[:self.max_chunk_size]

                    if "." in t:
                        cut_index = t.rindex(".") + 1
                    elif "," in t:
                        cut_index = t.rindex(",") + 1
                    elif " " in t:
                        cut_index = t.rindex(" ") + 1
                    else:
                        cut_index = self.max_chunk_size

                    text = buffer[:cut_index]
                    nodes.append({
                        "type": state,
                        "size": len(text),
                        "text": text
                    })
                    buffer = buffer[cut_index:]

                    continue

                if state == "title":
                    break

                if state == "par" and self.source[j].startswith("#"):
                    break

                buffer += self.source[j]

                j += 1
            nodes.append(
                {
                    "type": state,
                    "size": len(buffer),
                    "text": buffer
                }
            )
            i = j

        return nodes

    
    def set_chunks(self, file_path, max_chunk_size):
        self.file = file_path
        self.max_chunk_size = max_chunk_size
        nodes = self.set_nodes()
        
        i = 0

        start, end = (0, 0)
        while i < len(nodes):
            buffer = nodes[i]['text']

            j = i + 1
            while j < len(nodes):

                if nodes[j]['type'] == "title":
                    break
                if len(buffer + nodes[j]['text']) < max_chunk_size:
                    buffer += nodes[j]['text']
                    j += 1
                else:
                    break
            i = j

            end += len(buffer)

            yield (
                {
                    "id": None,
                    "file_path": self.file,
                    "first_character_index": start,
                    "last_character_index": end,
                    "text": buffer
                } 
            )
            start += len(buffer)
