<p align="center">
  <img src="https://img.shields.io/pypi/v/skillforge-mcp?style=for-the-badge&logo=pypi&logoColor=white&label=PyPI" alt="PyPI"/>
  <img src="https://img.shields.io/badge/MCP-Server-blueviolet?style=for-the-badge" alt="MCP Server"/>
  <img src="https://img.shields.io/badge/python-≥3.10-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/github/stars/CatVinci-Studio/skillForge?style=for-the-badge&logo=github" alt="Stars"/>
</p>

<h1 align="center">🛠️ SkillForge</h1>

<p align="center">
  <strong>一个让你的 AI 智能体学习与进化的 MCP 服务器 —— 每次一个技能。</strong>
</p>

<p align="center">
  <em>技能是可复用的指令，随着每次对话不断优化。</em>
</p>

<p align="center">
  <a href="README.md">🇬🇧 English</a> · <a href="https://pypi.org/project/skillforge-mcp/">📦 PyPI</a> · <a href="https://github.com/CatVinci-Studio/skillForge/issues">🐛 问题反馈</a>
</p>

---

## ✨ SkillForge 是什么？

SkillForge 是一个 **模型上下文协议（MCP）服务器**，为你的 AI 智能体提供一个持久化、可进化的技能库。不再需要每次对话都重复相同的纠正和偏好设置——SkillForge 会把它们捕获为 **技能（Skills）**，让智能体自动加载并遵循这些结构化指令。

> 💡 把它想象成 **AI 的肌肉记忆** —— 学一次你的习惯，永远自动应用。

### 🔄 反馈循环

```
  👤 用户给出反馈
        │
        ▼
  🔍 智能体检测到改进信号
        │
        ▼
  🔀 分流：复用 / 改进 / 新建？
        │
        ▼
  ✏️ 按照指南和计划起草技能
        │
        ▼
  🛡️ 验证门控（拒绝或通过）
        │
        ▼
  💾 技能保存（自动备份）
        │
        ▼
  ✅ 下次任务使用改进后的技能
```

---

## 🚀 快速开始

### 📦 安装

```bash
# 从 PyPI 安装（推荐）
pip install skillforge-mcp

# 或使用 uv
uv pip install skillforge-mcp
```

### ⚡ 启动服务器

```bash
# 直接运行
skillforge

# 或通过 uvx 免安装运行
uvx skillforge-mcp
```

### 🔌 连接到 Claude Code

在 MCP 配置中添加：

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
<summary>💡 备选方案：从源码安装</summary>

```bash
git clone https://github.com/CatVinci-Studio/skillForge.git
cd skillForge
pip install -e .
```

</details>

---

## 🧩 架构

```
src/skillforge/
├── 🏠 server.py              # MCP 服务器定义与提示词
├── 📨 response.py            # 响应格式化与反馈监听器
├── 🛡️ validator.py           # 技能质量硬性验证门控
├── 📁 skill_manager.py       # 核心 CRUD、备份、恢复逻辑
├── 🔧 tools/
│   ├── 🔍 discovery.py       # list_skills, get_skill
│   ├── ✏️  crud.py            # save_skill（含验证）, delete_skill
│   ├── 💾 backup.py          # list_backups, restore_skill
│   ├── 🔀 triage.py          # triage_skill_request
│   └── 🧠 optimization.py    # get_skill_guide, request_skill_optimization
└── 📖 guide/
    └── skill_writing_guide.md # 技能编写最佳实践
```

### 📂 运行时数据

SkillForge 将数据存储在 `~/.skillforge/`：

| 目录 | 用途 |
|------|------|
| `~/.skillforge/skills/` | 📚 活跃技能库 |
| `~/.skillforge/backups/` | 🗄️ 自动版本历史 |

> 🔒 可通过 `SKILLFORGE_SKILLS_DIR` 和 `SKILLFORGE_BACKUP_DIR` 环境变量覆盖。

---

## 🔧 可用工具

| 工具 | 说明 |
|------|------|
| 🔍 `list_skills` | 列出所有技能 —— **任务开始前的必要调用** |
| 📖 `get_skill` | 按名称加载完整技能指令 |
| 🔀 `triage_skill_request` | 创建/改进前检查已有技能 —— 防止重复 |
| 🧠 `request_skill_optimization` | 获取技能改进的结构化计划 |
| 📖 `get_skill_guide` | 加载技能编写最佳实践指南 |
| ✏️ `save_skill` | 创建或更新技能 —— **自动验证，质量不达标则拒绝** |
| 🗑️ `delete_skill` | 删除技能（两步确认，自动备份） |
| 📋 `list_backups` | 查看技能的版本历史 |
| ⏪ `restore_skill` | 回滚到之前的版本 |
| 📊 `get_optimization_history` | 查看驱动技能变更的反馈日志 |

