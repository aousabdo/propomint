# === policy_packs.py ===
import os, json
from typing import Dict, Any

# Two US-focused packs only (federal/state/local vs private sector).
POLICY_PACKS: Dict[str, Dict[str, Any]] = {
    "US_GOV": {
        "name": "US_GOV",
        "controls": ["NIST_800_53", "FedRAMP_optional"],
        "accessibility": ["Section_508", "WCAG_2_2_AA_optional"],
        "privacy": ["Privacy_Act", "CCPA_optional", "GDPR_optional"],
        "scrm": {"sbom": True, "section_889": True, "kaspersky": True},
        "scoring": {"Compliance": 30, "Technical": 30, "PM": 20, "SecurityPrivacy": 15, "Clarity": 5},
    },
    "US_COMMERCIAL": {
        "name": "US_COMMERCIAL",
        "controls": ["ISO_27001", "SOC2"],
        "accessibility": ["WCAG_2_2_AA"],
        "privacy": ["CCPA", "GDPR_optional"],
        "scrm": {"sbom": True, "section_889": False, "kaspersky": False},
        "scoring": {"Compliance": 25, "Technical": 35, "PM": 20, "SecurityPrivacy": 15, "Clarity": 5},
    },
}

DEFAULT_POLICY_PACK = os.getenv("DEFAULT_POLICY_PACK", "US_COMMERCIAL")

def select_policy_pack(profile: Dict[str, Any]) -> str:
    """
    Input example (from profiler):
    {
      "domain": "US_GOV" | "US_COMMERCIAL",
      "frameworks": ["NIST_800_53","508"] or ["ISO_27001","SOC2","WCAG_2_2"],
      "flags": ["SECTION_889","KASPERSKY"],
      "open_questions": [...]
    }
    """
    domain = (profile or {}).get("domain", "").upper()
    if domain in POLICY_PACKS:
        return domain
    # Signal-based fallback
    frameworks = set((profile or {}).get("frameworks", []))
    if {"NIST_800_53", "508"} & frameworks:
        return "US_GOV"
    if {"ISO_27001", "SOC2", "WCAG_2_2"} & frameworks:
        return "US_COMMERCIAL"
    return DEFAULT_POLICY_PACK

def inject_pack_context(instructions: list, pack_name: str) -> list:
    """Prepend a small, stable context block to any agent's instructions."""
    pack = POLICY_PACKS[pack_name]
    ctx = (
        "ACTIVE_POLICY_PACK:\n"
        + json.dumps(pack, ensure_ascii=False, indent=2)
        + "\n"
        "Use the ACTIVE_POLICY_PACK to adapt frameworks, accessibility, SCRM toggles, "
        "and scoring posture. Do not mention non-applicable frameworks."
    )
    return [ctx] + instructions
