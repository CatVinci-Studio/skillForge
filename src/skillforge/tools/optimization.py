"""
Optimization tools — skill improvement workflow and writing guide.
"""

from __future__ import annotations

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

        The sub-agent MUST call this BEFORE creating or modifying any skill.
        It covers: file format, writing principles, description optimization,
        and iterative improvement techniques.

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
        """Prepare a skill optimization task for a sub-agent.

        Call this when user feedback indicates a skill needs improvement or
        a new skill should be created. Returns a structured prompt to pass
        to a dedicated sub-agent.

        ⚠️ After calling this, SPAWN A SUB-AGENT with the returned prompt.
        Run it in the background so the main task is not blocked.

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

        if skill:
            import json
            current_content = (
                f"\n\n## Current Skill Content\n```\n"
                f"{json.dumps(skill.to_dict(), ensure_ascii=False, indent=2)}\n```"
            )
        else:
            current_content = f"\n\n## Note\nSkill '{skill_name}' does not exist yet — create it."

        agent_prompt = (
            f"# Skill Optimization Task\n\n"
            f"You are a skill-optimization sub-agent for SkillForge. Your job is to\n"
            f"improve (or create) a skill based on user feedback.\n\n"
            f"## Feedback\n{feedback}\n\n"
            f"## Context\n{context if context else 'No additional context.'}\n"
            f"{current_content}\n\n"
            f"## Steps\n"
            f"1. Call `get_skill_guide()` — read the writing best practices.\n"
            f"2. If updating: call `get_skill('{skill_name}')` for the latest version.\n"
            f"3. Analyze feedback → determine changes needed.\n"
            f"4. Apply optimization principles:\n"
            f"   - Generalize (don't overfit to one case)\n"
            f"   - Keep lean (remove what doesn't work)\n"
            f"   - Explain WHY behind each instruction\n"
            f"   - Bundle repeated patterns into reusable structure\n"
            f"5. Call `save_skill()` with improved content. (Auto-backed up.)\n"
            f"6. Report: what changed and why.\n\n"
            f"The skill will be used across many future tasks — make improvements "
            f"that generalize, not narrow fixes for a single case."
        )

        try:
            manager.append_optimization_log(skill_name, feedback, context)
        except ValueError:
            pass  # Skill doesn't exist yet — log will be created when skill is saved

        return respond({
            "status": "optimization_ready",
            "skill_name": skill_name,
            "agent_prompt": agent_prompt,
            "instruction": (
                "Spawn a sub-agent with the agent_prompt above. "
                "Use subagent_type='general-purpose' and run_in_background=true. "
                "The sub-agent has access to SkillForge MCP tools."
            ),
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
