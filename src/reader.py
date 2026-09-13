from pathlib import Path
"""
pathlib: module provides and oop interface for working with file system paths.
Path: returns path into Path object with methods to do system calls.
"""

class Reader:
    def __init__(self, resources_path):
        self.base_dir = Path(resources_path)
        self.patterns = [".py", ".md", ".txt"]
        self.paths = []

    def read(self):

        files = self.base_dir.rglob("*")

        for file in files:
            if file.suffix.lower() in self.patterns:
                self.paths.append(file)
