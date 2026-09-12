可以。下面这套我按 **2026 年 9 月 6 日的 Codex 官方文档**来整理，并针对你这种 **macOS 本地开发 + Codex CLI + Docker 执行项目代码 + 以后可能接 Serena/MCP** 的用法给出实际配置。

先给你最终框架：

```text
Codex CLI
│
├── config.toml       ← Codex 本身怎么运行
│
├── AGENTS.md         ← 告诉 Codex “这个项目应该怎么干活”
│
├── .agents/skills/   ← 把复杂、重复的工作流程模块化
│
├── MCP               ← 给 Codex 增加外部工具/数据源
│
├── Rules             ← 控制哪些 shell 命令允许/禁止/询问
│
├── Hooks             ← 在工具执行前后做强制检查
│
└── Docker            ← 真正运行项目代码、测试、build 的隔离环境
```

对于你，我最终推荐的是：

> **Codex 原生 sandbox + AGENTS.md + Docker + 少量 Skills + 必要 MCP + Hook 强制 Docker**

而不是一开始装十几个 MCP。

---

# 1. 安装 Codex CLI

目前 macOS/Linux 官方首先推荐 standalone installer：

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

更新也是同一个命令：

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

然后：

```bash
codex
```

首次启动登录 ChatGPT 即可。官方当前 CLI 页面展示的示例已经是：

```text
OpenAI Codex

model:     gpt-5.6-sol medium
directory: ~/code
```

并直接推荐 `/init`、`/status`、`/permissions`、`/model`、`/review` 作为入门命令。([OpenAI Developers][1])

官方页面：

