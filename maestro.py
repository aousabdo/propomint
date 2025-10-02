from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.reasoning import ReasoningTools
# from agno.tools.yfinance import YFinanceTools

import argparse
import dotenv, os
from datetime import datetime
import re
import json
import textwrap
from pathlib import Path
from rich.console import Console
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional

from agents.orchestration_integration import assemble_team_with_us_upgrades
from policy_packs import POLICY_PACKS, select_policy_pack
from agents.agents_domain_profiler import domain_profiler
from agents.agents_compliance_red_team import build_compliance_red_team
from agents.agents_controls_mapper import build_controls_mapper
from agents.agents_scrm_sbom import build_scrm_sbom_agent
from agents.agents_accessibility import build_accessibility_agent
from agents.agents_outlining_compliance import build_outlining_compliance_agent
from agents.agents_english import build_english_agent
from agents.agents_tone import build_tone_agent
from agents.agents_proposal_scoring import build_proposal_scoring_agent
from agents.agents_rfp_analyzer import build_rfp_analyzer_agent
from agents.agents_technology import build_technology_agent
from agents.agents_section_writer import build_section_writing_agent
from agents.agents_proposal_outline import build_proposal_outline_agent

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path, override=True)

llm_model = "gpt-4.1"
llm_model = "gpt-5"
# llm_model = "gpt-5-mini"
# llm_model = "gpt-5-nano"
    
# import os, re

# key = os.getenv("OPENAI_API_KEY", "")
# print("Using OPENAI_API_KEY:", re.sub(r"(sk-[^_]+_)[A-Za-z0-9_-]{20,}(.*)", r"\1***REDACTED***\2", key))


# agent = Agent(
#     model=OpenAIChat(id="gpt-5"),
#     markdown=True
# )

# # Print the response in the terminal
# agent.print_response("Share a 2 sentence horror story.")

# raise SystemExit("stop code here")

# Pydantic Models for Structured Outputs
class TaskItem(BaseModel):
    title: str
    description: str
    page: int

class Requirement(BaseModel):
    category: str  # Security | Compliance | IT Standards | Personnel
    description: str
    page: int

class DateItem(BaseModel):
    event: str
    date: str
    page: int

class RFPAnalysis(BaseModel):
    customer: str
    scope: dict  # {"text": str, "page": int}
    tasks: List[TaskItem]
    requirements: List[Requirement]
    dates: List[DateItem]

class ComplianceRow(BaseModel):
    requirement: str
    section: str
    page: str
    status: str  # "Y" | "N" | "Partial"
    owner: Optional[str] = None
    artifact: Optional[str] = None
    trigger: Optional[str] = None
    verification: Optional[str] = None

class ProposalSection(BaseModel):
    section_number: str
    title: str
    content: str
    word_count: Optional[int] = None

class ProposalOutline(BaseModel):
    sections: List[ProposalSection]

# JSON-only helper with schema validation and retry logic
def ask_json(agent, user_prompt: str, schema_model: type[BaseModel], max_retries: int = 2):
    """Ask an agent for structured JSON output with schema validation and auto-retry."""
    schema_hint = schema_model.model_json_schema()
    system_guard = (
        "Return ONLY valid JSON matching the provided schema. "
        "No prose, no markdown, no code fences. Do not include comments."
    )
    prompt = f"""
{system_guard}
SCHEMA (JSON Schema):
{json.dumps(schema_hint, ensure_ascii=False, indent=2)}

USER REQUEST:
{user_prompt}
"""
    for attempt in range(max_retries + 1):
        try:
            raw = agent.run(prompt).content if hasattr(agent, "run") else agent.print_response(prompt)
            # Clean the response - remove any markdown code fences or extra text
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            
            data = json.loads(raw)
            return schema_model.model_validate(data)
        except Exception as e:
            err = str(e)
            if attempt < max_retries:
                prompt = f"""
{system_guard}
Your previous output did not parse with error: {err}
Re-emit ONLY valid JSON that strictly matches the schema.

SCHEMA:
{json.dumps(schema_hint, ensure_ascii=False, indent=2)}

USER REQUEST:
{user_prompt}
"""
            else:
                raise ValueError(f"Failed to obtain valid JSON after {max_retries + 1} attempts. Last error: {err}")

