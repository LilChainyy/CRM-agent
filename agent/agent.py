from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent

import config
from agent.prompts import SYSTEM_PROMPT
from tools.gmail_tool import search_gmail, create_gmail_tool
from tools.linkedin_tool import search_connections


def create_crm_agent(api_key: str = "", gmail_address: str = "", gmail_password: str = ""):
    """Create and return the CRM agent.

    Args:
        api_key: Anthropic API key. Falls back to config/env if empty.
        gmail_address: Gmail address. Falls back to config/env if empty.
        gmail_password: Gmail app password. Falls back to config/env if empty.
    """
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=api_key or config.ANTHROPIC_API_KEY,
    )

    if gmail_address and gmail_password:
        gmail_tool = create_gmail_tool(gmail_address, gmail_password)
    else:
        gmail_tool = search_gmail

    tools = [gmail_tool, search_connections]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent
