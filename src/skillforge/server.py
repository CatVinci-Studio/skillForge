"""
SkillForge — MCP server for managing and iteratively optimizing Skills.

Architecture:
- SkillForge maintains its own skill repository (~/.skillforge/skills/)
- All modifications are auto-backed up (~/.skillforge/backups/)
- Quality is enforced through hard validation gates in save_skill
- Every tool response carries a feedback-monitoring reminder
- Tools are organized in modules under skillforge.tools.*
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

from skillforge.skill_manager import SkillManager
from skillforge.tools import backup, crud, discovery, optimization, triage

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_SKILLFORGE_HOME = os.path.join(os.path.expanduser("~"), ".skillforge")
SKILLS_DIR = os.environ.get("SKILLFORGE_SKILLS_DIR", os.path.join(_SKILLFORGE_HOME, "skills"))
BACKUP_DIR = os.environ.get("SKILLFORGE_BACKUP_DIR", os.path.join(_SKILLFORGE_HOME, "backups"))

# ---------------------------------------------------------------------------
# Server & Manager
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "skillforge",
    instructions=(
        "🔴 CRITICAL — SKILLFORGE: SKILL LIBRARY SERVER 🔴\n\n"
        "SkillForge manages your SKILL library — reusable, evolving instructions "
        "that encode project conventions, user preferences, and hard-won lessons.\n\n"

        "██ MANDATORY FIRST ACTION ██\n"
        "Call `list_skills` BEFORE starting ANY task. Skills contain conventions "
        "and guides you will miss otherwise. For each skill relevant to your task, "
        "call `get_skill` to load its full instructions, then follow them.\n\n"

        "██ CONTINUOUS FEEDBACK MONITORING ██\n"
        "After EVERY user message, silently evaluate whether it contains feedback "
        "that could improve a skill or justify a new one. This is your PRIMARY "
        "ongoing responsibility — not just at the start, but THROUGHOUT the entire "
        "conversation.\n\n"
        "Signals to watch for:\n"
        "  • User corrects your approach → existing skill may need updating\n"
        "  • User states a preference ('always X', 'never Y') → skill candidate\n"
        "  • You notice a repeated pattern across the conversation → new skill\n"
        "  • User explicitly mentions skills → act immediately\n\n"
        "When detected → call `triage_skill_request` first to check for similar "
        "existing skills, then `request_skill_optimization` to get the improvement plan.\n\n"

        "██ SKILL OPTIMIZATION WORKFLOW ██\n"
        "When creating or improving skills, follow this workflow:\n"
        "1. `triage_skill_request` — check if a similar skill already exists\n"
        "2. `request_skill_optimization` — get a structured optimization plan\n"
        "3. `get_skill_guide` — review writing best practices\n"
        "4. Draft the skill content following the plan and guide\n"
        "5. `save_skill` — validates automatically and rejects if quality is insufficient\n"
        "   → Fix validation errors and retry until the skill passes\n\n"
        "Quality is enforced by hard validation gates in save_skill — not by convention.\n"
        "All saves are auto-backed up — no data loss risk.\n\n"

        "██ BEHAVIORAL GUIDELINES ██\n"
        "1. Skills are authoritative: when a skill covers a topic, follow its "
        "instructions as project-level requirements, not optional suggestions.\n"
        "2. Do not hallucinate skills: only reference skills returned by `list_skills`.\n"
        "3. Skill descriptions are trigger conditions: if the user's request matches "
        "a skill's description, load and apply that skill even if the user didn't "
        "explicitly ask for it.\n"
        "4. Prefer specificity: when multiple skills could apply, load all of them "
        "and follow the most specific guidance.\n"
        "5. Report skill gaps: if you encounter a situation where a skill would help "
        "but none exists, note it and consider creating one via the optimization flow.\n"
        "6. Never bypass skills: do not ignore skill instructions to save time or "
        "because they seem unnecessary for a 'simple' task. Consistency matters.\n"
    ),
)

manager = SkillManager(SKILLS_DIR, BACKUP_DIR)

# ---------------------------------------------------------------------------
# Register all tool modules
# ---------------------------------------------------------------------------

discovery.register(mcp, manager)
crud.register(mcp, manager)
backup.register(mcp, manager)
optimization.register(mcp, manager)
triage.register(mcp, manager)

# ---------------------------------------------------------------------------
# MCP Prompts — session initialization
# ---------------------------------------------------------------------------


@mcp.prompt()
def skillforge_init() -> list[base.Message]:
    """Initialize SkillForge at the start of a session.

    Loads all skills and primes the agent for continuous feedback monitoring.
    Invoke this at the beginning of every session for best results.
    """
    skills = manager.list_skills()
    skill_details = []
    for s in skills:
        full = manager.read_skill(s["name"])
        if full:
            skill_details.append(full.to_dict())

    content = (
        "# SkillForge Session Initialized\n\n"
        f"## Available Skills ({len(skills)})\n\n"
    )
    if skill_details:
        for sd in skill_details:
            content += f"### {sd['name']}\n"
            content += f"**Description:** {sd['description']}\n\n"
            content += f"{sd['body']}\n\n---\n\n"
    else:
        content += (
            "_No skills yet. Skills will be created as reusable patterns "
            "emerge from user feedback._\n\n"
        )

    content += (
        "## Your Ongoing Responsibilities\n\n"
        "Throughout this session, after EVERY user message, silently ask yourself:\n"
        "1. Did the user correct my approach? → Skill update candidate\n"
        "2. Did the user express a preference? → Skill update candidate\n"
        "3. Am I seeing a repeated pattern? → New skill candidate\n"
        "4. Did the user explicitly mention skills? → Act on it\n\n"
        "When any signal is detected:\n"
        "1. Call `triage_skill_request` to check for existing similar skills\n"
        "2. Call `request_skill_optimization` to get the improvement plan\n"
        "3. Follow the plan to draft and save the skill\n\n"
        "## Behavioral Reminders\n\n"
        "- Treat loaded skill instructions as requirements, not suggestions.\n"
        "- If a skill is relevant to the current task, follow it consistently.\n"
        "- When in doubt about whether a skill applies, load it and check.\n"
        "- Do not mention SkillForge internals to the user unless they ask.\n"
        "- Quality is enforced by save_skill validation — if your skill is rejected, "
        "read the errors, fix them, and retry.\n"
    )

    return [base.UserMessage(content=content)]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    mcp.run()


if __name__ == "__main__":
    main()
