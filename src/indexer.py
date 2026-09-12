

from rank_bm25 import BM25Okapi
import re
import pickle
import numpy
from models import MinimalSource, MinimalSearchResults, StudentSearchResults, RagDataset
from pathlib import Path
import json


class BM25Indexer:
    def __init__(self):
        self.chunks = []
        self.tokenized_chunks = []
        self.bm25 = None
            
    def tokenize(self, text):
        return re.split(r'[ ,(){}:\n]', text.lower())
    
    def build(self, chunks):
        self.chunks = chunks
        texts = [chunk['text'] for chunk in chunks]

        tokenized_chunks = [
            self.tokenize(chunk)
            for chunk in texts
        ]

        self.tokenized_chunks = tokenized_chunks
        self.bm25 = BM25Okapi(tokenized_chunks)

    def save(self, path):
        data  = {
            "chunks": [MinimalSource(**chunk) for chunk in self.chunks],
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

    def search(self, question, k):
        tokenized_query = self.tokenize(question.question)

        scores = self.bm25.get_scores(tokenized_query)
        
        result = []
        seen_indexs = []
        for _ in range(k):
            
            index = numpy.argmax(scores)

            if index not in seen_indexs:
                result.append(self.chunks[index])
                seen_indexs.append(index)

            scores[index] = float("-infinity")

        return MinimalSearchResults(
                question_id=question.question_id,
                question=question.question,
                retrieved_sources=result
            )
        

    def get_search_result(self, datasets_path, k):

        dataset_folder = Path(datasets_path)
        datasets = dataset_folder.rglob("*.json")

        student_results: StudentSearchResults[MinimalSearchResults] = []
        for file in datasets:

            with open(str(file), "r") as file:
                questions = RagDataset(**json.load(file))
                for question in questions.rag_questions:
                    chunks = self.search(question, 1)
                    student_results.append(chunks)

        return StudentSearchResults(search_results=student_results, k=1)
