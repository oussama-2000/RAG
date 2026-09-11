from pathlib import Path

base_dir = Path("data/raw/vllm-0.10.1")

text_files = base_dir.rglob("*.py")

print(text_files)

for file in text_files:
    print(file)
