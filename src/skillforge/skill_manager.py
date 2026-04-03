"""
Skill Manager — handles file I/O for SKILL.md files with backup support.

Each skill lives in its own directory under the skills root:
  skills/<skill-name>/SKILL.md

Backups are stored under a separate backup root:
  backups/<skill-name>/<timestamp>/SKILL.md (+ any supporting files)

SKILL.md uses YAML frontmatter (between --- markers) + markdown body.
"""

from __future__ import annotations

import fcntl
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import json
import yaml

# ---------------------------------------------------------------------------
# Name validation
# ---------------------------------------------------------------------------

_VALID_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{0,62}[a-z0-9]$|^[a-z0-9]$")


def validate_skill_name(name: str) -> str:
    """Validate and return a safe skill name.
    Allowed: lowercase letters, digits, hyphens. 1-64 chars. No leading/trailing hyphen."""
    if not _VALID_NAME_RE.match(name):
        raise ValueError(
            f"Invalid skill name '{name}'. "
            "Must be 1-64 chars, lowercase letters/digits/hyphens only, "
            "no leading or trailing hyphen."
        )
    return name


def _safe_resolve(base: Path, untrusted: str) -> Path:
    """Resolve a path and verify it stays within base directory."""
    resolved = (base / untrusted).resolve()
    base_resolved = base.resolve()
    if not (resolved == base_resolved or str(resolved).startswith(str(base_resolved) + "/")):
        raise ValueError(f"Path traversal detected: {untrusted}")
    return resolved


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

_RESERVED_KEYS = {"body", "path"}


@dataclass
class SkillMeta:
    name: str
    description: str
    extra: dict = field(default_factory=dict)


@dataclass
class Skill:
    meta: SkillMeta
    body: str
    path: Path

    def to_dict(self) -> dict:
        # Filter extra to avoid overwriting reserved fields
        safe_extra = {k: v for k, v in self.meta.extra.items() if k not in _RESERVED_KEYS}
        return {
            "name": self.meta.name,
            "description": self.meta.description,
            **safe_extra,
            "body": self.body,
            "path": str(self.path),
        }

    def summary(self) -> dict:
        return {
            "name": self.meta.name,
            "description": self.meta.description,
        }


# ---------------------------------------------------------------------------
# SKILL.md parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_skill_md(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter and markdown body from SKILL.md content."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_raw = m.group(1)
    body = text[m.end():]
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


def render_skill_md(frontmatter: dict, body: str) -> str:
    """Render a SKILL.md file from frontmatter dict and markdown body."""
    fm_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return f"---\n{fm_str}---\n\n{body}"


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------