# Helper function to save structured outputs
def save_structured_output(data: BaseModel, filename: str, dir_name: str = "rfp_analysis"):
    """Save structured output to JSON file with timestamp in specified directory."""
    import os
    from datetime import datetime
    os.makedirs(dir_name, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = os.path.join(dir_name, f"{filename}_{timestamp}.json")
    with open(full_filename, "w", encoding="utf-8") as f:
        json.dump(data.model_dump(), f, indent=2, ensure_ascii=False)
    print(f"💾 Saved structured output to {full_filename}")
    return full_filename

# We need the following agents:

# 1. RFP Analyzer Agent: We already have this agent built, we will need to tweak it to fit our needs.
# 2. Outlining and Compliance matrix agent: this is somewhat already done as part of our RFP Analyzer agent above. But we need to revisit
# 3. Technology Agent: Research technologies that are relevent to the RFP. This agne should browse the internet and perform research on the technologies related to the given RFP.
# 4. English Agent: This agent takes a first glance at the proposal sections written by other agents and makes sure it is correct etc. 
# 5. Tone agent: make sure the final proposal souunds like it is from the same person
# 6. Proposal Scoring Agent: This agent scores the proposal based on the RFP and also based on what Patrick has already done in his custom gpt
# 7. Maestor Agent: This is the orchestrating agent that will be responsible for coordinating the other agents and making sure the final proposal is correct and complete.


# Core agent builders
rfp_analyzer_agent = build_rfp_analyzer_agent(llm_model)
proposal_outline_agent = build_proposal_outline_agent(llm_model)
outlining_compliance_agent = build_outlining_compliance_agent(llm_model)
technology_agent = build_technology_agent(llm_model)
section_writing_agent = build_section_writing_agent(llm_model)
english_agent = build_english_agent(llm_model)
tone_agent = build_tone_agent(llm_model)
proposal_scoring_agent = build_proposal_scoring_agent(llm_model)

# Maestor Agent: Orchestrates all specialized agents to produce a complete, high-quality proposal
maestor_team = Team(
    name="Maestor Orchestration Team",
    model=OpenAIChat(id=llm_model),
    members=[
        rfp_analyzer_agent,  # 1. Analyze RFP and extract structured info
        proposal_outline_agent,  # 2. Generate detailed proposal outline from RFP analysis
        outlining_compliance_agent,  # 3. Extract compliance matrix and map requirements
        technology_agent,  # 4. Research relevant technologies
        section_writing_agent,  # 5. Draft proposal sections using outline, compliance, and research
        english_agent,  # 6. Review language/clarity
        tone_agent,  # 7. Harmonize tone/style
        proposal_scoring_agent,  # 8. Score proposal
    ],
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        "Coordinate all member agents to analyze the RFP, generate a detailed proposal outline, extract structure and compliance, research technologies, draft full proposal sections, review language, harmonize tone, and score the proposal.",
        "Ensure the Proposal Outline Agent uses the output of the RFP Analyzer Agent to generate a comprehensive outline before compliance, technology, and section writing steps.",
        "Each step should be completed in logical order and outputs passed between agents as needed.",
        "If any agent flags missing or ambiguous information, highlight it in the final output.",
        "Produce a SINGLE, consolidated proposal package with all required sections, compliance matrix, technology research, language review, tone harmonization, and scoring summary.",
        "DO NOT duplicate content - each section should appear only once in the final output.",
        "Output all tables as markdown tables for easy rendering.",
        "Be explicit and clear in the final summary and recommendations.",
        "Ensure the final output is clean, well-structured, and free of redundant information.",
        "CRITICAL: Do not finish until EVERY section in the proposal outline has been fully written out with complete content. No placeholders, summaries, or incomplete sections are acceptable. The Section Writing Agent must produce full drafts of every section before proceeding to review and harmonization steps.",
    ],
    markdown=True,
    show_members_responses=False,
    enable_agentic_state=True,
    add_datetime_to_context=True,
    # success_criteria="The team has produced a COMPLETE proposal with ALL required sections written, reviewed, and harmonized. The proposal must include: 1) Full RFP analysis with structured JSON output, 2) Complete proposal outline with all sections numbered, 3) Detailed compliance matrix mapping all requirements, 4) Technology research summary, 5) FULL DRAFT of every section in the outline (not just summaries), 6) Language review and corrections applied, 7) Tone harmonization across all sections, 8) Final scoring and recommendations. NO section may be left as placeholder, summary, or incomplete. The proposal must be submission-ready with all content written out in full.",
)


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_RFP_FILENAME = "sample_rfp_dev.txt"
DEFAULT_RFP_PATH = BASE_DIR / DEFAULT_RFP_FILENAME


