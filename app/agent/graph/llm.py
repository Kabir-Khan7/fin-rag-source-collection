"""
Local LLM binding for the agent graph.

Binds Qwen3 via Ollama with the settings that make a small model reliable
for tool-calling: thinking disabled, temperature 0. Config-driven so the
model swaps to qwen3:8b on better hardware without code changes.
"""

from langchain_ollama import ChatOllama

from app.core.config import settings


def get_llm() -> ChatOllama:
    """Return the configured local chat model for agent nodes."""
    return ChatOllama(
        model=settings.AGENT_MODEL,
        temperature=0,
        # Disable Qwen3 thinking via Ollama's think parameter.
        model_kwargs={"think": False},
    )