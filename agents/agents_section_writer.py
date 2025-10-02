# === agents_section_writer.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_SECTION_WRITING_INSTRUCTIONS = [
    "For each section in the provided outline, write a detailed, professional draft that:",
    "- Integrates all relevant compliance requirements, personnel/security/IT standards, and key dates.",
    "- Incorporates technology research and best practices.",
    "- Uses the compliance matrix to ensure all requirements are addressed.",
    "- Follows the structure and recommendations from the English Agent.",
    "- Uses clear, persuasive, and action-oriented language.",
    "- References attachments, tables, and supporting documents as needed.",
    "Each section must contain at least three well-developed paragraphs or a rich blend of paragraphs and bullet lists covering solution approach, differentiators, and compliance evidence.",
    "Use substantive detail that reflects the customer's environment—include quantifiable results, past performance, team qualifications, tooling, and implementation specifics where known or inferable.",
    "Introduce bullet lists, tables, or subsection callouts when they make the content clearer or more compelling; do not leave requirements implied.",
    "Output each section as markdown, with clear section headers and numbering.",
    "Return a dictionary where each key is a section name/number and the value is the full markdown draft for that section.",
    "Be specific, avoid generic statements, and ensure all RFP requirements are addressed.",
    "Do not skip any sections from the outline.",
    "CRITICAL: Write FULL, COMPLETE content for every section. Do not use placeholders, summaries, or incomplete drafts. Each section must be submission-ready with detailed, substantive content that fully addresses the RFP requirements.",
]


def build_section_writing_agent(model_id: str | None = None) -> Agent:
    """Builds the section writing agent."""
    return Agent(
        name="Section Writing Agent",
        role=(
            "Drafts complete proposal sections based on the provided outline, compliance matrix, and technology research. "
            "Integrates all requirements, best practices, and recommendations into clear, persuasive, and compliant proposal text."
        ),
        model=OpenAIChat(id=model_id or llm_model),
        tools=[ReasoningTools(add_instructions=True)],
        instructions=_SECTION_WRITING_INSTRUCTIONS,
        add_datetime_to_context=True,
    )
