# === agents_proposal_outline.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_PROPOSAL_OUTLINE_INSTRUCTIONS = [
    "Read the structured RFP analysis (JSON) from the RFP Analyzer Agent.",
    "Generate a recommended proposal outline that covers all required sections, subsections, and logical groupings to address the RFP.",
    "Output the outline as a hierarchical numbered list (e.g., 1., 1.1, 1.2, 2., etc.) in markdown.",
    "Flag any areas where the RFP is ambiguous or where additional sections may be needed for competitiveness.",
    "Be concise and do not include content, just section titles/headings.",
]


def build_proposal_outline_agent(model_id: str | None = None) -> Agent:
    """Builds the proposal outline agent."""
    return Agent(
        name="Proposal Outline Agent",
        role=(
            "Generates a detailed, hierarchical proposal outline based on the structured RFP analysis, "
            "ensuring all customer requirements and best practices are addressed in the proposal structure."
        ),
        model=OpenAIChat(id=model_id or llm_model),
        tools=[ReasoningTools(add_instructions=True)],
        instructions=_PROPOSAL_OUTLINE_INSTRUCTIONS,
        add_datetime_to_context=True,
    )
