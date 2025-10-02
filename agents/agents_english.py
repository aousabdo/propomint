# === agents_english.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_ENGLISH_AGENT_INSTRUCTIONS = [
    "Read the provided proposal section(s) and check for grammar, spelling, and clarity.",
    "Suggest edits to improve tone, flow, and persuasiveness, making sure the writing sounds like it is from the same author throughout.",
    "Point out any logical inconsistencies or unclear statements.",
    "Output both the revised text and a brief summary of changes.",
    "Be concise and direct in your feedback.",
]


def build_english_agent(model_id: str | None = None) -> Agent:
    """Builds the English language review agent."""
    return Agent(
        name="English Agent",
        role=(
            "Reviews proposal sections for clarity, correctness, grammar, tone, and logical flow. "
            "Provides feedback and suggested edits to ensure professional, consistent, and persuasive writing."
        ),
        model=OpenAIChat(id=model_id or llm_model),
        tools=[ReasoningTools(add_instructions=True)],
        instructions=_ENGLISH_AGENT_INSTRUCTIONS,
        add_datetime_to_context=True,
    )
