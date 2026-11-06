from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph_email.agent.prompts import SYSTEM_PROMPT


def build_agent(settings, tools):
    model = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        api_key=settings.google_api_key
    )

    return create_agent(
        model=model,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "send_email": {
                        "allowed_decisions": ["approve", "reject"],
                    },
                    "delete_draft": {
                        "allowed_decisions": ["approve", "reject"],
                    },
                    "trash_email": {
                        "allowed_decisions": ["approve", "reject"],
                    },
                    "trash_thread": {
                        "allowed_decisions": ["approve", "reject"],
                    },
                    "permanently_delete_thread": {
                        "allowed_decisions": ["approve", "reject"],
                    },
                },
                description_prefix="User approval required",
                ),
        ],
        tools=tools,
        checkpointer=InMemorySaver(),
        system_prompt=SYSTEM_PROMPT,
    )
