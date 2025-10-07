# === agents_proposal_scoring.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_PROPOSAL_SCORING_INSTRUCTIONS = [
    "Ingest the active policy-pack weighting (if provided in context) and align your evaluation categories with those weights. When no pack metadata is provided, default to Compliance, Technical Solution, Management Approach, Staffing, Past Performance, and Risk Mitigation.",
    "Score each section and the overall proposal on a 0-100 scale, explicitly noting how the score maps to the policy-pack categories. Provide rationale that cites specific passages or coverage log entries.",
    "Highlight strengths, weaknesses, and areas for improvement, flagging any unmet compliance items or unresolved Coverage Log entries as critical actions.",
    "Output two tables: (1) Section | Category Weighting | Score | Strengths | Weaknesses | Recommendations, and (2) Overall Category | Weight | Score | Rationale | Required Fixes.",
    "Be objective, thorough, and actionable in your feedback. Where data is missing, state the assumption made and its impact on scoring.",
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
