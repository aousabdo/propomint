# === agents_outlining_compliance.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_OUTLINING_COMPLIANCE_INSTRUCTIONS = [
    "Generate a hierarchical outline of the RFP sections and subsections.",
    "Extract all compliance requirements and map them to their corresponding sections/pages, explicitly referencing the outline section number/title for each mapping.",
    "Create compliance matrix entries with: requirement, section, page, status (Y/N/Partial), owner, artifact, trigger, verification. Use the section field to store the exact outline section identifier so downstream agents can filter by section.",
    "Highlight any ambiguous or missing compliance items.",
    "Return ONLY valid JSON matching the ComplianceRow schema for each compliance item. No prose, no markdown, no code fences.",
]


def build_outlining_compliance_agent(model_id: str | None = None) -> Agent:
    """Builds the outlining and compliance matrix agent."""
    return Agent(
        name="Outlining & Compliance Matrix Agent",
        role=(
            "Extracts a detailed outline and compliance matrix from RFPs, mapping requirements "
            "to sections and ensuring all compliance items are captured. Outputs structured compliance matrix."
        ),
        model=OpenAIChat(id=model_id or llm_model),
        tools=[ReasoningTools(add_instructions=True)],
        instructions=_OUTLINING_COMPLIANCE_INSTRUCTIONS,
        add_datetime_to_context=True,
    )
