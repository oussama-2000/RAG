from rank_bm25 import BM25Okapi

documents = [
    "python functions and classes",
    "install vllm using uv",
    "bm25 retrieval algorithm vllm",
]

tokenized_documents = [
    document.lower().split()
    for document in documents
]

bm25 = BM25Okapi(tokenized_documents)

query = "install vllm"
tokenized_query = query.lower().split()

scores = bm25.get_scores(tokenized_query)

scores = bm25.get_top_n(tokenized_query, documents, n=1)
print(scores)