"""CLI entry point"""

from .chunkers.code import CodeChunker
from .chunkers.text import TextChunker
from .models import StudentSearchResults
from .reader import Reader
from .indexer import RagPipeline
from .recall_evaluation import Recall
import fire
import json
import os


class CLI:
    def __init__(self):
        self.indexer = RagPipeline()

    def index(self, max_chunk_size: int):
        print(f"indexing sources into chunks with size {max_chunk_size} ...")
        self.indexer.ingest(max_chunk_size)
        print("indexing is done and saved into 'data/processed/indexed_chunks' .")

    def search(self, query: str, k: int):
        print("loading data from disk ...")
        self.indexer.load()
        print(f"querying data '{query}' ...")
        search_result = self.indexer.search(query, k, single=True)
        print("search is done.")
        print(search_result)

    def search_dataset(self, dataset_path: str, k: int, save_directory: str):
        print("loading data from disk...")
        self.indexer.load()
        print(f"querying data with questions from '{dataset_path}'")

        search_result = self.indexer.get_search_result(dataset_path, k)

        self.indexer.save_searching_output(search_result,k, save_directory)
        print(f"search done and it's result saved into '{save_directory}'")

    def answer(self, query: str, k: int):
        self.indexer.load()
        search_results = self.indexer.search(query, k, single=True)

        sources = [source for source in search_results]

        from .llm import LLM
        llm = LLM()
        answer = llm.answer(query, sources)
        os.system("clear")
        print(answer)

    def answer_dataset(self, student_search_results_path: str, save_directory: str):
        from .llm import LLM
        llm = LLM()

        answers = []

        with open(student_search_results_path, "r") as file:
            search_results = json.load(file)['search_results']

            for result in search_results:
                question = result['question']
                sources = [source['text'] for source in result['retrieved_sources']]

                # answers.append(llm.answer(question, sources))
                print(llm.answer(question, sources), flush="True")
        # print(answers)

    def evaluate(self, student_search_results_path: str, dataset_path: str):
        evaluation = Recall()

        evaluation.evaluate(student_search_results_path, dataset_path)


if __name__ == "__main__":
    fire.Fire(CLI)



