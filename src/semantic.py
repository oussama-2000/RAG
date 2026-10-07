from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from .models import MinimalSearchResults
from pathlib import Path



class Semantic_search:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.d = 384
        self.index = faiss.IndexFlatIP(self.d)
        self.data = []

    def load(self):
        self.index = faiss.read_index("data/processed/vectores.faiss")

        with open("data/processed/semantic_index.json", "r") as file:
            self.data = json.load(file)

    def store(self, data):
        chunks = [chunk['text'] for chunk in data.values()]

        d_vectors = np.array(self.model.encode(chunks, normalize_embeddings=True))
        self.index.add(d_vectors)
        faiss.write_index(self.index, "data/processed/vectores.faiss")

        with open("data/processed/semantic_index.json", "w") as file:
            json.dump(data, file, indent=4)

        print(f"indexed {self.index.ntotal}")

    def search(self, question, k, single=False, storing_file="data/search_results/single_question_result.json"):
        if single:
            query = question
        else:
            query = question.question

        self.load()

        result = []
        q_vectors = np.array(self.model.encode([query], normalize_embeddings=True))
        distances, indices = self.index.search(q_vectors, k)
        for i in indices[0]:

            result.append(self.data[tuple(self.data)[i]])

        if single:
            return (result)

        return MinimalSearchResults(
            question_id= question.question_id,
            question= question.question,
            retrieved_sources= result,
            storing_file= Path(storing_file).name
        )


