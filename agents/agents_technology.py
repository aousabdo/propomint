# === agents_technology.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_TECHNOLOGY_AGENT_INSTRUCTIONS = [
    "Focus on technologies, frameworks, and standards directly relevant to the RFP.",
    "Summarize findings clearly and cite all sources.",
    "Highlight recent developments, pros/cons, and suitability for government/enterprise use.",
]


def build_technology_agent(model_id: str | None = None) -> Agent:
    """Builds the technology research agent."""
    return Agent(
        name="Technology Agent",
        role=(
            "Research and summarize technologies relevant to the RFP, including recent trends, standards, "
            "and best practices. Provide concise, actionable insights with sources."
        ),
        model=OpenAIChat(id=model_id or llm_model),
        tools=[DuckDuckGoTools()],
        instructions=_TECHNOLOGY_AGENT_INSTRUCTIONS,
        add_datetime_to_context=True,
    )