[Codex CLI 官方文档](https://developers.openai.com/codex/cli?utm_source=chatgpt.com)

---

# 2. 第一次进入项目

例如：

```bash
cd ~/projects/my-project

git status

codex
```

进入之后，第一批建议掌握的命令：

| 命令             | 用途                 |
| -------------- | ------------------ |
| `/model`       | 选择模型、reasoning     |
| `/permissions` | 修改当前权限             |
| `/status`      | 查看当前 sandbox、目录、配置 |
| `/init`        | 自动生成初始 `AGENTS.md` |
| `/plan`        | 先规划再修改             |
| `/review`      | Review 当前改动        |
| `/compact`     | 压缩长上下文             |
| `/mcp`         | 查看 MCP             |
| `/skills`      | 查看 Skills          |
| `/reasoning`   | 调整 reasoning       |
| `/fork`        | 从当前 session 分叉     |
| `/status`      | 出问题时首先检查这个         |

官方 Quickstart 也明确建议：**在交给 Codex 修改前后创建 Git checkpoint**。([OpenAI Developers][1])

所以我的日常模式是：

```text
git status
    ↓
codex
    ↓
/plan
    ↓
让 Codex 修改
    ↓
/review
    ↓
git diff
    ↓
测试
    ↓
commit
```

不要把 Codex 当成“自动写代码工具”。

更好的理解是：

> Codex 是一个拥有 terminal、文件编辑、搜索、MCP、Skills 等能力的 coding agent。

---

# 3. `config.toml` 是整个 Codex 的核心配置

用户级配置：

```text
~/.codex/config.toml
```

项目也可以：

```text
project/
└── .codex/
    └── config.toml
```

当前配置优先级是：

```text
CLI 参数
   ↓
项目 .codex/config.toml
   ↓
--profile 对应的 profile
   ↓
~/.codex/config.toml
   ↓
/etc/codex/config.toml
   ↓
Codex 默认值
```

而且只有 **trusted project** 才会加载项目自己的 `.codex/config.toml`、Hooks 和 Rules。([ChatGPT Learn][2])

---

# 4. 我推荐你的 `~/.codex/config.toml`

先不要做得太复杂。

### 第一阶段就用这个

```toml
# ~/.codex/config.toml

# -----------------------
# Model
# -----------------------

model = "gpt-5.6"

model_reasoning_effort = "high"

personality = "pragmatic"


# -----------------------
# Security
# -----------------------

approval_policy = "on-request"

sandbox_mode = "workspace-write"


# workspace-write 默认不开放 command 网络
[sandbox_workspace_write]
network_access = false


# -----------------------
# Web
# -----------------------

web_search = "cached"
```

官方目前基本配置示例也是：

```toml
model = "gpt-5.6"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
model_reasoning_effort = "high"
```

([ChatGPT Learn][2])

注意一个很容易混淆的地方：

**官方 config 教程目前用 `gpt-5.6` 作为通用示例，而当前 CLI 页面演示的是 `gpt-5.6-sol`。**

所以我建议：

```text
先运行：

/model
```

如果你的账户中已经出现：

```text
gpt-5.6-sol
```

再把：

```toml
model = "gpt-5.6-sol"
```

写死。

不要因为网上某篇教程写了模型名字，就直接塞进配置。

---

# 5. `workspace-write` 到底是什么意思？

这是一个非常重要的概念。

你的配置：

```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

意味着：

```text
项目目录内

读取文件       ✅
修改文件       ✅
执行命令       ✅
网络访问       ❌ 默认
工作区外写入   → 需要授权
需要额外权限   → 询问你
```

官方称这个组合为 **Auto preset**。`workspace-write` 默认关闭 command 网络，而且 `.git`、`.agents`、`.codex` 等部分路径还会保持保护状态。([ChatGPT Learn][3])

macOS 上 Codex 原生 sandbox 使用 OS sandbox 机制；Linux 当前主要使用 `bwrap + seccomp`。([ChatGPT Learn][3])

所以：

```text
Codex sandbox
≠
Docker
```

它们解决的问题不同。

---

# 6. 我为什么仍然推荐你使用 Docker？

因为你之前想要的是：

```text
Mac host
│
├── rg / grep / cat / git diff
│     ↓
│   可以直接执行
│
└── Python / Java / Go / Node
      测试
      build
      dependency install
      migration
      application
            ↓
          Docker
```

这个思路我仍然推荐。

也就是：

```text
                 ┌───────────────┐
                 │ Codex sandbox │
                 └───────┬───────┘
                         │
            ┌────────────┴────────────┐
            │                         │
         read/search              execution
            │                         │
         macOS                     Docker
                                      │
                              project runtime
```

**Codex sandbox 是第一层。**

**Docker 是项目代码执行的第二层。**

这比直接：

```bash
codex --yolo
```

安全得多。

官方也明确把：

```bash
--dangerously-bypass-approvals-and-sandbox
```

以及：

```bash
--yolo
```

定义为没有 sandbox、没有 approval 的危险全权限模式，不建议普通本地开发使用。([ChatGPT Learn][3])

---

# 7. Docker 怎么给 Codex 用？

我更推荐项目自己拥有：

```text
my-project/
├── Dockerfile.dev
├── compose.yaml
├── AGENTS.md
└── src/
```

然后 Codex 不运行：

```bash
pytest
npm test
go test ./...
./gradlew test
mvn test
```

而是运行：

```bash
docker compose run --rm app pytest
```

或者：

```bash
docker compose run --rm app npm test
```

或者：

```bash
docker compose run --rm app go test ./...
```

Java：

```bash
docker compose run --rm app ./gradlew test
```

这样 Codex 不需要知道你的 Mac 装了什么 Java、Python、Node、Go。

---

# 8. `AGENTS.md`：Codex 最值得认真配置的东西

如果只能学一个高级功能，我会让你先学：

> **AGENTS.md**

它不是 prompt 小技巧。

它相当于：

```text
项目的 AI 开发规范
```

官方加载顺序现在是：

```text
~/.codex/AGENTS.md
          ↓
repo/AGENTS.md
          ↓
repo/module/AGENTS.md
          ↓
repo/module/submodule/AGENTS.md
```

越靠近当前目录的规则优先级越高。

如果存在：

```text
AGENTS.override.md
```

则它会优先于同目录的 `AGENTS.md`。

默认所有加载的项目说明合计上限是 **32 KiB**。([OpenAI Developers][4])

---

# 9. 推荐你的全局 `AGENTS.md`

创建：

```bash
mkdir -p ~/.codex
```

然后：

```text
~/.codex/AGENTS.md
```

我建议写成这样：

```markdown
# Global Codex Instructions

## General approach

- Inspect the existing code before making changes.
- Prefer minimal, focused changes.
- Preserve the existing architecture unless there is a clear reason to change it.
- Do not introduce new dependencies unless necessary.
- Explain important architectural decisions briefly.

## Git safety

- Never run destructive Git commands unless explicitly requested.
- Never run `git reset --hard`.
- Never force push.
- Do not commit or push unless explicitly requested.
- Always inspect `git diff` after making changes.

## Host command policy

Read-only inspection commands may run directly on the host.

Examples:

- pwd
- ls
- find
- rg
- grep
- cat
- head
- tail
- git status
- git diff
- git log
- git show

Commands that execute project code, install dependencies, build artifacts,
run tests, start services, execute migrations, or modify runtime state
must run inside Docker.

Examples that MUST NOT run directly on the host:

- npm / pnpm / yarn scripts
- node
- python
- pytest
- pip install
- uv run
- go test
- go run
- cargo test
- cargo run
- java
- javac
- mvn
- gradle
- ./gradlew
- dotnet test
- application binaries

Prefer:

docker compose run --rm <service> <command>

or:

docker run --rm ... <command>

## Testing

After changing code:

1. Determine the smallest relevant test set.
2. Run those tests inside Docker.
3. Run broader tests only when necessary.
4. Report exactly what was tested.

## Security

- Never print secrets.
- Never read `.env` unless required for the task.
- Never send project data to external services without explicit need.
- Never mount the Docker socket inside project containers.
```

这已经能够让 Codex 的行为稳定很多。

---

# 10. 全局 AGENTS 和项目 AGENTS 怎么分？

这是一个关键设计。

### `~/.codex/AGENTS.md`

只放：

```text
你的个人开发习惯
安全原则
Docker 原则
Git 原则
回答习惯
```

### `project/AGENTS.md`

放：

```text
这个项目是什么
目录结构
架构
build/test
编码规范
数据库规则
API规则
```

例如：

```markdown
# Project Instructions

## Architecture

This repository contains:

- `backend/`: Spring Boot REST API
- `frontend/`: React frontend
- `db/`: database migrations
- `docs/`: architecture documentation

## Backend

Java 25 with Gradle.

Run backend tests with:

docker compose run --rm backend ./gradlew test

## Frontend

Run frontend tests with:

docker compose run --rm frontend pnpm test

## Database

Never apply migrations directly to production.

Local migrations must run through:

docker compose run --rm backend ./gradlew flywayMigrate

## Code style

- Follow existing conventions.
- Prefer small methods.
- Do not introduce unnecessary abstraction.
- Maintain backwards compatibility for public APIs.

## Definition of done

Before considering a task complete:

- relevant tests pass
- lint passes
- git diff has been reviewed
- no unrelated files were changed
```

这就是我认为 Codex 项目里最实用的配置。

---

# 11. 怎么确认 AGENTS.md 真被读取了？

官方直接提供了一个很好用的方法：

```bash
codex --ask-for-approval never \
  "Summarize the current instructions."
```

还可以：

```bash
codex --cd backend \
  --ask-for-approval never \
  "Show which instruction files are active."
```

([OpenAI Developers][4])

我非常建议第一次配置完就执行一次。

---

# 12. `config.toml` 和 `AGENTS.md` 千万不要混

简单记住：

| 内容            | 放哪里           |
| ------------- | ------------- |
| 默认模型          | `config.toml` |
| reasoning     | `config.toml` |
| sandbox       | `config.toml` |
| approval      | `config.toml` |
| MCP           | `config.toml` |
| 项目结构          | `AGENTS.md`   |
| 测试方式          | `AGENTS.md`   |
| Docker 开发规则   | `AGENTS.md`   |
| coding style  | `AGENTS.md`   |
| Git 行为原则      | `AGENTS.md`   |
| 可复用工作流        | Skill         |
| 外部工具          | MCP           |
| 强制阻止 shell 命令 | Hook / Rule   |

这是整个 Codex 配置体系最重要的心智模型。

---

# 13. Skills 到底是什么？

Skills 适合：

> **重复、复杂、具有固定流程的任务。**

例如你经常做：

```text
修 bug
→ 找相关代码
→ 找测试
→ Docker 跑测试
→ 修改
→ 再测试
→ review diff
```

就可以变成：

```text
docker-fix
```

Skill。

当前 Codex Skill 的目录结构是：

```text
my-skill/
├── SKILL.md
├── scripts/       # optional
├── references/    # optional
├── assets/        # optional
└── agents/
    └── openai.yaml
```

其中只有：

```text
SKILL.md
```

必需，而且必须包含：

```yaml
name:
description:
```

Codex 首先只加载 Skill 的名字和 description，真正选中后再加载完整 `SKILL.md`，这是官方所谓的 progressive disclosure。([OpenAI Developers][5])

---

# 14. Skill 放在哪里？

项目级：

```text
project/.agents/skills/
```

个人全局：

```text
~/.agents/skills/
```

系统：

```text
/etc/codex/skills/
```

官方会从当前目录一直向 repo root 查找 `.agents/skills`。([OpenAI Developers][5])

所以你的项目最终可以变成：

```text
my-project/
│
├── AGENTS.md
│
├── .codex/
│   └── config.toml
│
├── .agents/
│   └── skills/
│       ├── docker-test/
│       │   └── SKILL.md
│       │
│       ├── fix-bug/
│       │   └── SKILL.md
│       │
│       └── code-review/
│           └── SKILL.md
│
├── Dockerfile.dev
├── compose.yaml
└── src/
```

---

# 15. 给你一个真正有用的 Skill

例如：

```text
.agents/skills/docker-test/SKILL.md
```

内容：

```markdown
---
name: docker-test
description: Run project tests, builds, dependency commands, or application code safely using Docker. Use whenever project code needs to execute.
---

# Docker project execution

Never execute project runtimes directly on the host.

Determine the appropriate Docker service from compose.yaml.

Prefer:

docker compose run --rm <service> <command>

For tests:

1. Identify the smallest relevant test scope.
2. Run targeted tests first.
3. If they succeed, run the broader suite when appropriate.
4. Report the exact command and result.

Do not:

- mount /var/run/docker.sock into project containers
- copy host secrets into containers
- run destructive Docker cleanup commands
```

之后在 Codex 里可以显式调用：

```text
$docker-test
```

或者：

```text
Use $docker-test and run the backend tests.
```

Codex 也可以根据 `description` 自动选择 Skill。官方同时提供：

```text
$skill-creator
```

帮助你生成 Skill。([OpenAI Developers][5])

---

# 16. AGENTS.md 和 Skill 有什么区别？

这是很多人最容易弄错的地方。

```text
AGENTS.md
    =
永远应该遵守的规则
```

例如：

```text
测试必须 Docker
禁止 git reset --hard
数据库 migration 规则
项目架构
```

而：

```text
Skill
    =
“做某类事情时”采用的工作流程
```

例如：

```text
修 GitHub CI
release
升级 Gradle
生成 migration
code review
处理 Oracle APEX
```

所以：

**Docker 必须执行这个原则不能只写 Skill。**

至少应该在：

```text
AGENTS.md
```

里存在。

---

# 17. MCP 是干什么的？

MCP 的定位完全不同：

```text
AGENTS
  ↓
告诉 Codex 怎么做

Skills
  ↓
告诉 Codex 某件事怎么做

MCP
  ↓
给 Codex 新工具
```

比如：

```text
Context7
→ 查询第三方库最新文档

Serena
→ symbol/code intelligence

Database MCP
→ 查询数据库

GitHub MCP
→ issue/PR

Browser MCP
→ 浏览器
```

Codex 当前支持 MCP 的：

```text
STDIO
Streamable HTTP
OAuth
Bearer token
```

等模式。([OpenAI Developers][6])

---

# 18. MCP 最简单的添加方式

官方当前 Context7 示例：

```bash
codex mcp add context7 -- npx -y @upstash/context7-mcp
```

检查：

```bash
codex mcp list
```

帮助：

```bash
codex mcp --help
```

OAuth MCP：

```bash
codex mcp login <server-name>
```

([OpenAI Developers][6])

也可以直接配置：

```toml
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]
```

---

# 19. MCP 还能限制工具

这是现在比较值得用的功能。

例如一个 MCP 有：

```text
read
search
delete
write
execute
```

你未必都想开放。

现在可以：

```toml
[mcp_servers.example]
enabled = true

