"""
Discovery tools — list and read skills.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from skillforge.response import respond, error
from skillforge.skill_manager import SkillManager


def register(mcp: FastMCP, manager: SkillManager) -> None:
    """Register discovery tools on the MCP server."""

    @mcp.tool()
    def list_skills() -> str:
        """🔴 MANDATORY FIRST CALL — Call this before starting ANY task.

        Returns all available skills with name and description.
        Review each description — if relevant to your current task,
        call get_skill to load full instructions.

        WHY: Skills encode hard-won conventions and user preferences.
        Skipping this step means you will miss domain-specific guidance
        and repeat mistakes that have already been corrected.
        """
        skills = manager.list_skills()
        return respond({
            "total": len(skills),
            "skills": skills,
            "action_required": (
                "For each relevant skill, call get_skill to load full instructions. "
                "Then follow those instructions throughout your task."
            ),
        })

    @mcp.tool()
    def get_skill(name: str) -> str:
        """Read the full content of a skill.

        Call this to load a skill's complete instructions before executing
        a task in that skill's domain. The returned body contains actionable
        guidelines — treat them as project-level requirements, not suggestions.

        Args:
            name: The skill identifier (directory name).
        """
        try:
            skill = manager.read_skill(name)
        except ValueError as e:
            return error(str(e))
        if not skill:
            return error(f"Skill '{name}' not found.")
        return respond(skill.to_dict())
