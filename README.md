# SecondBrain — 卡片式第二大脑（Obsidian + AI）

一套「开箱即用」的个人知识库模板：**目录即架构、卡片即契约、脚本守纪律、AI 当助手**。
用 [Obsidian](https://obsidian.md) 打开就是一个能跑起来的完整系统——看板、模板、校验脚本、命令行工具、AI 对话插件全齐。

> 仓库内置一套 **mock 示例数据**（张三/李四、晨跑、周会……），用来演示各卡片形态与看板效果。
> 熟悉后整体删除 `01 Goals/`~`07 Habits/` 下的示例卡即可开始自己的内容，骨架会由模板重建。

---

## 它能做什么

| 能力 | 入口 |
|------|------|
| 🏠 单页看板：今日到期/逾期、待分诊 Inbox、习惯打卡、领域/项目/目标统计 | `🏠 Home.md`（homepage 插件自动落位） |
| 🗺️ 全局拓扑图：目标 → 领域 → 项目 → 任务簇，红色标异常 | `🗺️ Atlas.md`，`uv run scripts/gen_atlas.py` 重建 |
| 📥 快速捕获：Cmd+P 唤起 QuickAdd，按模板建任务/会议/联系人…… | 16 个 QuickAdd 选择，全部走 `99 Templates/` |
| ✅ 契约校验：卡片 frontmatter 违规当场报错（枚举/路径/断链/退役字段） | `uv run scripts/validate_cards.py`，退出码 0 = 健康 |
| 🤖 Newton AI 插件：对话式捕获/分诊/查询/完成，AI 只能走动作块写库，写前校验 | 设置里填 API Key 即用（见下文） |
| 🔔 提醒推送：扫描逾期与今日到期任务，输出单行摘要（可接系统通知） | `uv run scripts/check_reminders.py` |
| 📋 操作手册：AI 与人的完整操作目录（怎么捕获、怎么分诊、怎么复盘） | `05 Notes/Handbook/📋 AI 操作手册.md` |
| 🧠 MCP 网关：把幂等写操作暴露给任意 Agent（Claude Code 等） | `uv run scripts/mcp_server.py` |

## 快速开始

### 1. 环境要求

- [Obsidian](https://obsidian.md)（桌面端；iPad 端也支持，插件为 isDesktopOnly: false）
- [uv](https://docs.astral.sh/uv/)（Python 工具链，脚本与校验都靠它跑）

### 2. 打开库并启用插件

用 Obsidian 「Open folder as vault」打开本目录。

设置 → 第三方插件：关闭安全模式，启用全部插件（本仓库已捆绑，无需另装）：

- **dataview**（必须）——Home / Atlas / 卡片内动态表格全靠它
- **templater-obsidian**（必须）——QuickAdd 建卡走模板
- **homepage**——打开 Obsidian 直达 🏠 Home
- calendar / heatmap-tracker / iconize / quickadd / rainbow-* —— 看板与打卡热力图
- **newton**——AI 助手（可选，见第 4 步）

### 3. 跑一遍校验（确认环境 OK）

```bash
cd <本目录>
uv sync                              # 首次：装 Python 依赖
uv run scripts/validate_cards.py     # 应输出 0 ERROR / 0 WARN
```

### 4. （可选）启用 Newton AI 助手

Newton 是内置的 AI 对话插件：在右侧边栏与 AI 对话，它能**通过动作块安全地**建任务、改属性、查统计——所有写入都走与命令行同一套契约校验，AI 无法绕过。

1. 设置 → Newton → 填入 API Key（兼容 OpenAI Responses 接口；Key 只存在本机 `data.json`，已被 gitignore）
2. 打开对话侧边栏，试着说：`记个待办：明天上午打电话给张三`
3. AI 会发一个 `create_task` 动作块并执行，任务落到 `06 Tasks/2026/11/`，回报可点击的卡片链接

更多玩法（语音捕获、会议行动项挖掘、自动日记/周报、长任务执行、后台知识沉淀）见 `05 Notes/Handbook/📋 AI 操作手册.md`。

### 5. 捕获你的第一个任务

- 界面：Cmd+P → `✅ 新建任务`
- 命令行：`uv run scripts/sb.py capture_task "你好，第二大脑" --due 2026-12-01`
- AI 对话：对 Newton 说「记个待办：……」

## 每天怎么用（最小工作流）

```
随手捕获（QuickAdd / Newton / CLI）
   ↓ 没想清楚归属就先空着 → 自动进「待分诊 Inbox」
每周分诊（enrich_card 补领域/项目/主题）
   ↓
每天执行（Home 看板看今日到期/逾期；完成打勾，Newton 或 CLI 均可）
   ↓
定期复盘（日记/周报自动聚合真实数据；🗺️ Atlas 看全局拓扑）
```

核心纪律只有一条：**先设计接口，再填充内容**——每张卡片都有类型契约（见 `AGENTS.md`），
AI 与脚本写入前必须过校验，人手改也随时可以全库体检。

## 目录结构

```
01 Goals/        🎯 目标（年度/季度/月度/长期，目录即层级：2026/Q4/…）
02 Areas/        📂 领域（要持续负责的事，过「三测」才配建：无终点/有后果/是角色）
03 Projects/     🚀 项目（有终点线的事，按年归档：2026/…）
05 Notes/        📓 主题 / 👤 联系人 / 🤝 会议 / 📌 知识 / 💡 灵感 / 📎 剪藏 / ✍️ 博客 / 📋 手册 / 日记周报
06 Tasks/        ✅ 任务（按月归档：2026/11/标题_1120.md）
07 Habits/       🔄 习惯（打卡 + 热力图）
99 Templates/    全部卡片模板（QuickAdd / Templater 引用）
scripts/         Python 工具集（sb.py 幂等写操作 / 校验 / 提醒 / Atlas / MCP）
.obsidian/       插件与配置（Newton 的 API Key 在 data.json，不入库）
AGENTS.md        卡片契约 + Agent 行为守则（单一事实源，AI 工具都会读它）
🏠 Home.md       单页看板
🗺️ Atlas.md      全局拓扑（生成物，勿手改）
```

## 卡片类型速览

| 类型 | 位置 | 关键字段 |
|------|------|----------|
| task 任务 | 06 Tasks/YYYY/MM | status（todo/in-progress/paused/done）、due、area/project/topic 三关联、owner（委托=等待中）、collaborators、sessions（投入时段） |
| meeting 会议 | 05 Notes/Meetings/YYYY/MM | date、time、attendees、行动项派生任务（source 双链） |
| goal 目标 | 01 Goals/YYYY[/Qn] | level（annual/quarterly/monthly/longterm）、parent、progress |
| area 领域 | 02 Areas | name、status（active/dormant）——建卡前先过三测 |
| project 项目 | 03 Projects/YYYY | deadline、area、progress |
| topic 主题 | 05 Notes/Topics | area（挂在领域下）、学习目标 |
| habit 习惯 | 07 Habits | frequency、checkins、checkin_notes |
| note 笔记 | 05 Notes/* | subtype（knowledge/learning/clip/inspiration/blog/handbook） |

完整契约（必填/枚举/格式/退役字段）见 `AGENTS.md`。

## 脚本清单

```bash
uv run scripts/sb.py capture_task "标题" [--due …] [--priority …] [--area …] [--owner 人名]   # 捕获任务
uv run scripts/sb.py complete_task "标题片段"          # 完成任务（幂等）
uv run scripts/sb.py checkin_habit "习惯片段" [--date …] [--note …]   # 习惯打卡
uv run scripts/sb.py inbox                            # 待分诊清单
uv run scripts/sb.py enrich_card "查询" --area "[[📂 工作]]" [--owner 人名] [--force]  # 分诊/补属性
uv run scripts/validate_cards.py                      # 全库契约校验（0 ERROR 才算健康）
uv run scripts/check_reminders.py                     # 逾期/今日到期摘要（退出码 1=有提醒）
uv run scripts/gen_atlas.py                           # 重建全局拓扑
uv run scripts/mcp_server.py                          # MCP 网关（Agent 原生接入）
uv run scripts/stamp_new_vault.py /path/to/new-vault  # 从本库再分发一个全新空库
```

提交钩子已配好（`.githooks/pre-commit`）：每次 git commit 自动跑全库校验，非 0 ERROR 拒绝提交。

## 自动化（可选）

- **每日提醒**：把 `check_reminders.py` 挂进 cron / launchd，早上推送逾期与今日到期。
- **AI 夜间分诊 / 周报**：Newton 插件内置定时任务（设置里可开关），无需额外配置。
- **MCP 接入 Claude Code**：`claude mcp add secondbrain -- uv run scripts/mcp_server.py`（在本目录执行）。

## Mock 数据说明

`01`~`07` 目录下的示例卡覆盖了所有形态，建议按这张表对照着看一遍再删：

| 看什么 | 卡片 |
|--------|------|
| 三关联任务 | 完成英语第六课练习（topic）、提交项目周报（area） |
| 待分诊 Inbox | 整理书桌并归档旧笔记（三关联全空） |
| 进行中计时 | 晨跑 5 公里（activeSince） |
| 搁置 + 投入统计 | 学完 Obsidian 基础课（paused + sessions） |
| GTD 等待中 | 约张三评审知识库方案（owner + collaborators + due=回收日） |
| 逾期提醒 | 预约年度体检（due 已过） |
| 会议派生 | 项目周会 → 跟进行动项（source 双链） |
| 目标层级 | 年度 → Q4 季度 → 长期目标（parent 链） |

## 设计文档

- `AGENTS.md` —— 卡片契约与 Agent 守则（单一事实源）
- `05 Notes/Handbook/📋 个人知识库搭建方法论.md` —— 为什么这样设计
- `05 Notes/Handbook/📋 AI 操作手册.md` —— 全部操作目录（人 + AI 通用）

## License

仅供个人学习使用。