enabled_tools = [
    "read",
    "search"
]
```

甚至：

```toml
disabled_tools = [
    "delete"
]
```

还支持：

```toml
default_tools_approval_mode = "prompt"
```

以及 per-tool approval。([OpenAI Developers][6])

这个比以前 MCP 一接进来所有 tools 全暴露，要成熟很多。

---

# 20. 那 Serena 还有没有必要？

针对你的情况，我会这样排优先级：

```text
Codex 原生
    ↓
rg / find / git
    ↓
AGENTS.md
    ↓
Skills
    ↓
Context7
    ↓
必要时才 Serena
```

不是：

```text
Codex
↓
先装 Serena
↓
再装十几个 MCP
```

对于普通：

```text
10k
50k
100k lines
```

级别项目，我会先观察 Codex 原生搜索是否够用。

但大型：

```text
Java monorepo
Go monorepo
Python 大型 package
```

如果你经常需要：

```text
find symbol
find references
类继承
接口 implementation
symbol rename
跨模块 dependency
```

那么 **Serena/LSP 类型 MCP 依然有价值**。

不过它应该是：

> **代码导航增强层**

而不是 Codex 能理解代码的前提。

---

# 21. MCP 不要装太多

这是我的推荐，不是官方硬限制。

我会控制在：

```text
2～5 个真正有价值的 MCP
```

例如你的环境，我可能只配：

```text
Context7
Serena
GitHub（需要时）
Database MCP（需要时）
```

原因很简单：

```text
MCP 越多
    ↓
