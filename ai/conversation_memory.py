"""Manage conversation history."""


class MemoryManager:
    def __init__(self):
        self.history = []

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_messages(self) -> list:
        return self.history
