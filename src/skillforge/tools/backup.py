"""
Backup & restore tools — manage skill version history.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from skillforge.response import respond, error
from skillforge.skill_manager import SkillManager


def register(mcp: FastMCP, manager: SkillManager) -> None:
    """Register backup and restore tools on the MCP server."""

    @mcp.tool()
    def list_backups(name: str) -> str:
        """List all backups for a skill, newest first.

        Use this to inspect version history before restoring or to verify
        that a backup was created after a save/delete operation.

        Args:
            name: The skill identifier.
        """
        try:
            backups = manager.list_backups(name)
        except ValueError as e:
            return error(str(e))
        return respond({
            "skill": name,
            "total": len(backups),
            "backups": backups,
        })

    @mcp.tool()
    def restore_skill(name: str, timestamp: str) -> str:
        """Restore a skill from a specific backup. Current version is backed up first.

        Use this when a skill optimization went wrong and you need to roll back.
        The current version is always saved before overwriting, so no data is lost.

        Args:
            name: The skill identifier.
            timestamp: Backup timestamp (from list_backups output).
        """
        try:
            if not manager.list_backups(name):
                return error(f"No backups for skill '{name}'.")
            success = manager.restore_skill(name, timestamp)
        except ValueError as e:
            return error(str(e))
        if not success:
            return error(f"Backup '{timestamp}' not found for '{name}'.")
        return respond({
            "status": "ok",
            "restored": name,
            "from_backup": timestamp,
        })
