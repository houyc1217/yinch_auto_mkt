<p align="center">
  <img src="./assets/readme-banner.svg" alt="Yinch Auto MKT banner" width="100%" />
</p>

<p align="center">
  <strong>Yincheng 工作内容的沉淀框架，面向 Claude Code 和 Codex 复用成熟工作流</strong><br />
  同事只复制一句话完成安装，后面直接复用已经打磨过的工作流。
</p>

<p align="center">
  <a href="./README.en.md"><img src="https://img.shields.io/badge/English-README-1f6feb?style=flat-square" alt="English README"></a>
</p>

<p align="center">
  <a href="https://github.com/houyc1217/yinch_auto_mkt/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-0f172a?style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/badge/Claude%20Code-ready-0ea5e9?style=flat-square" alt="Claude Code Ready">
  <img src="https://img.shields.io/badge/Codex-ready-2563eb?style=flat-square" alt="Codex Ready">
  <img src="https://img.shields.io/badge/workflows-5-14b8a6?style=flat-square" alt="Workflows">
  <img src="https://img.shields.io/badge/output-JSON%20%2B%20XLSX-f59e0b?style=flat-square" alt="Output">
</p>

<p align="center">
  <a href="#一句话安装">一句话安装</a> ·
  <a href="#能直接做什么">能直接做什么</a> ·
  <a href="#架构理念">架构理念</a> ·
  <a href="#手动命令">手动命令</a>
</p>

## 一句话安装

把下面这句话直接复制给 Claude Code 或 Codex：

```text
请安装 Yinch Auto MKT：https://raw.githubusercontent.com/houyc1217/yinch_auto_mkt/main/install.sh 。把 Yinch Auto MKT 安装到你默认的全局目录里并自动修复环境：如果你是 Claude Code，就配置 ~/.claude/skills 和可选 ~/.claude/agents；如果你是 Codex，就配置 ${CODEX_HOME:-~/.codex}/skills；完成后帮我做一次 health check。
```

> [!TIP]
> 用户装完后，只需要正常提需求即可，不需要再关心 skill 目录、plugin 结构或环境问题。

## 能直接做什么

| Workflow | 作用 | 最终产物 |
| --- | --- | --- |
| `x-kol` | 研究 X/Twitter KOL，严格筛选内容并保留中间数据 | JSON 中间文件 + XLSX |
| `linkedin-post` | 先生成可审阅草稿，再在确认后用有头浏览器发布 | Markdown 草稿 + JSON 包 |
| `google-review` | 抓 Google Maps 公开评论，生成截图或 fallback review card | 图片素材 + Markdown/JSON 包 |
| `channel-setup` | 准备 Telegram 通知和 X/Instagram 发布所需的非敏感配置 | setup checklist + env template |
| `agent-install` | 修复或重装整套 Yinch Auto MKT 集成 | 可用的默认安装目录 |

## 为什么这个 repo 存在

它不是单个脚本，也不是某个 agent 专用的老式插件包。

它的定位更明确一些：

它是 **Yincheng 工作内容的沉淀框架**，让团队同事可以基于 Claude Code / Codex，快速完整复用已经成熟的工作流。

它更像一个面向 coding agent 的安装层和工作流分发层：

| 面向谁 | 解决什么问题 |
| --- | --- |
| 用户 / 同事 | 只复制一句话，之后直接复用成熟工作流 |
| Agent | 自动把能力安装到自己的默认目录，处理 skill / command / agent / runtime 的衔接 |
| Workflow | 把 Yincheng 已验证过的方法沉淀成可追溯、可复跑、可交付的流程 |

## 架构理念

这个项目把复杂度拆成三层：

### 1. 安装层

- `install.sh`
- `update.sh`
- `scripts/check-env.sh`

负责解决“能不能装、装到哪里、环境通不通”。

### 2. Agent 适配层

| Agent | 默认模式 |
| --- | --- |
| Claude Code | `~/.claude/skills` + 可选 `~/.claude/agents` |
| Codex | `${CODEX_HOME:-~/.codex}/skills` + 仓库内 `AGENTS.md` |

目标是兼容两种 coding agent 刚安装完成时最自然的默认入口。

这里采用的是 `skill-first` 设计：

- 对 Claude Code，主入口是 `skills`
- `agents` 只作为角色层补充
- 不再把 `commands` 作为主架构的一部分

### 3. 业务工作流层

- `x-kol`
- `linkedin-post`
- `google-review`
- `channel-setup`
- `agent-install`

目标不是堆说明文档，而是把复杂工作流封装成 agent 可以稳定调用的能力。

### 运行时自修复

- 首次执行业务 workflow 时，再按需创建本地 venv
- 再按需安装 Python 包和 Playwright
- 登录态只在运行时复用，不写进仓库和输出物

## 默认兼容方式

```text
Claude Code
  ~/.claude/skills
  ~/.claude/agents

Codex
  ${CODEX_HOME:-~/.codex}/skills
  AGENTS.md
```

## 安装后怎么用

安装完成后，用户直接自然语言使用即可。Claude Code 和 Codex 都以已安装的 `skills` 作为主入口。

## Repo 结构

```text
yinch-auto-mkt/
├── AGENTS.md
├── .claude/
│   ├── agents/
├── assets/
│   └── readme-banner.svg
├── skills/
│   ├── agent-install/
│   ├── channel-setup/
│   ├── google-review/
│   ├── linkedin-post/
│   └── x-kol/
├── scripts/
│   ├── check-env.sh
│   ├── install-agent-assets.sh
│   └── install-deps.sh
├── install.sh
└── update.sh
```

## 手动命令

如果不是通过自然语言交给 agent，也可以直接运行：

```bash
curl -fsSL https://raw.githubusercontent.com/houyc1217/yinch_auto_mkt/main/install.sh | bash
```

更新：

```bash
curl -fsSL https://raw.githubusercontent.com/houyc1217/yinch_auto_mkt/main/update.sh | bash
```

检查：

```bash
~/.yinch-auto-mkt/repo/scripts/check-env.sh
```

## 注意事项

> [!IMPORTANT]
> `linkedin-post` 发布前一定会先产出草稿，并且只在显式确认后发布。

> [!NOTE]
> `x-kol` 严格只统计 `article` 和 `post`。

> [!NOTE]
> `google-review` 优先抓取公开 Google Maps 评论，不默认要求 Google 登录。

> [!WARNING]
> 凭证、cookies、token 不会被写进仓库文件或输出物。Telegram token 和社媒连接信息只应保存在用户本地环境或外部集成里。

## License

MIT

---

Yincheng 感谢各位同事一直以来的帮助和支持，祝大家工作顺利。
