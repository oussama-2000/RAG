

from rank_bm25 import BM25Okapi
import re
import pickle
import numpy
from .models import MinimalSource, MinimalSearchResults, StudentSearchResults, RagDataset
from pathlib import Path
import json
import os
from .reader import Reader
from .chunkers.code import CodeChunker
from .chunkers.text import TextChunker
from tqdm import tqdm

class RagPipeline:
    def __init__(self):
        self.reader = Reader("data/raw/vllm-0.10.1")
        self.code_chunker = CodeChunker()
        self.text_chunker = TextChunker()
        self.resurce_paths = []
        self.chunks = {} # [{"file_path": chunks}]
        self.tokenized_chunks = []
        self.bm25 = None
            
    def tokenize(self, text):
        return re.split(r'[-\s,./;<=>?!_(){}":]+', text.lower())


    def clean_tokenized_chunks(self, chunks):

        cleaned_chunks = []

        for chunk in chunks:
            cleaned_chunk = []

            for token in chunk:
                token = token.strip(".,;:!?(){}[]'\"-_")

                if len(token) < 3 or not token:
                    continue
                
                cleaned_chunk.append(token)
            cleaned_chunks.append(cleaned_chunk)
        return cleaned_chunks


    def chunk(self, max_chunk_size):

        self.resurce_paths = self.reader.read()
        chunks_exist = True # if the chunks file exists/empty or not

        # we should read the indexed files first to get the chunks and sources_path
        # then we check if the any file changed or not
        # if yes we update that file chunks with the new reading chunks
        # else we skip none changed files

        try:
            with open("data/processed/indexed_chunks", "rb") as file:
                data = pickle.load(file)

                self.chunks = {

                    f"{chunk.file_path}{chunk.first_character_index}" :
                        {
                            'file_path': chunk.file_path,
                            'first_character_index': chunk.first_character_index,
                            'last_character_index': chunk.last_character_index,
                            'text': chunk.text
                        }
                    for chunk in data['chunks']
                }
                self.resurce_paths = list(data['files'].keys())

        except FileNotFoundError, EOFError:
            chunks_exist = False

        for file in tqdm(self.resurce_paths, desc=f"chunking resources into chunks with size {max_chunk_size}"):
            if chunks_exist and os.path.getctime(file) == data['files'][file]:
                continue

            if file.suffix.lower() == ".py":
                chunks = self.code_chunker.extract_chunks(str(file), max_chunk_size)
                for chunk in chunks:
                    self.chunks.update({f"{file}{chunk['first_character_index']}" : chunk})
      
            elif file.suffix.lower() in [".txt", ".md"]:
                chunks = self.text_chunker.extract_chunks(str(file), max_chunk_size)
                for chunk in chunks:
                    self.chunks.update({f"{file}{chunk['first_character_index']}" : chunk})
 

    def build(self):

        chunks_content = [chunk['text'] for chunk in self.chunks.values()]

        tokenized_chunks = [
            self.tokenize(chunk)
            for chunk in chunks_content
        ]
        self.tokenized_chunks = self.clean_tokenized_chunks(tokenized_chunks) 
        self.bm25 = BM25Okapi(tokenized_chunks)


    def save(self, path):
        data  = {
            "files": {
                path: os.path.getctime(path) for path in self.resurce_paths
            },
            "chunks": [MinimalSource(**chunk) for chunk in self.chunks.values()],
            "tokenized_tokens": self.tokenized_chunks
        }

        with open(path, "wb") as file:
            pickle.dump(data, file)
    
    
    def ingest(self, max_chunk_size):
        self.chunk(max_chunk_size)
        self.build()
        self.save("data/processed/indexed_chunks")

    
    def load(self, path="data/processed/indexed_chunks"):
        print("loading data from disk ...")

        with open(path, "rb") as file:
            data = pickle.load(file)

        self.chunks = {
            f"{chunk.file_path}{chunk.first_character_index}" :
                {
                    'file_path': chunk.file_path,
                    'first_character_index': chunk.first_character_index,
                    'last_character_index': chunk.last_character_index,
                    'text': chunk.text
                }
            for chunk in data['chunks']
        }
        self.tokenized_chunks = data["tokenized_tokens"]
        self.bm25 = BM25Okapi(self.tokenized_chunks)


    def search(self, question, k, storing_file="data/search_results/single_question_result.json", single=False):
        if single:
            tokenized_query = self.tokenize(question)

        else:
            tokenized_query = self.tokenize(question.question)

        scores = self.bm25.get_scores(tokenized_query)
        
        result = []
        if single:
            for _ in tqdm(range(min(k, len(self.chunks))), desc=f"querying data '{question}'"):
                
                index = numpy.argmax(scores)

                result.append(list(self.chunks.values())[index])

                scores[index] = float("-infinity")
        else:
            for _ in range(min(k, len(self.chunks))):
                
                index = numpy.argmax(scores)

                result.append(list(self.chunks.values())[index])

                scores[index] = float("-infinity")

        if single:
            return result
        
        storing_file = Path(storing_file).name
        return MinimalSearchResults(
                question_id=question.question_id,
                question=question.question,
                retrieved_sources=result,
                storing_file=storing_file
            )
        

    def get_search_result(self, dataset_path, k):

        dataset_folder = Path(dataset_path)
        datasets = dataset_folder.rglob("*.json")

        student_results: list[MinimalSearchResults] = []
        for file in datasets:

            with open(str(file), "r") as f:
                questions = RagDataset(**json.load(f))
                for question in tqdm(questions.rag_questions, desc=f"querying data with questions from '{dataset_path}'"):
                    chunks = self.search(question, k, str(file))
                    student_results.append(chunks)

        return StudentSearchResults(search_results=student_results, k=k)


    def save_searching_output(self, result,k, save_directory="data/search_results"):

        os.makedirs(save_directory, exist_ok=True)

        content = {}

        for result in tqdm(result.search_results, desc=f"saving search results into {save_directory}"):
            sources = []

            for source in result.retrieved_sources:

                    sources.append({
                        "file_path": source.file_path,
                        "first_character_index": source.first_character_index,
                        "last_character_index": source.last_character_index,
                        "text": source.text
                    })
            try:
                content[result.storing_file]['search_results'].append({
                    "question_id": result.question_id,
                    "question": result.question,
                    "retrieved_sources": sources,
                })
            except KeyError:
                content.update({result.storing_file: {'search_results': [{
                    "question_id": result.question_id,
                    "question": result.question,
                    "retrieved_sources": sources
                    }]
                }})
            content[result.storing_file]["k"] = k

        for file in content.keys():
            with open(f"{save_directory}/{file}", "w") as f:
                json.dump(content[file], f, indent=4)
