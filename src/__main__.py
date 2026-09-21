"""CLI entry point"""

from chunkers.code import CodeChunker
from chunkers.text import TextChunker
from models import StudentSearchResults
from reader import Reader
from indexer import RagPipeline
from recall_evaluation import Recall
import time


max_chunk_size = 2000

index = RagPipeline()

index.ingest("data/processed/indexed_chunks", max_chunk_size)

# retrival
index.load("data/processed/indexed_chunks")
k = 5
student_search: StudentSearchResults = index.get_search_result("data/datasets_public/public/UnansweredQuestions", k)

index.save_searching_output(student_search, k)

evaluation = Recall()

evaluation.evaluate("data/search_results/dataset_code_public.json", "data/datasets_public/public/AnsweredQuestions/dataset_code_public.json")


