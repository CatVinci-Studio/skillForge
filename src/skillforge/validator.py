"""
Skill Validator — hard validation gates for skill quality control.

Runs automatically before every save_skill call. Returns errors (block save)
and warnings (allow save but inform). This is the primary quality mechanism
in SkillForge — since we cannot control LLM behavior through prompts alone,
we enforce quality at the tool boundary.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_DESCRIPTION_LENGTH = 50
MAX_DESCRIPTION_LENGTH = 1000
MAX_BODY_LINES = 500
MIN_BODY_LINES = 3

# Trigger keywords that suggest a good description includes WHEN to activate
_TRIGGER_PATTERNS = re.compile(
    r"(when|whenever|if the user|use this skill|trigger|activate|invoke|"
    r"applies when|relevant when|also activate|even if)",
    re.IGNORECASE,
)

# Overly rigid language that suggests poor skill writing
_RIGID_PATTERNS = re.compile(
    r"\b(YOU MUST ALWAYS|NEVER EVER|ABSOLUTELY MUST|STRICTLY FORBIDDEN)\b",
)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
        }


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------


def validate_skill(name: str, description: str, body: str) -> ValidationResult:
    """Validate a skill before saving. Returns errors and warnings."""
    result = ValidationResult()

    # --- Description checks ---
    desc_len = len(description.strip())
    if desc_len < MIN_DESCRIPTION_LENGTH:
        result.errors.append(
            f"Description too short ({desc_len} chars, minimum {MIN_DESCRIPTION_LENGTH}). "
            f"A good description explains WHAT the skill does and WHEN to trigger it. "
            f"Example: 'Guidelines for reviewing code changes. Use this skill whenever "
            f"the user asks for a code review, PR review, or feedback on code quality.'"
        )
    elif desc_len > MAX_DESCRIPTION_LENGTH:
        result.warnings.append(
            f"Description is very long ({desc_len} chars). Consider keeping it under "
            f"{MAX_DESCRIPTION_LENGTH} chars — move details to the body instead."
        )

    if description.strip() and not _TRIGGER_PATTERNS.search(description):
        result.warnings.append(
            "Description lacks trigger conditions. A good description tells the LLM "
            "WHEN to activate this skill (e.g., 'Use this skill when...', "
            "'Activate whenever the user...'). Without trigger conditions, "
            "the skill may not be loaded when it should be."
        )

    # --- Body checks ---
    body_lines = body.strip().splitlines()
    num_lines = len(body_lines)

    if num_lines < MIN_BODY_LINES:
        result.errors.append(
            f"Body too short ({num_lines} lines, minimum {MIN_BODY_LINES}). "
            f"A skill body should contain actionable instructions, not just a title."
        )
    elif num_lines > MAX_BODY_LINES:
        result.errors.append(
            f"Body too long ({num_lines} lines, maximum {MAX_BODY_LINES}). "
            f"Move large reference material to supporting files within the skill directory."
        )

    if body.strip() and _RIGID_PATTERNS.search(body):
        result.warnings.append(
            "Body contains overly rigid language (e.g., 'YOU MUST ALWAYS', 'NEVER EVER'). "
            "Modern LLMs respond better to reasoning — explain WHY something matters "
            "instead of using rigid imperatives."
        )

    # --- Cross-field checks ---
    if name.strip() and description.strip():
        # Check if description is just the name repeated
        if description.strip().lower().replace("-", " ") == name.strip().lower().replace("-", " "):
            result.errors.append(
                "Description is identical to the skill name. "
                "The description should explain what the skill does and when to use it."
            )

    return result