tool catalog 越大
    ↓
模型要判断的工具越多
    ↓
启动/上下文/误调用成本增加
```

Skills 通常比“为了所有事情安装 MCP”更轻量。

---

# 22. Rules：控制 shell 命令

现在 Codex 还有一层：

```text
~/.codex/rules/
```

例如：

```text
~/.codex/rules/default.rules
```

Rules 可以定义：

```text
allow
prompt
forbidden
```

并通过：

```text
prefix_rule()
```

匹配命令前缀。

多个 rule 同时匹配时，最严格的决定优先：

```text
forbidden
>
prompt
>
allow
```

([ChatGPT Learn][7])

所以可以用于类似：

```text
git status
→ allow

docker
→ prompt

rm
→ forbidden
```

这种策略。

---

# 23. 但是你的 Docker-only 规则最好用 Hook

这是我尤其推荐给你的进阶配置。

因为：

```text
AGENTS.md
```

本质上是 **给模型的指令**。

它不是严格 security boundary。

如果你的真正要求是：

> 除了读取代码，项目程序绝对不能直接在 Mac 上运行。

那可以增加：

```text
PreToolUse Hook
```

Hook 会在 Bash 工具真正执行前被调用，而且可以 **直接阻止调用**。官方明确支持 `PreToolUse` 检查 Bash、`apply_patch`、MCP 和其他本地 tools；返回 deny 或 exit code 2 可以阻止执行。([ChatGPT Learn][8])

这就变成：

```text
Codex 想执行 pytest
       ↓
