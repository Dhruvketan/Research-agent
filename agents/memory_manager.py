class MemoryManager:
    """A lightweight in-memory store for the research workflow."""

    def __init__(self) -> None:
        self.storage = []

    def update(self, topic: str, findings: list[dict], tasks: list[str]) -> None:
        self.storage.append({
            "topic": topic,
            "findings": findings,
            "tasks": tasks,
        })

    def snapshot(self) -> dict:
        return {
            "context_entries": len(self.storage),
            "latest_topic": self.storage[-1]["topic"] if self.storage else None,
        }
