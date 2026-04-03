"""
Optimization tools — skill improvement workflow and writing guide.

The optimization flow is designed to work reliably across any MCP client:
no sub-agent spawning is required. The tool returns structured guidance
that the LLM can follow directly, and save_skill enforces quality gates.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from skillforge.response import respond, error
from skillforge.skill_manager import SkillManager

GUIDE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "guide", "skill_writing_guide.md")


def register(mcp: FastMCP, manager: SkillManager) -> None:
    """Register optimization tools on the MCP server."""

    @mcp.tool()
    def get_skill_guide() -> str:
        """Get the Skill Writing & Optimization Guide.

        Call this BEFORE creating or modifying any skill. It covers: file format,
        writing principles, description optimization, and iterative improvement.

        WHY: Skills that ignore the guide tend to be either too rigid
        (walls of MUST/NEVER) or too vague (no actionable instructions).
        The guide teaches how to write skills that actually help.
        """
        try:
            guide = Path(GUIDE_PATH).read_text(encoding="utf-8")
        except FileNotFoundError:
            return error("Guide file not found.")
        return respond({"guide": guide})

    @mcp.tool()
    def request_skill_optimization(
        skill_name: str,
        feedback: str,
        context: str = "",
    ) -> str:
        """Prepare and return a structured optimization plan for a skill.

        Call this when user feedback indicates a skill needs improvement or
        a new skill should be created. Returns a step-by-step plan that you
        can follow directly — no sub-agent required.

        Recommended workflow:
        1. Call triage_skill_request first to check for existing skills
        2. Call this tool to get the optimization plan
        3. Call get_skill_guide to understand writing best practices
        4. Draft the skill content following the plan and guide
        5. Call save_skill — it will validate and reject if quality is insufficient

        Trigger signals to watch for:
        - User corrects your approach → existing skill may need updating
        - User states a preference ('always X', 'never Y') → skill candidate
        - Repeated pattern across conversation → new skill candidate
        - User explicitly mentions skills → act immediately

        Args:
            skill_name: Which skill to optimize (or create if it doesn't exist).
            feedback: The user feedback that triggered this optimization.
            context: Optional additional context about what went wrong or what
                     the user expects.
        """
        try:
            skill = manager.read_skill(skill_name)
        except ValueError as e:
            return error(str(e))

        current_content = None
        if skill:
            current_content = skill.to_dict()

        optimization_plan = {
            "action": "update" if skill else "create",
            "skill_name": skill_name,
            "feedback": feedback,
            "context": context or None,
            "current_skill": current_content,
            "steps": [
                "1. Call get_skill_guide() to review writing best practices.",
                f"2. {'Call get_skill(\'' + skill_name + '\') for the latest version.' if skill else 'This is a new skill — start from scratch.'}",
                "3. Analyze the feedback and determine what changes are needed.",
                "4. Draft the skill following these principles:",
                "   - Generalize: don't overfit to one specific case",
                "   - Keep lean: remove instructions that don't earn their place",
                "   - Explain WHY: reasoning > rigid imperatives",
                "   - Include trigger conditions in the description",
                "   - Bundle repeated patterns into reusable structure",
                "5. Call save_skill() with the drafted content.",
                "   → save_skill validates automatically and rejects if quality is insufficient.",
                "   → Fix any validation errors and retry.",
                "6. Confirm the result to the user.",
            ],
        }

        try:
            manager.append_optimization_log(skill_name, feedback, context)
        except ValueError:
            pass  # Skill doesn't exist yet — log will be created when skill is saved

        return respond({
            "status": "optimization_ready",
            "optimization_plan": optimization_plan,
        })

    @mcp.tool()
    def get_optimization_history(skill_name: str) -> str:
        """View the optimization history for a skill.

        Use this to understand how a skill has evolved over time and what
        feedback drove each change. Helpful before making further edits
        to avoid reverting previous improvements.

        Args:
            skill_name: The skill to check.
        """
        try:
            history = manager.read_optimization_history(skill_name)
        except ValueError as e:
            return error(str(e))
        return respond({"skill": skill_name, "history": history})