PreToolUse
       ↓
docker command?
   ↙          ↘
 yes          no
 ↓             ↓
允许          拒绝
```

---

# 24. 我给你一个 Docker Guard Hook

创建：

```text
~/.codex/hooks/docker_guard.py
```

```python
#!/usr/bin/env python3

import json
import re
import sys


data = json.load(sys.stdin)

if data.get("tool_name") != "Bash":
    sys.exit(0)

tool_input = data.get("tool_input") or {}
command = tool_input.get("command", "")

if not isinstance(command, str):
    print("Unsupported Bash command format.", file=sys.stderr)
    sys.exit(2)

command = command.strip()


# Docker execution is allowed.
if re.match(r"^(docker|docker-compose)\b", command):
    sys.exit(0)


# Read-only commands allowed directly on host.
safe_patterns = [
    r"^pwd(?:\s.*)?$",
    r"^ls(?:\s.*)?$",
    r"^find(?:\s.*)?$",
    r"^rg(?:\s.*)?$",
    r"^grep(?:\s.*)?$",
    r"^cat(?:\s.*)?$",
    r"^head(?:\s.*)?$",
    r"^tail(?:\s.*)?$",
    r"^wc(?:\s.*)?$",
    r"^file(?:\s.*)?$",
    r"^stat(?:\s.*)?$",

    r"^git\s+status(?:\s.*)?$",
    r"^git\s+diff(?:\s.*)?$",
    r"^git\s+log(?:\s.*)?$",
    r"^git\s+show(?:\s.*)?$",
    r"^git\s+rev-parse(?:\s.*)?$",
]

