# === agents_technology.py ===
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
import os

llm_model = os.getenv("LLM_MODEL", "gpt-5")

_TECHNOLOGY_AGENT_INSTRUCTIONS = [
    "Produce structured insights that downstream agents can slot into each outline section. Return ONLY valid JSON with a top-level key 'sections' containing an array of objects with: outline_section_id, outline_section_title, technology_theme, insight, implementation_guidance, risk_flags (array), and sources (array of {name, url}).",
    "Prioritize technologies, frameworks, and standards explicitly tied to the RFP tasks, compliance controls, or policy-pack directives. If a section has no relevant technology considerations, include the section with an insight of 'No additional technology research required' and explain why.",
    "For each insight, explain practical integration details (tool owners, cadence, data flows) and note any dependencies or risks called out in the RFP or policy packs.",
    "Cite authoritative, recent sources (≤3 years old when possible) and include accessible URLs. Do not return prose outside the JSON structure.",
]


def build_technology_agent(model_id: str | None = None) -> Agent:
    """Builds the technology research agent."""
    return Agent(
        name="Technology Agent",
        role=(
            "Research and summarize technologies relevant to the RFP, including recent trends, standards, "
            "and best practices. Provide concise, actionable insights with sources."
        ),
        model=OpenAIChat(id=model_id or llm_model),
        tools=[DuckDuckGoTools()],
        instructions=_TECHNOLOGY_AGENT_INSTRUCTIONS,
        add_datetime_to_context=True,
    )
