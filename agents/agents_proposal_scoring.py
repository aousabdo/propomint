# === agents_proposal_scoring.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_PROPOSAL_SCORING_INSTRUCTIONS = [
    "Evaluate the proposal section(s) for compliance, completeness, clarity, and competitiveness.",
    "Score each section and the overall proposal on a 0-100 scale, with rationale for each score.",
    "Highlight strengths, weaknesses, and areas for improvement.",
    "Output a summary table: Section | Score | Strengths | Weaknesses | Recommendations.",
    "Be objective, thorough, and actionable in your feedback.",
]


def build_proposal_scoring_agent(model_id: str | None = None) -> Agent:
    """Builds the proposal scoring agent."""
    return Agent(
        name="Proposal Scoring Agent",
        role=(
            "Scores the proposal against the RFP requirements and industry best practices. "
            "Provides a detailed breakdown of strengths, weaknesses, and actionable recommendations."
        ),
        model=OpenAIChat(id=model_id or llm_model),
        tools=[ReasoningTools(add_instructions=True)],
        instructions=_PROPOSAL_SCORING_INSTRUCTIONS,
        add_datetime_to_context=True,
    )
