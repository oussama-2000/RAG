

from rank_bm25 import BM25Okapi
import re
import pickle
import numpy


class BM25Indexer:
    def __init__(self):
        self.chunks = []
        self.tokenized_chunks = []
        self.bm25 = None

    def muliple_remove(self, element, list):
        while element in list:
            list.remove(element)
    def tokenize(self, text):
        return re.split(r'[ ,(){}:\n]', text.lower())
    
    def build(self, chunks):
        self.chunks = chunks
        texts = [chunk['text'] for chunk in chunks]

        tokenized_chunks = [
            self.tokenize(chunk)
            for chunk in texts
        ]

        for chunk in tokenized_chunks:
            for token in chunk:
                if len(token) < 2 or token.isspace() or not token:
                    self.muliple_remove(token, chunk)

        self.tokenized_chunks = tokenized_chunks
        self.bm25 = BM25Okapi(tokenized_chunks)

    def save(self, path):
        data  = {
            "chunks": self.chunks,
            "tokenized_tokens": self.tokenized_chunks
        }

        with open(path, "wb") as file:
            pickle.dump(data, file)

    def ingest(self, chunks, save_file_path):
        self.build(chunks)
        self.save(save_file_path)
    
    def load(self, path):

        with open(path, "rb") as file:
            data = pickle.load(file)

        self.chunks = data["chunks"]
        self.tokenized_chunks = data["tokenized_tokens"]
        self.bm25 = BM25Okapi(self.tokenized_chunks)

    def search(self, query, k):
        tokenized_query = self.tokenize(query)

        scores = self.bm25.get_scores(tokenized_query)
        
        result = []
        for _ in range(k):
            index = numpy.argmax(scores)
            scores = numpy.delete(scores, index)
            result.append(self.chunks[index])

        return result
















# documents = [
#     "python functions and classes",
#     "install vllm using uv",
#     "bm25 retrieval algorithm vllm",
# ]

# tokenized_documents = [
#     document.lower().split()
#     for document in documents
# ]

# bm25 = BM25Okapi(tokenized_documents)

# query = "install vllm"
# tokenized_query = query.lower().split()

# scores = bm25.get_scores(tokenized_query)

# scores = bm25.get_top_n(tokenized_query, documents, n=1)
# print(scores)