# Skill Writing & Optimization Guide

This guide is extracted from Anthropic's official skill-creator. Follow these principles when creating or optimizing skills.

## Skill File Structure

```
skill-name/
├── SKILL.md              # Entry point (required, <500 lines)
│   ├── YAML frontmatter  # name, description (required)
│   └── Markdown body     # Instructions
└── Bundled Resources (optional)
    ├── scripts/          # Executable code for deterministic tasks
    ├── references/       # Docs loaded into context as needed
    └── assets/           # Templates, icons, fonts
```

## SKILL.md Format

```yaml
---
name: skill-name            # lowercase, hyphens, max 64 chars
description: >
  What this skill does and when to trigger it.
  Front-load the key use case in the first 250 characters.
  Be slightly "pushy" — list specific trigger contexts to avoid under-triggering.
---

# Skill Instructions (markdown body)
```

## Frontmatter Fields

| Field | Type | Purpose |
|-------|------|---------|
| name | string | Identifier for `/skill-name` invocation |
| description | string | **Critical** — primary trigger mechanism. Include WHAT + WHEN |
| disable-model-invocation | bool | `true` = only user can invoke (for side-effect workflows) |
| user-invocable | bool | `false` = only LLM can invoke (background knowledge) |
| allowed-tools | string/list | Tools allowed without per-use approval |
| context | string | `fork` = run in isolated sub-agent |
| agent | string | Sub-agent type when `context: fork` |

## Writing Principles

### 1. Explain the WHY, not just the WHAT
Today's LLMs are smart. They have good theory of mind. Explain *why* something is important rather than piling on rigid MUSTs and NEVERs. If you find yourself writing ALL CAPS imperatives, reframe as reasoning.

### 2. Use Imperative Form
Write instructions as direct commands: "Read the config file", "Check for errors", not "You should read the config file".

### 3. Keep It Lean
- SKILL.md under 500 lines
- Move large references to `references/` with clear pointers
- For large reference files (>300 lines), include a table of contents
- Remove instructions that aren't pulling their weight

### 4. Progressive Disclosure (Three Levels)
1. **Metadata** (name + description) — Always in context (~100 words)
2. **SKILL.md body** — Loaded when skill triggers (<500 lines)
3. **Bundled resources** — Loaded as needed (unlimited size)

### 5. Description Writing
The description is the primary triggering mechanism. Be specific and slightly aggressive:

**Bad:** `"How to build a dashboard"`
**Good:** `"How to build a fast dashboard to display data. Use this skill whenever the user mentions dashboards, data visualization, metrics, or wants to display any kind of data, even if they don't explicitly ask for a 'dashboard.'"`

### 6. Include Examples
```markdown
## Output Format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### 7. Domain Organization
When a skill supports multiple domains, organize by variant:
```
cloud-deploy/
├── SKILL.md (workflow + selection logic)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

## Optimization Principles

When improving a skill based on feedback:

### 1. Generalize from Feedback
Don't overfit to specific examples. The skill will be used across many different prompts. Rather than fiddly, narrow fixes, try different metaphors or patterns.

### 2. Keep the Prompt Lean
Read transcripts, not just outputs. If the skill makes the model waste time on unproductive steps, remove those instructions.

### 3. Explain the Why
Understand the user's feedback deeply — what they actually want, not just what they literally said. Transmit that understanding into the instructions.

### 4. Bundle Repeated Work
If multiple runs independently write similar helper scripts, bundle that script into `scripts/` and reference it from the skill.

### 5. Draft → Review → Improve
Write a draft revision, then look at it with fresh eyes and improve. Consider:
- Is each instruction earning its place?
- Would a newcomer understand the reasoning?
- Are there contradictions or redundancies?

## Variable Substitutions

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed to skill |
| `$0`, `$1`, `$2` | Positional arguments |
| `${CLAUDE_SKILL_DIR}` | Directory containing SKILL.md |
| `` !`command` `` | Shell command output injected at load time |
