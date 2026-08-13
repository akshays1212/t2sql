"""LLM configuration module."""

from langchain_ollama import ChatOllama


def get_llm():
    """Initialize and return the LLM instance."""
    return ChatOllama(
        model="llama3.1:8b",
        temperature=0,
        num_ctx=8192,       # Chinook's full schema is ~1-2k tokens; 8k is plenty and safer than 20k on limited hardware
        num_predict=512,    # SQL queries are short — cap generation length
    )
