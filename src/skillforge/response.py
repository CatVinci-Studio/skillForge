"""
Response formatting utilities for SkillForge MCP tools.

Every tool response is wrapped with a feedback-monitoring reminder so the LLM
continuously watches for skill-improvement opportunities.
"""

from __future__ import annotations

import json

# ---------------------------------------------------------------------------
# Feedback monitor — appended to EVERY tool response
# ---------------------------------------------------------------------------

_FEEDBACK_MONITOR = {
    "_skillforge_monitor": {
        "always_active": True,
        "instruction": (
            "After EVERY user message, silently evaluate: does this message contain "
            "feedback that could improve an existing skill or justify a new one? "
            "Signals: corrections ('not like that'), preferences ('always/never do X'), "
            "repeated patterns, explicit requests. "
            "If YES → call request_skill_optimization and spawn a background sub-agent. "
            "If UNSURE → do nothing, but stay alert for the next message."
        ),
    },
}


def respond(data: dict) -> str:
    """Wrap a tool response with the feedback monitor reminder."""
    return json.dumps({**data, **_FEEDBACK_MONITOR}, ensure_ascii=False, indent=2)


def error(msg: str) -> str:
    """Return a standardized error response."""
    return respond({"error": msg})
