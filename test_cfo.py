"""Test the L2 CFO: cash, payables, vendor spend, and full overview."""

from langchain_core.messages import HumanMessage
from app.agent.graph.cfo_graph import build_cfo_graph


QUESTIONS = [
    "What's my current cash runway?",
    "How much do I owe in total payables?",
    "Where am I spending the most money?",
    "How's my business doing overall?",
]


def main() -> None:
    app = build_cfo_graph()

    for i, question in enumerate(QUESTIONS):
        config = {"configurable": {"thread_id": f"cfo-l2-{i}"}}
        print(f"\n{'='*60}\nOwner: {question}\n(working...)\n")

        result = app.invoke(
            {"messages": [HumanMessage(content=question)],
             "iteration": 0, "escalations": []},
            config=config,
        )
        print(f"AI CFO: {result['final_answer']}")


if __name__ == "__main__":
    main()