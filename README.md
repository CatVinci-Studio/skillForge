<p align="center">
  <img src="https://img.shields.io/badge/MCP-Server-blueviolet?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTEyIDJMMiA3bDEwIDUgMTAtNS0xMC01ek0yIDE3bDEwIDUgMTAtNS0xMC01LTEwIDV6TTIgMTJsMTAgNSAxMC01LTEwLTUtMTAgNXoiLz48L3N2Zz4=" alt="MCP Server"/>
  <img src="https://img.shields.io/badge/python-≥3.10-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/badge/status-beta-orange?style=for-the-badge" alt="Status"/>
</p>

<h1 align="center">🛠️ SkillForge</h1>

<p align="center">
  <strong>An MCP server that makes your AI agent learn and evolve — one skill at a time.</strong>
</p>

<p align="center">
  <em>Skills are reusable instructions that get better with every conversation.</em>
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
  🤖 Sub-agent optimizes the skill
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
├── 📁 skill_manager.py       # Core CRUD, backup, restore logic
├── 🔧 tools/
│   ├── 🔍 discovery.py       # list_skills, get_skill
│   ├── ✏️  crud.py            # save_skill, delete_skill
│   ├── 💾 backup.py          # list_backups, restore_skill
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

| Tool | Description | Who Calls It |
|------|-------------|--------------|
| 🔍 `list_skills` | List all skills (mandatory first call!) | 🤖 Agent |
| 📖 `get_skill` | Load full skill instructions | 🤖 Agent |
| ✏️ `save_skill` | Create or update a skill | 🤖 Sub-agent |
| 🗑️ `delete_skill` | Remove a skill (with confirmation) | 🤖 Sub-agent |
| 📋 `list_backups` | View version history for a skill | 🤖 Agent |
| ⏪ `restore_skill` | Roll back to a previous version | 🤖 Agent |
| 📖 `get_skill_guide` | Load the skill writing guide | 🤖 Sub-agent |
| 🧠 `request_skill_optimization` | Trigger skill improvement | 🤖 Agent |
| 📊 `get_optimization_history` | View optimization log | 🤖 Agent |

---

## 📝 Skill Format

Each skill lives in its own directory as a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: my-skill
description: >
  What this skill does and when to trigger it.
  Be specific about trigger contexts.
---

# Skill Instructions

Your markdown instructions here...
```

### 🏷️ Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Identifier (`lowercase-with-hyphens`, max 64 chars) |
| `description` | ✅ | Trigger conditions — WHAT it does + WHEN to use it |
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
- ✅ **Sub-agent isolation** — skill edits don't interrupt your main task

---

## 🌟 Why SkillForge?

| Without SkillForge | With SkillForge |
|---------------------|-----------------|
| 😤 Repeat the same corrections every session | 🧠 Agent remembers and applies automatically |
| 📋 Conventions scattered across docs | 📦 Single source of truth per topic |
| 🎲 Inconsistent agent behavior | ✅ Deterministic, skill-guided responses |
| 🔄 No learning from feedback | 📈 Skills evolve with every interaction |

---

## 🛣️ Roadmap

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
