"""
Triage tools — help the LLM decide whether to create, improve, or reuse a skill.

Unlike tripleyak's approach (LLM-powered semantic matching inside the skill),
we provide structured information and let the calling LLM make the routing
decision. This works reliably across any MCP client.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from skillforge.response import respond, error
from skillforge.skill_manager import SkillManager


def register(mcp: FastMCP, manager: SkillManager) -> None:
    """Register triage tools on the MCP server."""

    @mcp.tool()
    def triage_skill_request(intent: str) -> str:
        """Analyze intent against existing skills to decide the best action.

        Call this BEFORE creating or optimizing a skill. It returns all existing
        skills with their descriptions so you can determine:

        - **REUSE**: An existing skill already covers this need (match >= 80%).
          → Just call get_skill to load it.
        - **IMPROVE**: An existing skill partially covers this (match 50-79%).
          → Call request_skill_optimization with the existing skill name.
        - **CREATE**: No existing skill is relevant (match < 50%).
          → Call request_skill_optimization with a new skill name.

        You (the LLM) make the routing decision — this tool provides the
        information you need to decide.

        Args:
            intent: What the user wants or the feedback that triggered this.
                    Be specific — include the domain, task type, and context.
        """
        skills = manager.list_skills()

        if not skills:
            return respond({
                "intent": intent,
                "existing_skills": [],
                "total": 0,
                "recommendation": (
                    "No existing skills found. If this intent represents a reusable "
                    "pattern, create a new skill via request_skill_optimization."
                ),
            })

        # Load full descriptions for better matching by the LLM
        skill_details = []
        for s in skills:
            full = manager.read_skill(s["name"])
            if full:
                skill_details.append({
                    "name": full.meta.name,
                    "description": full.meta.description,
                    "body_preview": full.body[:300] + "..." if len(full.body) > 300 else full.body,
                })

        return respond({
            "intent": intent,
            "existing_skills": skill_details,
            "total": len(skill_details),
            "decision_guide": {
                "REUSE": "An existing skill already covers this intent well. Load it with get_skill.",
                "IMPROVE": "An existing skill partially covers this. Optimize it with request_skill_optimization using the existing skill name.",
                "CREATE": "No existing skill matches. Create a new one with request_skill_optimization using a new skill name.",
            },
            "instruction": (
                "Compare the intent against each existing skill's description. "
                "Decide REUSE / IMPROVE / CREATE based on relevance. "
                "Explain your reasoning briefly before acting."
            ),
        })
