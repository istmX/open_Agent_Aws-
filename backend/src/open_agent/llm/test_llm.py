"""Test the Groq LLM provider."""

import asyncio

from langchain_core.messages import HumanMessage, SystemMessage

from open_agent.llm.groq_provider import GroqProvider


async def main() -> None:
    """Test the Groq provider."""

    provider = GroqProvider()

    messages = [
        SystemMessage(
            content="You are a helpful AI assistant."
        ),
        HumanMessage(
            content="Explain what an AI agent is in one sentence."
        ),
    ]

    response = await provider.generate(messages)

    print("\n=== LLM RESPONSE ===")
    print(response.content)

    print("\n=== TOOL CALLS ===")
    print(response.tool_calls)


if __name__ == "__main__":
    asyncio.run(main())