"""CLI entry point"""

from .chunkers.code import CodeChunker
from .chunkers.text import TextChunker
from .models import StudentSearchResults
from .reader import Reader
from .indexer import RagPipeline
from .recall_evaluation import Recall
import fire
import json
# from llm import LLM


class Pipeline:
    def __init__(self):
        self.indexer = RagPipeline()
        # self.llm = LLM()

    def index(self, max_chunk_size: int):
        self.indexer.ingest(max_chunk_size)

    def search(self, query: str, k: int):
        self.indexer.load()
        print(self.indexer.search(query, k, single=True))

    def search_dataset(self, dataset_path: str, k: int, save_directory: str):
        self.indexer.load()
        search_result = self.indexer.get_search_result(dataset_path, k)
        self.indexer.save_searching_output(search_result,k, save_directory)

    # def answer(self, query: str, k: int):
    #     print(self.llm.answer(query, ))

# max_chunk_size = 2000


# index = pipeline.ingest

# index.ingest("data/processed/indexed_chunks", max_chunk_size)

# # retrival
# index.load("data/processed/indexed_chunks")
# k = 1
# student_search: StudentSearchResults = index.get_search_result("data/datasets_public/public/UnansweredQuestions", k)

# index.save_searching_output(student_search, k)

# evaluation = Recall()

# evaluation.evaluate("data/search_results/dataset_docs_public.json", "data/datasets_public/public/AnsweredQuestions/dataset_docs_public.json")

from llm import LLM
llm = LLM()
resources = []
with open("data/search_results/dataset_docs_public.json", "r") as file:
    data = json.load(file)
    resources.append([source['text'] for source in data['search_results'][4]['retrieved_sources']])
question = "What are the differences between mm_kwargs and tok_kwargs when using the _call_hf_processor method in vLLM multimodal processing?"
print(llm.answer(question, resources))


fire.Fire(Pipeline)
# fire.Fire(index.load)