for pattern in safe_patterns:
    if re.match(pattern, command):
        sys.exit(0)


print(
    "Direct host command blocked. "
    "Run project execution through Docker instead.",
    file=sys.stderr,
)

sys.exit(2)
```

然后启用 Hook。

在：

```toml
~/.codex/config.toml
```

加入：

```toml
[features]
hooks = true

[[hooks.PreToolUse]]
matcher = "^Bash$"

[[hooks.PreToolUse.hooks]]
type = "command"
command = "python3 ~/.codex/hooks/docker_guard.py"
timeout = 5
```

官方 Hook 本身也明确提醒：它是一层很好用的 **guardrail，但不能视为完整安全边界**。所以仍然保留 Codex sandbox。([ChatGPT Learn][8])

这套对于你的需求特别合适。

---

# 25. 最终就形成了三层防护

```text
                    Codex
                      │
                      ▼
              ┌──────────────┐
              │  AGENTS.md   │
              │  行为规范     │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Hook / Rules │
              │ 强制检查命令  │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Codex sandbox│
              │ workspace    │
              └──────┬───────┘
                     │
           ┌─────────┴─────────┐
           ▼                   ▼
       read-only            execution
         host                   │
                                ▼
                             Docker
```

我认为这比你之前考虑做一个复杂的“大型 agent sandbox 平台”更合理。

---

# 26. `codex exec`：从交互式进入自动化

平时：

```bash
codex
```

是 interactive。

而：

```bash
codex exec "..."
```

适合：

```text
shell script
CI
cron
自动 review
batch task
```

例如：

```bash
codex exec \
  --sandbox read-only \
  --ask-for-approval never \
  "Review this repository and report possible bugs."
```

这个非常安全：

```text
read-only
+
never approval
```

等于：

> 允许它读，但是既不能写，也不会跳出来向你要求扩大权限。

---

# 27. 自动修复可以这样

```bash
codex exec \
  --sandbox workspace-write \
  --ask-for-approval never \
  "Fix the failing tests. Follow AGENTS.md."
```

这时：

```text
workspace-write
```

允许修改项目。

但：

```text
approval = never
```

意味着它不能为了完成任务自己要求更高权限。

官方现在也建议 non-interactive 工作使用：

```bash
codex exec --sandbox workspace-write
```

旧的：

```bash
codex exec --full-auto
```

已作为兼容路径保留，但官方现在标记为 deprecated。([ChatGPT Learn][3])

---

# 28. `codex exec` 高级用法

机器消费结果：

```bash
codex exec --json \
  "Review the changes"
```

保存最后回答：

```bash
codex exec \
  --output-last-message result.txt \
  "Analyze the repository"
```

结构化输出还可以使用：

```text
--output-schema
```

这意味着你以后可以做：

```text
GitHub Action
      ↓
codex exec
      ↓
