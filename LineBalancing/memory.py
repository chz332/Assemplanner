import json
from pathlib import Path

class MemoryManager:
    def __init__(self, filename=None):
        default_path = "./logs/memories.json"
        self.filename = filename or default_path

        Path(self.filename).parent.mkdir(parents=True, exist_ok=True)
        self.memories = self.load()

    def add(self, question, answer, reflection=None):
        self.memories.append({
            "question": question,
            "answer": answer,
            "reflection": reflection or ""
        })
        self.save()

    def format(self):
        result = []
        for m in self.memories:
            result.append((m["question"], m["answer"]))
        return result

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=4)

    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []