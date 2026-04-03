"""
CRUD tools — create, update, and delete skills (with auto-backup).
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from skillforge.response import respond, error
from skillforge.skill_manager import SkillManager


def register(mcp: FastMCP, manager: SkillManager) -> None:
    """Register CRUD tools on the MCP server."""

    @mcp.tool()
    def save_skill(
        name: str,
        description: str,
        body: str,
        extra_frontmatter: Optional[str] = None,
    ) -> str:
        """Create or update a skill. Auto-backs up before overwrite.

        ⚠️ Should be called by a SKILL-OPTIMIZATION SUB-AGENT, not the
        main agent. The sub-agent workflow: get_skill_guide → draft → save_skill.

        WHY this restriction exists: skill edits affect every future conversation.
        A dedicated sub-agent can focus on writing high-quality, generalizable
        instructions without being distracted by the user's current task.

        Args:
            name: Skill identifier (lowercase, hyphens, max 64 chars).
            description: What the skill does and when to trigger (~250 chars).
                         Front-load the key use case. Be specific about trigger
                         contexts to avoid under-triggering.
            body: Markdown body (<500 lines). Follow the skill writing guide.
            extra_frontmatter: Optional JSON of additional frontmatter fields.
        """
        extra = {}
        if extra_frontmatter:
            try:
                extra = json.loads(extra_frontmatter)
            except json.JSONDecodeError:
                return error("extra_frontmatter must be valid JSON")

        try:
            is_update = manager.skill_exists(name)
            path, backup_path = manager.save_skill(name, description, body, extra or None)
        except ValueError as e:
            return error(str(e))

        result = {
            "status": "ok",
            "action": "updated" if is_update else "created",
            "skill": name,
            "path": str(path),
        }
        if backup_path:
            result["backup"] = str(backup_path)
            result["restore_hint"] = f"restore_skill(name='{name}', timestamp='{backup_path.name}')"
        return respond(result)

    @mcp.tool()
    def delete_skill(name: str, confirm: bool = False) -> str:
        """Delete a skill permanently. Auto-backs up before deletion.

        This is a destructive operation — the skill will be removed from the
        active library. A backup is always created so it can be restored later
        if needed.

        Args:
            name: Skill identifier to delete.
            confirm: Must be True to actually delete. This two-step confirmation
                     prevents accidental deletions.
        """
        if not confirm:
            return respond({
                "status": "blocked",
                "message": f"Call again with confirm=True to delete '{name}'. It will be backed up first.",
            })
        try:
            backup_path = manager.delete_skill(name)
        except ValueError as e:
            return error(str(e))
        if backup_path is None:
            return error(f"Skill '{name}' not found.")
        return respond({
            "status": "ok",
            "deleted": name,
            "backup": str(backup_path),
            "restore_hint": f"restore_skill(name='{name}', timestamp='{backup_path.name}')",
        })
