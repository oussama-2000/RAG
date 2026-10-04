from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json


data = [
    {"/data/0": {"text": "color"}},
    {"/data/1": {"text": "USA"}},
    {"/data/2": {"text": "sky"}},
    {"/data/3": {"text": "nagasaki bomb"}},
]

class Semantic_search:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.d = 384
        self.index = faiss.IndexFlatL2(self.d)
        self.data = []


    def load(self):
        self.index = faiss.read_index("data/processed/vectores.faiss")

        with open("data/processed/semantic_index.json", "r") as file:
            self.data = json.load(file)

    def store(self, data):
        chunks = [list(chunk.values())[0]['text'] for chunk in data]


        d_vectors = np.array(self.model.encode(chunks))
        self.index.add(d_vectors)
        faiss.write_index(self.index, "data/processed/vectores.faiss")

        with open("data/processed/semantic_index.json", "w") as file:
            json.dump(data, file)

        print(f"indexed {self.index.ntotal}")

    def search(self, query, k):
        self.load()

        result = []
        q_vectors = np.array(self.model.encode([query]))
        distances, indices = self.index.search(q_vectors, k)
        for i in indices[0]:
            result.append(list(self.data[i].values())[0])

        return result ### should return pydantic type

q = "exploding"

search = Semantic_search()
# search.store(data)
search.search(q, 3)

