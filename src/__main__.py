"""CLI entry point"""

from .models import StudentSearchResults, StudentSearchResultsAndAnswer, MinimalAnswer
from .reader import Reader
from .indexer import RagPipeline
from .recall_evaluation import Recall
import fire
import json
from tqdm import tqdm
import os


class CLI:
    def __init__(self):
        self.indexer = RagPipeline()

    def index(self, max_chunk_size: int):
        self.indexer.ingest(max_chunk_size)
        print("indexing is done and saved into 'data/processed/indexed_chunks' .")


    def search(self, query: str, k: int):
        search_result = self.indexer.check_cache_single_q(query, k)
        if not search_result:
            self.indexer.load()
            search_result: str = self.indexer.search(query, k, single=True)
        
        print("search is done.")
        print(search_result)


    def search_dataset(self, dataset_path: str, k: int, save_directory: str):

        self.indexer.load()
        search_result: StudentSearchResults = self.indexer.get_search_result(dataset_path, k)
        self.indexer.save_searching_output(search_result, k, save_directory)


    def answer(self, query: str, k: int):
        self.indexer.load()
        search_results = self.indexer.search(query, k, single=True)
        sources = [source['text'] for source in search_results]

        from .llm import LLM
        llm = LLM()
        answer: MinimalAnswer = llm.answer(query, sources)
        print(answer)


    def answer_dataset(self, student_search_results_path: str, save_directory: str):
        from .llm import LLM
        llm = LLM()

        search_results_answer: StudentSearchResultsAndAnswer = {
            'search_results': [],
            'k': 0
        }
        answers :list[MinimalAnswer] = []

        with open(student_search_results_path, "r") as file:
            search_results = json.load(file)['search_results']

            k = 0

            for result in tqdm(search_results, desc=f"answering results from {student_search_results_path}"):
                question = result['question']
                sources = [source['text'] for source in result['retrieved_sources']]
                answers.append(llm.answer(question, sources))

                k += 1

        search_results_answer['search_results'] = answers
        search_results_answer['k'] = k

        os.makedirs(save_directory, exist_ok=True)

        with open("answer_results.json", "w") as file:
            json.dump(search_results_answer, file, indent=4)

        print(f"dataset answers saved int {save_directory}")


    def evaluate(self, student_search_results_path: str, dataset_path: str):
        evaluation = Recall()

        evaluation.evaluate(student_search_results_path, dataset_path, at=1)
        evaluation.evaluate(student_search_results_path, dataset_path, at=3)
        evaluation.evaluate(student_search_results_path, dataset_path, at=5)
        evaluation.evaluate(student_search_results_path, dataset_path, at=10)


if __name__ == "__main__":
    fire.Fire(CLI)



