from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph_email.agent.prompts import SYSTEM_PROMPT


def build_agent(settings, tools):
    model = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        api_key=settings.google_api_key
    )

    return create_agent(
        model=model,
        tools=tools,
        checkpointer=InMemorySaver(),
        system_prompt=SYSTEM_PROMPT,
    )