---

## 🛡️ 质量门控（v0.2.0）

不同于依赖 LLM 自觉遵守的提示词质量控制，SkillForge 通过 `save_skill` 中的 **硬性验证门控** 强制保障质量：

| 检查项 | 类型 | 规则 |
|--------|------|------|
| 📏 描述长度 | ❌ 错误 | 必须 ≥ 50 字符 |
| 📏 正文长度 | ❌ 错误 | 必须为 3–500 行 |
| 🔄 描述 ≠ 名称 | ❌ 错误 | 描述必须解释功能，而非重复名称 |
| 🎯 触发条件 | ⚠️ 警告 | 应包含"当.../每当.../使用此技能当..." |
| 🗣️ 过于僵硬的语言 | ⚠️ 警告 | 推荐用推理解释取代"必须始终"等强制措辞 |
| 📐 描述过长 | ⚠️ 警告 | 保持 1000 字符以内，详情放入正文 |

> 🔴 **错误** 会阻止保存 —— 修复后重试。
> 🟡 **警告** 允许保存，但标记待改进项。

### 🔀 技能分流

在创建新技能前，`triage_skill_request` 返回所有已有技能，供 LLM 判断：

| 决策 | 条件 | 操作 |
|------|------|------|
| **复用** | 已有技能完全覆盖需求 | 用 `get_skill` 加载 |
| **改进** | 已有技能部分覆盖 | 用 `request_skill_optimization` 优化 |
| **新建** | 没有相关技能 | 通过 `request_skill_optimization` 创建 |

---

## 📝 技能格式

每个技能以 `SKILL.md` 文件的形式存放在独立目录中，使用 YAML 前置元数据：

```yaml
---
name: my-skill
description: >
  这个技能做什么，以及何时触发。
  当用户要求...时使用此技能。
  即使用户没有明确要求...也应激活。
---

# 技能指令

你的 Markdown 指令内容...
```

### 🏷️ 前置元数据字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 标识符（`小写-连字符`，最长 64 字符） |
| `description` | ✅ | 触发条件 —— 做什么 + 何时使用（≥ 50 字符） |
| `disable-model-invocation` | ❌ | `true` = 仅用户可调用 |
| `user-invocable` | ❌ | `false` = 仅 LLM 可调用 |
| `allowed-tools` | ❌ | 允许免审批使用的工具 |
| `context` | ❌ | `fork` = 在隔离子代理中运行 |

---

## 🧠 优化机制

SkillForge 持续监控对话中的改进信号：

| 信号 | 示例 | 操作 |
|------|------|------|
| 🔴 **纠正** | "不要 mock 数据库" | 更新相关技能 |
| 🟡 **偏好** | "始终使用 snake_case" | 创建或更新技能 |
| 🔵 **模式** | 相同结构使用 3 次以上 | 打包为新技能 |
| 🟢 **显式请求** | "把这个加到 review 技能里" | 直接编辑技能 |

### 🔒 安全保障

- ✅ 每次保存和删除前 **自动备份**
- ✅ 从任意备份时间戳 **一键恢复**
- ✅ 所有文件操作均有 **路径遍历防护**
- ✅ 优化日志使用文件锁 **原子写入**
- ✅ **硬性验证门控** —— 质量在工具边界强制执行，而非依赖提示词

---

## 🌟 为什么选择 SkillForge？

| 没有 SkillForge | 有 SkillForge |
|-----------------|---------------|
| 😤 每次对话重复同样的纠正 | 🧠 智能体自动记住并应用 |
| 📋 规范散落在各处文档中 | 📦 每个主题一个权威来源 |
| 🎲 智能体行为不一致 | ✅ 确定性的、技能驱动的响应 |
| 🔄 无法从反馈中学习 | 📈 技能随每次交互进化 |
| 🤞 指望 LLM 遵守质量规范 | 🛡️ 硬性验证拒绝低质量技能 |

---

## 🛣️ 路线图

- [x] 🛡️ 技能质量硬性验证门控
- [x] 🔀 技能分流防止重复
- [ ] 🌐 从远程仓库共享和导入技能
- [ ] 📊 技能使用与效果分析面板
- [ ] 🔗 跨技能依赖管理
- [ ] 🧪 技能测试框架与评估工具
- [ ] 🏪 社区技能市场

---

## 🤝 参与贡献

欢迎贡献！请随时提交 Pull Request。

---

## 📄 许可证

本项目基于 MIT 许可证开源 —— 详见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  <strong>由 <a href="https://github.com/CatVinci-Studio">CatVinci Studio</a> 用 ❤️ 打造</strong>
</p>

<p align="center">
  <em>锻造更好的 AI，每次一个技能。🔨</em>
</p>
