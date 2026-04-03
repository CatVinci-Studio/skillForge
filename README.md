<p align="center">
  <img src="https://img.shields.io/pypi/v/skillforge-mcp?style=for-the-badge&logo=pypi&logoColor=white&label=PyPI" alt="PyPI"/>
  <img src="https://img.shields.io/badge/MCP-Server-blueviolet?style=for-the-badge" alt="MCP Server"/>
  <img src="https://img.shields.io/badge/python-≥3.10-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/github/stars/CatVinci-Studio/skillForge?style=for-the-badge&logo=github" alt="Stars"/>
</p>

<h1 align="center">🛠️ SkillForge</h1>

<p align="center">
  <strong>An MCP server that makes your AI agent learn and evolve — one skill at a time.</strong>
</p>

<p align="center">
  <em>Skills are reusable instructions that get better with every conversation.</em>
</p>

<p align="center">
  <a href="README_CN.md">🇨🇳 中文文档</a> · <a href="https://pypi.org/project/skillforge-mcp/">📦 PyPI</a> · <a href="https://github.com/CatVinci-Studio/skillForge/issues">🐛 Issues</a>
</p>

---

## ✨ What is SkillForge?

SkillForge is a **Model Context Protocol (MCP) server** that gives your AI agent a persistent, evolving skill library. Instead of repeating the same corrections and preferences every session, SkillForge captures them as **skills** — structured instructions that the agent loads and follows automatically.

> 💡 Think of it as **muscle memory for your AI** — it learns your conventions once and applies them forever.

### 🔄 The Feedback Loop

```
  👤 User gives feedback
        │
        ▼
  🔍 Agent detects improvement signal
        │
        ▼
  🔀 Triage: reuse / improve / create?
        │
        ▼
  ✏️ Draft skill following guide + plan
        │
        ▼
  🛡️ Validation gate (reject or pass)
        │
        ▼
  💾 Skill saved (auto-backed up)
        │
        ▼
  ✅ Next task uses improved skill
```

---

## 🚀 Quick Start

### 📦 Installation

```bash
# Install from PyPI (recommended)
pip install skillforge-mcp

# Or with uv
uv pip install skillforge-mcp
```

### ⚡ Run the Server

```bash
# Run directly
skillforge

# Or run without installing via uvx
uvx skillforge-mcp
```

### 🔌 Connect to Claude Code

Add to your MCP config:

```json
{
  "mcpServers": {
    "skillforge": {
      "command": "uvx",
      "args": ["skillforge-mcp"]
    }
  }
}
```

<details>
<summary>💡 Alternative: install from source</summary>

```bash
git clone https://github.com/CatVinci-Studio/skillForge.git
cd skillForge
pip install -e .
```

</details>

---

## 🧩 Architecture

```
src/skillforge/
├── 🏠 server.py              # MCP server definition & prompts
├── 📨 response.py            # Response formatting & feedback monitor
├── 🛡️ validator.py           # Hard validation gates for skill quality
├── 📁 skill_manager.py       # Core CRUD, backup, restore logic
├── 🔧 tools/
│   ├── 🔍 discovery.py       # list_skills, get_skill
│   ├── ✏️  crud.py            # save_skill (with validation), delete_skill
│   ├── 💾 backup.py          # list_backups, restore_skill
│   ├── 🔀 triage.py          # triage_skill_request
│   └── 🧠 optimization.py    # get_skill_guide, request_skill_optimization
└── 📖 guide/
    └── skill_writing_guide.md # Best practices for skill authoring
```

### 📂 Runtime Data

SkillForge stores its data in `~/.skillforge/`:

| Directory | Purpose |
|-----------|---------|
| `~/.skillforge/skills/` | 📚 Active skill library |
| `~/.skillforge/backups/` | 🗄️ Automatic version history |

> 🔒 Override with `SKILLFORGE_SKILLS_DIR` and `SKILLFORGE_BACKUP_DIR` environment variables.

---

## 🔧 Available Tools

| Tool | Description |
|------|-------------|
| 🔍 `list_skills` | List all skills — **mandatory first call** before any task |
| 📖 `get_skill` | Load full skill instructions by name |
| 🔀 `triage_skill_request` | Check existing skills before creating/improving — prevents duplication |
| 🧠 `request_skill_optimization` | Get a structured plan for skill improvement |
| 📖 `get_skill_guide` | Load the skill writing best practices guide |
| ✏️ `save_skill` | Create or update a skill — **validates and rejects if quality is insufficient** |
| 🗑️ `delete_skill` | Remove a skill (two-step confirmation, auto-backup) |
| 📋 `list_backups` | View version history for a skill |
| ⏪ `restore_skill` | Roll back to a previous version |
| 📊 `get_optimization_history` | View the feedback log that drove skill changes |

