from pydantic import BaseModel, Field
from typing import List
import uuid

"""
uuid.uuid4(): function that generates random uuid (universally unique identifier)
its the standard choice for creating unique ids
"""

class MinimalSource(BaseModel):
    """Represent a source location in the indexed corpus."""
    file_path: str
    first_character_index: int
    last_character_index: int

class UnansweredQuestion(BaseModel):
    """Represent a question without its generated answer."""
    question_id: str = Field(default_factory=lambda:str(uuid.uuid4()))
    question: str

class AnsweredQuestion(UnansweredQuestion):
    """Represent a question with its answer and source locations."""
    sources: List[MinimalSource]
    answer: str

class RagDataset(BaseModel):
    """Represent a dataset of RAG questions."""
    rag_questions: List[AnsweredQuestion | UnansweredQuestion]

class MinimalSearchResults(BaseModel):
    """Represent retrieved sources for one question."""
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]

class MinimalAnswer(MinimalSearchResults):
    """Represent retrieved sources together with a generated answer."""
    answer: str

class StudentSearchResults(BaseModel):
    """Represent search results for a dataset."""
    search_results: List[MinimalSearchResults]
    k: int

class StudentSearchResultsAndAnswer(BaseModel):
    """Represent search results together with generated answers."""
    search_results: List[MinimalAnswer]
    k: int