class SkillManager:
    """Manages skills stored as <root>/<name>/SKILL.md with automatic backups."""

    def __init__(self, root: str | Path, backup_root: str | Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.backup_root = Path(backup_root).resolve()
        self.backup_root.mkdir(parents=True, exist_ok=True)

    def _skill_dir(self, name: str) -> Path:
        """Return skill directory path. Validates name to prevent traversal."""
        validate_skill_name(name)
        return self.root / name

    def _skill_file(self, name: str) -> Path:
        return self._skill_dir(name) / "SKILL.md"

    # ------------------------------------------------------------------
    # Backup
    # ------------------------------------------------------------------

    def _backup_dir(self, name: str) -> Path:
        validate_skill_name(name)
        return self.backup_root / name

    def backup_skill(self, name: str) -> Optional[Path]:
        """Snapshot the entire skill directory into backups/<name>/<timestamp>/.
        Returns the backup path, or None if the skill doesn't exist."""
        skill_dir = self._skill_dir(name)
        if not skill_dir.exists():
            return None
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        dest = self._backup_dir(name) / ts
        shutil.copytree(skill_dir, dest)
        return dest

    def list_backups(self, name: str) -> list[dict]:
        """Return all backups for a skill, newest first."""
        validate_skill_name(name)
        backup_dir = self._backup_dir(name)
        if not backup_dir.exists():
            return []
        results = []
        for d in sorted(backup_dir.iterdir(), reverse=True):
            if d.is_dir() and (d / "SKILL.md").exists():
                results.append({
                    "timestamp": d.name,
                    "path": str(d),
                })
        return results

    def restore_skill(self, name: str, timestamp: str) -> bool:
        """Restore a skill from a specific backup timestamp.
        Backs up the current version first (if it exists)."""
        validate_skill_name(name)
        backup_path = self._backup_dir(name) / timestamp
        # Verify backup path doesn't escape backup dir
        if not str(backup_path.resolve()).startswith(str(self._backup_dir(name).resolve()) + "/"):
            return False
        if not backup_path.exists():
            return False
        if self.skill_exists(name):
            self.backup_skill(name)
        skill_dir = self._skill_dir(name)
        if skill_dir.exists():
            shutil.rmtree(skill_dir)
        shutil.copytree(backup_path, skill_dir)
        return True

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def list_skills(self) -> list[dict]:
        """Return summary (name + description) of every skill."""
        results = []
        if not self.root.exists():
            return results
        for d in sorted(self.root.iterdir()):
            if d.is_dir() and (d / "SKILL.md").exists():
                # Only process valid skill names (skip stray directories)
                if not _VALID_NAME_RE.match(d.name):
                    continue
                skill = self.read_skill(d.name)
                if skill:
                    results.append(skill.summary())
        return results

    def read_skill(self, name: str) -> Optional[Skill]:
        """Read and parse a single skill."""
        path = self._skill_file(name)
        if not path.exists():
            return None
        text = path.read_text(encoding="utf-8")
        fm, body = parse_skill_md(text)
        meta = SkillMeta(
            name=fm.pop("name", name),
            description=fm.pop("description", ""),
            extra=fm,
        )
        return Skill(meta=meta, body=body, path=path)

    def save_skill(self, name: str, description: str, body: str, extra: Optional[dict] = None) -> tuple[Path, Optional[Path]]:
        """Create or overwrite a skill. Auto-backs up if updating.
        Returns (skill_path, backup_path_or_None)."""
        validate_skill_name(name)
        backup_path = None
        if self.skill_exists(name):
            backup_path = self.backup_skill(name)

        skill_dir = self._skill_dir(name)
        skill_dir.mkdir(parents=True, exist_ok=True)
        fm: dict = {"name": name, "description": description}
        if extra:
            fm.update(extra)
        content = render_skill_md(fm, body)
        path = self._skill_file(name)
        path.write_text(content, encoding="utf-8")
        return path, backup_path

    def delete_skill(self, name: str) -> Optional[Path]:
        """Delete a skill directory. Auto-backs up first.
        Returns backup path, or None if skill didn't exist."""
        validate_skill_name(name)
        if not self.skill_exists(name):
            return None
        backup_path = self.backup_skill(name)
        shutil.rmtree(self._skill_dir(name))
        return backup_path

    def skill_exists(self, name: str) -> bool:
        validate_skill_name(name)
        return self._skill_file(name).exists()

    # ------------------------------------------------------------------
    # Optimization history (atomic append)
    # ------------------------------------------------------------------

    def append_optimization_log(self, name: str, feedback: str, context: str) -> None:
        """Append an optimization entry with file locking for concurrency safety."""
        validate_skill_name(name)
        skill_dir = self._skill_dir(name)
        skill_dir.mkdir(parents=True, exist_ok=True)
        history_file = skill_dir / ".optimization_history.json"

        # Use file locking for atomic read-modify-write
        lock_file = skill_dir / ".optimization_history.lock"
        with open(lock_file, "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                history = []
                if history_file.exists():
                    try:
                        history = json.loads(history_file.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError):
                        history = []
                history.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "feedback": feedback,
                    "context": context,
                })
                history_file.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)

    def read_optimization_history(self, name: str) -> list[dict]:
        """Read optimization history for a skill."""
        validate_skill_name(name)
        history_file = self._skill_dir(name) / ".optimization_history.json"
        if not history_file.exists():
            return []
        try:
            return json.loads(history_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    # ------------------------------------------------------------------
    # Supporting files
    # ------------------------------------------------------------------

    def read_supporting_file(self, skill_name: str, relative_path: str) -> Optional[str]:
        """Read a supporting file from a skill directory."""
        validate_skill_name(skill_name)
        base = self._skill_dir(skill_name)
        path = _safe_resolve(base, relative_path)
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
        return None

    def save_supporting_file(self, skill_name: str, relative_path: str, content: str) -> Path:
        """Save a supporting file within a skill directory."""
        validate_skill_name(skill_name)
        base = self._skill_dir(skill_name)
        path = _safe_resolve(base, relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


