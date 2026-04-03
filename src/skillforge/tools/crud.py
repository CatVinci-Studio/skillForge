"""
CRUD tools — create, update, and delete skills (with auto-backup).

save_skill includes a hard validation gate: skills that fail structural
or content checks are rejected with actionable error messages.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from skillforge.response import respond, error
from skillforge.skill_manager import SkillManager
from skillforge.validator import validate_skill


def register(mcp: FastMCP, manager: SkillManager) -> None:
    """Register CRUD tools on the MCP server."""

    @mcp.tool()
    def save_skill(
        name: str,
        description: str,
        body: str,
        extra_frontmatter: Optional[str] = None,
    ) -> str:
        """Create or update a skill. Validates before saving, auto-backs up before overwrite.

        This tool enforces quality gates — if the skill fails validation,
        it will be REJECTED with specific error messages explaining what
        to fix. Fix the issues and call save_skill again.

        Validation checks:
        - Description must be >= 50 chars and explain WHAT + WHEN
        - Body must be 3-500 lines of actionable instructions
        - Description should include trigger conditions
        - Body should avoid overly rigid language (explain WHY instead)

        Args:
            name: Skill identifier (lowercase, hyphens, max 64 chars).
            description: What the skill does and when to trigger (>= 50 chars).
                         Front-load the key use case. Include trigger conditions
                         like 'Use this skill when...' or 'Activate whenever...'.
            body: Markdown body (3-500 lines). Follow the skill writing guide.
            extra_frontmatter: Optional JSON of additional frontmatter fields.
        """
        extra = {}
        if extra_frontmatter:
            try:
                extra = json.loads(extra_frontmatter)
            except json.JSONDecodeError:
                return error("extra_frontmatter must be valid JSON")

        # --- Hard validation gate ---
        validation = validate_skill(name, description, body)
        if not validation.passed:
            return respond({
                "status": "rejected",
                "skill": name,
                "validation": validation.to_dict(),
                "instruction": (
                    "Fix the errors listed above and call save_skill again. "
                    "Warnings are informational — the skill can be saved once "
                    "all errors are resolved."
                ),
            })

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
        if validation.warnings:
            result["warnings"] = validation.warnings
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
