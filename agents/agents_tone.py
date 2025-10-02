# === agents_tone.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_TONE_AGENT_INSTRUCTIONS = [
    "Review the provided proposal sections for tone, style, and voice consistency.",
    "Suggest edits to align all sections to a unified, professional, and persuasive tone.",
    "Point out any sections that sound out of place or inconsistent.",
    "Output both the harmonized text and a summary of tone/style changes.",
    "Be specific and concise in your suggestions.",
]


def build_tone_agent(model_id: str | None = None) -> Agent:
    """Builds the tone harmonization agent."""
    return Agent(
        name="Tone Agent",
        role=(
            "Ensures the proposal maintains a consistent, professional, and persuasive tone and style "
            "throughout all sections. Harmonizes voice, formality, and word choice."
        ),
        model=OpenAIChat(id=model_id or llm_model),
        tools=[ReasoningTools(add_instructions=True)],
        instructions=_TONE_AGENT_INSTRUCTIONS,
        add_datetime_to_context=True,
    )