JSON
      ↓
程序解析
      ↓
自动 Review
```

---

# 29. Profile 很值得使用

不要经常修改：

```text
config.toml
```

例如可以有：

```text
~/.codex/config.toml

~/.codex/deep.config.toml

~/.codex/readonly.config.toml
```

默认：

```bash
codex
```

深入复杂任务：

```bash
codex --profile deep
```

只读分析：

```bash
codex --profile readonly
```

例如：

### `~/.codex/readonly.config.toml`

```toml
model = "gpt-5.6"

model_reasoning_effort = "high"

approval_policy = "never"

sandbox_mode = "read-only"
```

然后：

```bash
codex --profile readonly
```

非常适合：

```text
解释代码
架构分析
安全 review
找 bug
```

---

# 30. 我的模型选择建议

你目前可以简单使用：

| 工作        |    Reasoning |
| --------- | -----------: |
| 小改动       |       medium |
| 普通 coding |         high |
| debug     |         high |
| 架构分析      |         high |
| 大型重构      | high / xhigh |
| 复杂跨模块问题   |        xhigh |

`xhigh` 是否可用取决于模型。官方 config reference 当前支持到 `xhigh`，但不是所有模型都支持。

所以我通常不会天天固定 xhigh。

我的默认：

```toml
model_reasoning_effort = "high"
```

足够。

遇到特别难的问题再：

```text
/reasoning
```

提升。

---

# 31. 一个很有效的 Codex Prompt Pattern

不要这样：

```text
fix this project
```

也不要：

```text
看看有什么问题，全修了
```

推荐：

```text
First inspect the repository and identify the cause of issue X.

Do not modify anything yet.

Explain:
1. root cause
2. affected files
3. proposed change
4. tests that should be run
```

确认后：

```text
Implement the proposed solution.

Keep the change minimal.
Do not modify unrelated files.
Run the relevant tests according to AGENTS.md.
Finally review the diff and summarize what changed.
```

对于大型任务则先：

```text
/plan
```

然后再实施。

---

# 32. Review 是 Codex 很值得利用的能力

修改之后不要只问：

```text
done?
```

直接：

```text
/review
```

或者：

```text
Review the current diff.

Focus on:
- correctness
- regressions
- edge cases
- security
- unnecessary complexity
- missing tests

Do not edit files.
```

然后自己：

```bash
git diff
```

最终形成：

```text
Agent 写
↓
Agent review
↓
你 review
↓
Docker tests
```

这比让一个 agent 一口气“写完就算了”可靠得多。

---

# 33. `codex resume` 很有用

之前的 session 可以继续：

```bash
codex resume
```

因此一个复杂项目不需要每次重新说明：

```text
昨天为什么这样设计
我们讨论过什么
哪些方案被排除
```

尤其长期 bug / refactoring，很方便。

---

# 34. 一个我推荐的真实项目目录

最终我会把你的项目整理成这样：

```text
my-project/
│
├── AGENTS.md
│
├── README.md
│
├── compose.yaml
│
├── Dockerfile.dev
│
├── src/
│
├── tests/
│
│
├── .codex/
│   ├── config.toml
│   ├── rules/
│   │   └── default.rules
│   └── hooks/
│       └── ...
│
└── .agents/
    └── skills/
        ├── docker-test/
        │   └── SKILL.md
        ├── bug-fix/
        │   └── SKILL.md
        └── code-review/
            └── SKILL.md
```

而你的 Home：

```text
~/.codex/
│
├── config.toml
├── AGENTS.md
├── readonly.config.toml
├── deep.config.toml
│
├── hooks/
│   └── docker_guard.py
│
└── rules/
    └── default.rules
```

这已经属于比较完整、但又没有过度工程化的 Codex 配置。

---

# 35. 我建议你的实际技术栈

如果现在让我直接替你选择，我会用：

```text
Codex CLI
│
├── gpt-5.6 / gpt-5.6-sol
│
├── reasoning = high
│
├── workspace-write
│
├── approval = on-request
│
├── AGENTS.md
│
├── Docker
│
├── Docker Guard Hook
│
├── Context7 MCP
│
├── Serena MCP
│     └─ 只在大型项目需要 symbol intelligence 时
│
└── Skills
      ├── docker-test
      ├── bug-fix
      └── code-review
