# === agents_english.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_ENGLISH_AGENT_INSTRUCTIONS = [
    "Read the provided proposal section(s) and check for grammar, spelling, clarity, and narrative coherence.",
    "Restructure overly bullet-heavy passages into flowing paragraphs with transitions, unless a short list (≤3 bullets) improves readability.",
    "Emphasize active voice, varied sentence length, and a confident, conversational-professional tone.",
    "Call out opportunities to embed compliance references and metrics naturally inside sentences rather than as detached lists, and replace bracketed requirement tags with plain-language references (e.g., \"per the RFP on page 3\").",
    "Highlight any logical inconsistencies, missing transitions, or abrupt topic shifts that break the story.",
    "Output the revised text followed by a brief summary of the most important edits and remaining risks.",
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
