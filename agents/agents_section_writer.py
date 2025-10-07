# === agents_section_writer.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_SECTION_WRITING_INSTRUCTIONS = [
    "Before drafting, open each section with an italicized single-line \"Inputs Reviewed\" note that names the outline ID/title, linked compliance-matrix rows, technology insights, policy-pack directives (controls mapper, accessibility, SCRM/SBOM, red-team items), and any upstream editorial feedback you actually consulted. Mark each element as COMPLETE or MISSING inside the sentence so downstream agents can verify the hand-off without breaking the narrative flow.",
    "For each section in the provided outline, write a detailed, professional draft that integrates all relevant compliance requirements, personnel/security/IT standards, key dates, and technology recommendations while following the English Agent's structural guidance.",
    "Embed compliance obligations and policy-pack directives directly inside the narrative (e.g., \"aligns with NIST SP 800-53 AC-2\") rather than as detached bullet statements, and reference RFP sources in natural language (\"per the RFP on page 3\").",
    "Open each section with a full-paragraph narrative that centers the customer mission, then sustain the story with at least two additional paragraphs naming responsible teams, tools, cadence, and at least one quantified benefit or KPI woven into sentences.",
    "Include a brief proof point or micro-scenario demonstrating how we achieved a similar outcome for another jurisdiction or program.",
    "Default to paragraphs. Use no more than one short bullet list (≤3 bullets) or a table when it materially improves clarity; surround it with transitional sentences so the prose remains fluid.",
    "Close each section with a forward-looking statement that previews the next phase, highlights risk mitigation, or reiterates the evaluator's takeaway.",
    "Highlight the human impact in every section by naming the teams or residents who benefit and describing the change they will feel.",
    "Vary sentence length and use connective language (e.g., \"meanwhile\", \"as a result\", \"building on\") so the prose reads like a cohesive story instead of a checklist.",
    "Reference adjacent sections when natural (\"As detailed in Section SEC-OUT-04...\") to reinforce continuity and avoid isolated, robotic-sounding blocks.",
    "Never include bracketed requirement identifiers like [IT-1]; cite requirements and standards in plain language.",
    "After the narrative, append a markdown subheading titled 'Coverage Log' containing a table with columns Input | Evidence Used | Status. Log every compliance row, technology insight, policy-pack directive, and upstream comment you addressed. Use Status values of Complete, Partially Addressed (with follow-up notes), or Missing Input.",
    "If an expected input is missing or unclear, note it in the Coverage Log and add a short 'Open Questions' bullet list (≤3 bullets) beneath the table only when follow-up is required.",
    "Output each section as markdown with clear numbering and headers, followed by the Coverage Log (and Open Questions when needed).",
    "Return a dictionary where each key is a section name/number and each value is the full markdown draft (including Coverage Log) for that section.",
    "Be specific, avoid generic statements, and ensure all RFP requirements are addressed. Do not skip any sections from the outline.",
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
