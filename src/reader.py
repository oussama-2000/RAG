from pathlib import Path

class Reader:
    def __init__(self, resources_path):
        self.base_dir = Path(resources_path)
        self.patterns = [".py", ".md", ".txt", ".test"]
        self.paths = []

    def read(self):

        files = self.base_dir.rglob("*")

        for file in files:
            if file.suffix.lower() in self.patterns:
                self.paths.append(file)