```

**我不会默认使用 `--yolo`。**

**我不会装一大堆 MCP。**

**我不会把所有东西塞进一个 2000 行 AGENTS.md。**

**我也不会把 Codex 本身全部塞进 Docker。**

Codex CLI 留在 Mac 上，让它方便读取、编辑代码；**项目代码的实际执行进入 Docker**。这与 Codex 自带 sandbox 叠加，我认为是你目前最平衡的方案。

---

# 36. 最值得记住的 10 个命令

```bash
# 打开
codex

# 指定目录
codex -C ~/project

# 恢复 session
codex resume

# 查看配置
/status

# 修改权限
/permissions

# 模型
/model

# 规划
/plan

# Review
/review

# MCP
codex mcp list

# 非交互执行
codex exec "..."
```

再加：

```bash
codex --help

codex mcp --help

codex --version
```

基本就够日常用了。

---

# 37. 学习顺序，我建议不要乱

```text
Level 1
Codex CLI
    ↓
/model
/permissions
/status

Level 2
AGENTS.md
    ↓
让 Codex 稳定遵守项目规范

Level 3
workspace-write + approvals
    ↓
理解权限

Level 4
Docker
    ↓
隔离项目执行

Level 5
Skills
    ↓
标准化重复工作流

Level 6
MCP
    ↓
增加真正缺少的工具能力

Level 7
Rules + Hooks
    ↓
把“建议”升级成“强制策略”

Level 8
codex exec
    ↓
CI / automation
```

按照这个顺序学，Codex 会非常清晰，而不会变成：

> MCP + prompt + plugin + sandbox + rule + skill 全部混在一起。

---

## 给你一个最重要的最终结论

如果是**你现在这台 Mac 上开始配置**，我建议第一版只做四件事：

```text
① ~/.codex/config.toml
② ~/.codex/AGENTS.md
③ 每个项目自己的 AGENTS.md
④ Docker 执行 project commands
```

用一两周后再加入：

```text
⑤ Context7
⑥ Serena
⑦ Skills
⑧ Docker Guard Hook
```

这样你能清楚知道**哪一个组件到底给 Codex 带来了什么提升**，不会一开始把系统搞得很复杂。

尤其你原来那个“**纯读取可以 Mac 直接执行，其余项目 runtime/test/build 全部 Docker**”的方案，我现在反而觉得非常适合 Codex CLI：**Codex 自带 sandbox 管文件权限，Docker 管执行环境，AGENTS 管行为，Hook 最后兜底。** ([ChatGPT Learn][3])

官方资料我主要以这几个当前页面为准：[Codex CLI](https://developers.openai.com/codex/cli?utm_source=chatgpt.com) · [AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md?utm_source=chatgpt.com) · [MCP](https://developers.openai.com/codex/extend/mcp?utm_source=chatgpt.com) · [Skills](https://developers.openai.com/codex/build-skills?utm_source=chatgpt.com)。

[1]: https://developers.openai.com/codex/cli "Codex CLI | ChatGPT Learn"
[2]: https://learn.chatgpt.com/codex/config-file/config-basic "Config basics | ChatGPT Learn"
[3]: https://learn.chatgpt.com/codex/agent-approvals-security "Agent approvals & security | ChatGPT Learn"
[4]: https://developers.openai.com/codex/agent-configuration/agents-md "Custom instructions with AGENTS.md | ChatGPT Learn"
[5]: https://developers.openai.com/codex/build-skills "Build skills | ChatGPT Learn"
[6]: https://developers.openai.com/codex/extend/mcp "Model Context Protocol | ChatGPT Learn"
[7]: https://learn.chatgpt.com/codex/agent-configuration/rules "Rules | ChatGPT Learn"
[8]: https://learn.chatgpt.com/codex/hooks "Hooks | ChatGPT Learn"
