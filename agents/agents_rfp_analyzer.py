# === agents_rfp_analyzer.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_RFP_ANALYZER_INSTRUCTIONS = [
    "Analyze the provided RFP text and extract the following:",
    "- Customer (primary agency/department)",
    "- Clear scope of work (1-2 sentences)",
    "- Major tasks (active work activities to be performed, with titles, descriptions, and page numbers)",
    '  Note: Only include actual work activities that require active effort, not compliance requirements',
    "- Key requirements (rules, standards, compliance requirements with page numbers)",
    "  Categories: Security, Compliance, IT Standards, Personnel",
    "- Key dates (submission, performance period)",
    "",
    "Guidelines:",
    '- Tasks must be active work activities (e.g., "Develop system", not "Must comply with")',
    '- Requirements should be rules/standards that must be followed',
    '- Group similar requirements under the same category',
    '- Normalize date descriptions (e.g., "after contract award" vs "after the date of award")',
    '- Avoid duplicate information with slight wording variations',
    '- Each requirement, task, and date should appear only once in the output',
    '- Consolidate similar requirements into single entries',
    "",
    "Return ONLY valid JSON matching the RFPAnalysis schema. No prose, no markdown, no code fences.",
]


def build_rfp_analyzer_agent(model_id: str | None = None) -> Agent:
    """Builds the RFP analyzer agent."""
    return Agent(
        name="RFP Analyzer Agent",
        role=(
            "Extracts structured information from RFP text, including customer, scope, tasks, requirements, and key dates. "
            "Outputs structured JSON for downstream processing."
        ),
        model=OpenAIChat(id=model_id or llm_model),
        tools=[ReasoningTools(add_instructions=True)],
        instructions=_RFP_ANALYZER_INSTRUCTIONS,
        add_datetime_to_context=True,
    )