---

## 🛡️ Quality Gates (v0.2.0)

Unlike prompt-based quality control that depends on LLM compliance, SkillForge enforces quality through **hard validation gates** in `save_skill`:

| Check | Type | Rule |
|-------|------|------|
| 📏 Description length | ❌ Error | Must be ≥ 50 characters |
| 📏 Body length | ❌ Error | Must be 3–500 lines |
| 🔄 Description ≠ name | ❌ Error | Description must explain, not repeat the name |
| 🎯 Trigger conditions | ⚠️ Warning | Should include "when/whenever/use this skill..." |
| 🗣️ Rigid language | ⚠️ Warning | Prefer reasoning over "YOU MUST ALWAYS" imperatives |
| 📐 Description too long | ⚠️ Warning | Keep under 1000 chars, move details to body |

> 🔴 **Errors** block the save — fix them and retry.
> 🟡 **Warnings** allow the save but flag areas for improvement.

### 🔀 Skill Triage

Before creating a new skill, `triage_skill_request` returns all existing skills so the LLM can decide:

| Decision | Condition | Action |
|----------|-----------|--------|
| **REUSE** | Existing skill covers the need | Load it with `get_skill` |
| **IMPROVE** | Existing skill partially covers it | Optimize with `request_skill_optimization` |
| **CREATE** | No relevant skill exists | Create via `request_skill_optimization` |

---

## 📝 Skill Format

Each skill lives in its own directory as a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: my-skill
description: >
  What this skill does and when to trigger it.
  Use this skill whenever the user asks for...
  Also activate when...
---

# Skill Instructions

Your markdown instructions here...
```

### 🏷️ Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Identifier (`lowercase-with-hyphens`, max 64 chars) |
| `description` | ✅ | Trigger conditions — WHAT it does + WHEN to use it (≥ 50 chars) |
| `disable-model-invocation` | ❌ | `true` = only user can invoke |
| `user-invocable` | ❌ | `false` = only LLM can invoke |
| `allowed-tools` | ❌ | Tools allowed without per-use approval |
| `context` | ❌ | `fork` = run in isolated sub-agent |

---

## 🧠 How Optimization Works

SkillForge continuously monitors conversations for improvement signals:

| Signal | Example | Action |
|--------|---------|--------|
| 🔴 **Correction** | "No, don't mock the database" | Update relevant skill |
| 🟡 **Preference** | "Always use snake_case" | Create or update skill |
| 🔵 **Pattern** | Same structure used 3+ times | Bundle into new skill |
| 🟢 **Explicit** | "Add this to the review skill" | Direct skill edit |

### 🔒 Safety Guarantees

- ✅ **Auto-backup** before every save and delete
- ✅ **One-click restore** from any backup timestamp
- ✅ **Path traversal protection** on all file operations
- ✅ **Atomic writes** with file locking for optimization logs
- ✅ **Hard validation gates** — quality enforced at the tool boundary, not by prompt

---

## 🌟 Why SkillForge?

| Without SkillForge | With SkillForge |
|---------------------|-----------------|
| 😤 Repeat the same corrections every session | 🧠 Agent remembers and applies automatically |
| 📋 Conventions scattered across docs | 📦 Single source of truth per topic |
| 🎲 Inconsistent agent behavior | ✅ Deterministic, skill-guided responses |
| 🔄 No learning from feedback | 📈 Skills evolve with every interaction |
| 🤞 Hope the LLM follows quality guidelines | 🛡️ Hard validation rejects low-quality skills |

---

## 🛣️ Roadmap

- [x] 🛡️ Hard validation gates for skill quality
- [x] 🔀 Skill triage to prevent duplication
- [ ] 🌐 Skill sharing & import from remote repositories
- [ ] 📊 Analytics dashboard for skill usage & effectiveness
- [ ] 🔗 Cross-skill dependency management
- [ ] 🧪 Skill testing framework with evaluation harness
- [ ] 🏪 Community skill marketplace

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Built with ❤️ by <a href="https://github.com/CatVinci-Studio">CatVinci Studio</a></strong>
</p>

<p align="center">
  <em>Forging better AI, one skill at a time. 🔨</em>
</p>
