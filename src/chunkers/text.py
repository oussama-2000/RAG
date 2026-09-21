
class TextChunker:
    def __init__(self):
        pass

    def set_chunks(self, file_path, max_chunk_size):


        with open(file_path, encoding="utf-8") as file:
            source = file.read()

        start = 0

        while start < len(source):

            end = min(start + max_chunk_size, len(source))
            chunk_text = source[start:end]

            if end < len(source):
                cut_index = -1


                if "\n" in chunk_text:
                    cut_index = chunk_text.rfind("\n") + 1
                elif "." in chunk_text:
                    cut_index = chunk_text.rfind(".") + 1
                elif "," in chunk_text:
                    cut_index = chunk_text.rfind(",") + 1
                elif " " in chunk_text:
                    cut_index = chunk_text.rfind(" ") + 1

                if cut_index > 0:
                    end = start + cut_index

            text = source[start:end]


            yield ({
                "size": len(text),
                "file_path": file_path,
                "first_character_index": start,
                "last_character_index": end,
                "text": text
            })

            start = end





    
    