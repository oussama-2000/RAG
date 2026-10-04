

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
from .semantic import Semantic_search
from tqdm import tqdm
import uuid

class RagPipeline:
    def __init__(self):
        self.reader = Reader("data/raw/vllm-0.10.1")
        self.code_chunker = CodeChunker()
        self.text_chunker = TextChunker()
        self.resurce_paths = []
        self.chunks = {} # {"file_path": chunk}
        self.tokenized_chunks = []
        self.bm25 = None
        self.max_chunk_size = 0
        self.semantic_search = Semantic_search()
            
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


    def chunk(self):

        self.resurce_paths = self.reader.read()
        chunks_exist = True # if the chunks file exists/empty or not

        # we should read the indexed files first to get the chunks and sources_path
        # then we check if the any file changed or not
        # if yes we update that file chunks with the new reading chunks
        # else we skip none changed files

        try:
            with open("data/processed/indexed_chunks", "rb") as file:
                data = pickle.load(file)

                if data['max_chunk_size'] != self.max_chunk_size:
                    self.chunks = {}
                    raise EOFError
                    # when the chunk size changed we should reset our chunks stock variable 
                else:
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

        for file in tqdm(self.resurce_paths, desc=f"chunking resources into chunks with size {self.max_chunk_size}"):
            if chunks_exist:
                if os.path.getctime(file) == data['files'][file]:
                    continue

            if file.suffix.lower() == ".py":
                chunks = self.code_chunker.extract_chunks(str(file), self.max_chunk_size)
                for chunk in chunks:
                    self.chunks.update({f"{file}{chunk['first_character_index']}" : chunk})
      
            elif file.suffix.lower() in [".txt", ".md"]:
                chunks = self.text_chunker.extract_chunks(str(file), self.max_chunk_size)
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
            "tokenized_tokens": self.tokenized_chunks,
            "max_chunk_size": self.max_chunk_size
        }

        with open(path, "wb") as file:
            pickle.dump(data, file)
    
    
    def ingest(self, max_chunk_size, semantic=False):
        self.max_chunk_size = max_chunk_size
        self.chunk()
        if semantic:
            print("running semantic indexing...")
            self.semantic_search = Semantic_search()
            self.semantic_search.store(self.chunks)
        else:
            self.build()
            self.save("data/processed/lexical_index")

    
    def load(self, path="data/processed/lexical_index"):
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


    def check_cache_single_q(self, question, k):

        # check cache existing first
        cache_file = "data/query_cache.json"
        cache_existing = Path(cache_file).exists()

        if not cache_existing:
            with open(cache_file, "w"):
                return False
            
        question_cache_key = f"{question.lower().strip()}{k}"
        try:
            with open(cache_file, "r") as cache:
                data = json.load(cache)
                if question_cache_key in data.keys():
                    print("the question already exists in cache")
                    return data[question_cache_key]
                
        except json.decoder.JSONDecodeError:
            pass

        return False


    def search(self, question, k, storing_file="data/search_results/single_question_result.json", single=False):
        storing_file = Path(storing_file).name

        tokenized_query = self.tokenize(question if single else question.question)

        scores = self.bm25.get_scores(tokenized_query)
        
        result = []
        for _ in tqdm(range(min(k, len(self.chunks))), desc=f"querying data '{question}'") if single else range(min(k, len(self.chunks))):
            
            index = numpy.argmax(scores)

            result.append(list(self.chunks.values())[index])

            scores[index] = float("-infinity")

        # cache the question results
        cache_file = "data/query_cache.json"
        cache_existing = Path(cache_file).exists()

        if not cache_existing:
            with open(cache_file, "w"):
                pass
        question_cache_key = f"{question.lower().strip()}{k}" if single else f"{question.question.lower().strip()}{k}"
        
        with open(cache_file, "r+") as cache:
            try:
                # data = pickle.load(cache)
                data = json.load(cache)
            except EOFError, json.decoder.JSONDecodeError: # if the file is empty
                data = {}

            if single:
                data.update({
                    question_cache_key: 
                        {
                            "question_id": str(uuid.uuid4()),
                            "question": question,
                            "retrieved_sources": result,
                            "storing_file": storing_file
                        }
                    })
            else:
                data.update({
                    question_cache_key: {
                        "question_id": question.question_id,
                        "question": question.question,
                        "retrieved_sources": result,
                        "storing_file": storing_file
                    }
                })
            cache.seek(0) # reset the reading pointer
            cache.truncate() # clear the file
            # pickle.dump(data, cache)
            json.dump(data, cache, indent=4)
        ####
  
        if single:
            return result

        return MinimalSearchResults(
                question_id=question.question_id,
                question=question.question,
                retrieved_sources=result,
                storing_file=storing_file
            )
        

    def get_search_result(self, dataset_path, k, semantic=False):
        if semantic:
            print("running semantic searching...")
        cache_file = "data/query_cache.json"
        cache_data = {}
    
        try:
            with open(cache_file, "r") as cache:
                cache_data = json.load(cache)           
        except FileNotFoundError, json.decoder.JSONDecodeError:
            pass
    
        dataset_folder = Path(dataset_path)
        datasets = dataset_folder.rglob("*.json")

        student_results: list[MinimalSearchResults] = []
        
        for file in datasets:

            with open(str(file), "r") as f:
                questions = RagDataset(**json.load(f))

                for question in tqdm(questions.rag_questions, desc=f"querying data with questions from '{dataset_path}'"):
                    question_cache_key = f"{question.question.lower().strip()}{k}"

                    if question_cache_key in cache_data.keys():
                        student_results.append(cache_data[question_cache_key])
                    else:
                        if semantic:
                            chunks = self.semantic_search.search(question, k, False, str(file))
                        else:
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
