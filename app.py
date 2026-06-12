import argparse

from agents.intent_agent import understand_intent
from agents.planner import plan_topic
from agents.search_agent import search_papers
from agents.reader_agent import read_papers
from agents.critic_agent import validate_findings
from agents.writer_agent import write_report
from agents.memory_manager import MemoryManager


def generate_report(topic: str) -> str:
    intent = understand_intent(topic)
    tasks = plan_topic(topic) + [
        f"Use structured intent: {intent['query_type']} across {', '.join(intent['domains'])}",
        "Validate retrieved papers for domain and technical relevance",
    ]
    papers = search_papers(topic)
    notes = read_papers(papers)
    critique = validate_findings(notes)
    memory = MemoryManager()
    memory.update(topic=topic, findings=notes, tasks=tasks)
    return write_report(topic, tasks, papers, notes, critique, memory.snapshot())


def main() -> None:
    parser = argparse.ArgumentParser(description="Research Agent CLI")
    parser.add_argument("topic", nargs="?", default="Applications of Gaussian Boson Sampling in Biological Systems")
    args = parser.parse_args()

    report = generate_report(args.topic)
    print(report)


if __name__ == "__main__":
    main()
