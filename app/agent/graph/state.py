import operator
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    escalations: Annotated[list[str], operator.add]
    facts: Annotated[list[dict], operator.add]   # NEW: structured figures