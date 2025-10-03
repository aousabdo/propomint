# === agents_tone.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_TONE_AGENT_INSTRUCTIONS = [
    "Review the provided proposal sections for tone, style, and voice consistency, favoring a confident, solutions-focused narrative.",
    "Smooth out abrupt lists by adding transitional sentences, varying sentence length, and ensuring paragraphs flow logically.",
    "Flag any language that sounds mechanical, repetitive, or compliance-only; replace bracketed requirement tags with conversational references and recommend more human, benefit-oriented phrasing.",
    "Ensure terminology, acronyms, and references remain consistent while keeping the voice warm, accountable, and forward-looking.",
    "Output the harmonized text along with a summary of tone/style changes and any remaining rough spots to polish.",
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