def load_rfp_text(rfp_path: Optional[str] = None) -> tuple[str, Path]:
    """Return RFP text and resolved path, defaulting to the lightweight dev sample."""
    path = Path(rfp_path) if rfp_path else DEFAULT_RFP_PATH
    if not path.is_absolute():
        path = BASE_DIR / path
    if not path.exists():
        raise FileNotFoundError(f"RFP file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return handle.read(), path


def _dedupe_consecutive_lines(text: str) -> str:
    """Remove consecutive duplicate lines while preserving order.
    Keeps the first occurrence when the same normalized line repeats back-to-back.
    """
    lines = text.splitlines()
    cleaned = []
    prev_norm = None
    for line in lines:
        norm = line.strip().lower()
        if norm == prev_norm:
            # skip exact consecutive duplicate
            continue
        cleaned.append(line)
        prev_norm = norm
    return "\n".join(cleaned)


def _msg_to_text(msg) -> str:
    try:
        d = msg.to_dict() if hasattr(msg, "to_dict") else None
    except Exception:
        d = None
    role = None
    name = None
    content = None
    if isinstance(d, dict):
        role = d.get("role")
        name = d.get("name")
        content = d.get("content")
    else:
        role = getattr(msg, "role", None)
        name = getattr(msg, "name", None)
        content = getattr(msg, "content", None)
    # Normalize content to string
    if content is None:
        content_str = ""
    elif isinstance(content, (list, dict)):
        import json
        try:
            content_str = json.dumps(content, ensure_ascii=False, indent=2)
        except Exception:
            content_str = str(content)
    else:
        content_str = str(content)
    header = f"[{role or 'unknown'}{(' - ' + name) if name else ''}]"
    return f"{header}\n{content_str}".strip()


def _format_transcript(messages) -> str:
    parts = ["Agent Conversation Transcript", ""]
    for m in messages:
        parts.append(_msg_to_text(m))
        parts.append("\n---\n")
    return "\n".join(parts).rstrip()


# def main():
#     from datetime import datetime
#     dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
#     session_id = f"maestor_{dt_str}"

#     print("Running team to generate proposal...")
#     response = maestor_team.run(sample_rfp, session_id=session_id, retries=2)

#     # Prefer the content field rather than repr to avoid duplicated metadata
#     raw_text = getattr(response, "content", str(response)) or ""

#     # Light cleanup: drop consecutive duplicate lines (common at the start)
#     cleaned_text = _dedupe_consecutive_lines(raw_text)

#     # Save main consolidated output
#     out_filename = f"proposal_clean_{dt_str}.txt"
#     with open(out_filename, "w", encoding="utf-8") as f:
#         f.write(cleaned_text)

#     # Save full conversation transcript separately
#     try:
#         # Prefer full session history if available
#         messages = maestor_team.get_messages_for_session(session_id=session_id) or response.messages or []
#     except Exception:
#         messages = response.messages or []
#     transcript_text = _format_transcript(messages) if messages else "(No conversation messages captured)"
#     transcript_filename = f"proposal_conversation_{dt_str}.md"
#     with open(transcript_filename, "w", encoding="utf-8") as tf:
#         tf.write(transcript_text)

#     print(f"Saved clean output to {out_filename}\nSaved conversation transcript to {transcript_filename}")

def main(argv=None):
    parser = argparse.ArgumentParser(description="Run Maestor proposal workflow against an RFP text file.")
    parser.add_argument(
        "--rfp-file",
        dest="rfp_file",
        help="Path to an RFP .txt file. Defaults to sample_rfp_dev.txt.",
    )
    args = parser.parse_args(argv)

    try:
        rfp_text, rfp_path = load_rfp_text(args.rfp_file)
    except FileNotFoundError as err:
        print(f"❌ {err}")
        return

    print(f"Using RFP file: {rfp_path}")
    console = Console(record=True)
    
    # First, get structured RFP analysis
    print("Analyzing RFP with structured output...")
    try:
        rfp_analysis = ask_json(rfp_analyzer_agent, rfp_text, RFPAnalysis)
        print(f"✅ RFP Analysis completed: {len(rfp_analysis.tasks)} tasks, {len(rfp_analysis.requirements)} requirements, {len(rfp_analysis.dates)} dates")
        
        # Save structured output
        save_structured_output(rfp_analysis, "rfp_analysis")
        
        # Convert structured analysis back to text for the team
        analysis_text = f"""
RFP Analysis Results:
Customer: {rfp_analysis.customer}
Scope: {rfp_analysis.scope['text']} (Page {rfp_analysis.scope['page']})

Tasks:
{chr(10).join([f"- {task.title}: {task.description} (Page {task.page})" for task in rfp_analysis.tasks])}

Requirements:
{chr(10).join([f"- {req.category}: {req.description} (Page {req.page})" for req in rfp_analysis.requirements])}

Key Dates:
{chr(10).join([f"- {date.event}: {date.date} (Page {date.page})" for date in rfp_analysis.dates])}

Original RFP Text:
{rfp_text}
"""
        
        # Assemble upgraded orchestrated team and run
        base_members = [
            rfp_analyzer_agent,
            proposal_outline_agent,
            outlining_compliance_agent,
            technology_agent,
            section_writing_agent,
            english_agent,
            tone_agent,
            proposal_scoring_agent,
        ]
        upgraded_team, active_pack_name, profile = assemble_team_with_us_upgrades(
            llm_model=llm_model,
            base_members=base_members,
            rfp_text_or_draft=analysis_text,
        )

        upgraded_team.print_response(
            analysis_text,
            stream=False,
            show_full_reasoning=False,
            stream_intermediate_steps=False,
            console=console,
        )
        
    except Exception as e:
        print(f"❌ Structured analysis failed: {e}")
        print("Falling back to original approach...")
        base_members = [
            rfp_analyzer_agent,
            proposal_outline_agent,
            outlining_compliance_agent,
            technology_agent,
            section_writing_agent,
            english_agent,
            tone_agent,
            proposal_scoring_agent,
        ]
        upgraded_team, active_pack_name, profile = assemble_team_with_us_upgrades(
            llm_model=llm_model,
            base_members=base_members,
            rfp_text_or_draft=rfp_text,
        )
        upgraded_team.print_response(
            rfp_text,
            stream=False,
            show_full_reasoning=False,
            stream_intermediate_steps=False,
            console=console,
        )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "output_proposals"
    os.makedirs(output_dir, exist_ok=True)
    pretty_filename = os.path.join(output_dir, f"proposal_pretty_{ts}.txt")
    console.save_text(pretty_filename)
    # Truncate to last 3000 lines if needed
    with open(pretty_filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) > 3000:
        with open(pretty_filename, "w", encoding="utf-8") as f:
            f.writelines(lines[-3000:])
        print(f"Output exceeded 3000 lines, truncated to last 3000 lines in {pretty_filename}")
    else:
        print(f"Saved pretty output to {pretty_filename}")


if __name__ == "__main__":
    main()
    
