import asyncio
from uuid import uuid4
from langchain.mcp import MCPAdapter
from langgraph_email.agent.factory import build_agent
from langgraph_email.core.config import Settings
from langgraph_email.mcp.client import create_mcp_client


async def main():
    settings = Settings()
    mcp_client = create_mcp_client(settings)

    async with MCPAdapter(mcp_client) as adapter:
        tools = await adapter.list_tools()
        agent = build_agent(settings, tools)

        config = {
            "configurable": {
                "thread_id": str(uuid4())
            }
        }

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue

            result = await agent.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input,
                        }
                    ]
                },
                config=config,
            )

            print("Assistant:", result["messages"][-1].text)


if __name__ == "__main__":
    asyncio.run(main())
