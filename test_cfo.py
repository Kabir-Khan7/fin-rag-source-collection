"""Test the L1 CFO hierarchy: CFO -> Finance HOD -> Cash-Flow Worker."""

from langchain_core.messages import HumanMessage
from app.agent.graph.cfo_graph import build_cfo_graph


def main() -> None:
    app = build_cfo_graph()
    config = {"configurable": {"thread_id": "cfo-test-1"}}

    question = "What's my current cash runway?"
    print(f"Owner: {question}\n(the finance team is working...)\n")

    result = app.invoke(
        {"messages": [HumanMessage(content=question)],
         "iteration": 0, "escalations": []},
        config=config,
    )

    print(f"AI CFO: {result['final_answer']}")


if __name__ == "__main__":
    main()