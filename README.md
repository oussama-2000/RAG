
1 - Indexing

    we need to ingest the provided vllm repository and split files into chunks.

2 - Retrieval

    retieval returns:
        file_path
        first_character_index
        last_character_index

3 - answer generation

    the retrieved chunks are passed to 'Qwen/Qwen3-0.6B' to generate readable answer


the project must work like this :

    uv run python -m src index --max_chunk_size 2000

    uv run python -m src search "How does X work?" --k 5

    uv run python -m src search_dataset \
        --dataset_path ... \
        --k 10 \
        --save_directory ...

    uv run python -m src answer "How does X work?" --k 5

    uv run python -m src answer_dataset \
        --student_search_results_path ... \
        --save_directory ...

    uv run python -m src evaluate \
        --student_search_results_path ... \
        --dataset_path ...

our strategy:

    Build index
        ↓
    Implement retrieval
        ↓
    Measure Recall@5 (evaluation)
        ↓
    Improve chunking/tokenization/ranking
        ↓
    Only then focus heavily on LLM generation


STEP 1  → Understand the evaluation/data
STEP 2  → Create uv project
STEP 3  → Create Pydantic models
STEP 4  → Implement Python chunker
STEP 5  → Implement Markdown chunker
STEP 6  → Build persistent BM25 index
STEP 7  → Implement search
STEP 8  → Implement dataset search
STEP 9  → Implement Recall@k evaluation
STEP 10 → Optimize retrieval until targets are reached
STEP 11 → Integrate Qwen3-0.6B
STEP 12 → Implement answer generation
STEP 13 → Add Makefile/tests/mypy/flake8
STEP 14 → README + defense preparation
STEP 15 → Bonus, if everything passes
