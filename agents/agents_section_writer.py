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
    "Open each section with a narrative paragraph that sets the customer mission, this narrative should be at least a full paragraph long.",
    "Sustain the narrative with two or more paragraphs that describe the solution in story form—name the responsible teams, tools, cadence, and include at least one quantified benefit or KPI woven into sentences rather than bullets.",
    "Only introduce bullet lists or tables when they add clarity for dense requirements; keep them short (≤5 bullets) and surround them with transitional sentences so the prose feels continuous.",
    "Incorporate a proof point or micro-scenario that shows how we have delivered a similar outcome for another jurisdiction or program.",
    "Call out compliance obligations and cross-references inside the prose (e.g., \"aligns with NIST SP 800-53 AC-2\") instead of standalone bullet declarations.",
    "Close each section with a forward-looking statement that previews the next phase, highlights risk mitigation, or reiterates the outcome the evaluator should remember.",
    "Ensure the voice feels conversational-professional: vary sentence length, use active verbs, and avoid repetitive list structures.",
    "Default to paragraphs unless a list is absolutely necessary. When using bullets, limit to three items, keep them concise, and wrap them with sentences that explain the relevance.",
    "Use no more than one bullet list per section; when more detail is needed, translate it into sentences or tables instead of additional lists.",
    "Never include bracketed requirement identifiers like [IT-1]; reference requirements in plain language such as \"as called out on page 14 of the RFP\".",
    "Refer to RFP sources in natural language—cite the page or requirement inside the sentence (e.g., \"per the RFP on page 3\") instead of bracketed tags.",
    "If the outline references compliance items, weave them into sentences (e.g., \"aligned with NIST SP 800-53 AC-2\") rather than listing them verbatim.",
    "Highlight the human impact in every section: name the Springfield teams or residents who benefit and describe the change they will feel.",
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
