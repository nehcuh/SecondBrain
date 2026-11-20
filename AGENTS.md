# AGENTS.md — SecondBrain 系统契约 (v3.2)

> 本文件是外部 Agent / 自动化脚本操作此 Vault 的**唯一规则源**。人类向导见 `README.md`。
> 契约的可执行化是 `scripts/validate_cards.py`——修改本文件必须同步修改校验器，反之亦然。
> 所有卡片必须含 `type` 字段。日期一律 ISO 格式：`YYYY-MM-DD`；含时间的用 `YYYY-MM-DDTHH:mm`。
> 所有卡片可选 `icon` 字段（单个内容相关 emoji；勿用类型标记 📂🚀🎯📓💡📌📎），外部引用时以「icon 标题」形式展示。

---

## 0. Agent 行为守则（先读这一节）

### 写边界

- ✅ **可写**：`01 Goals/`、`02 Areas/`、`03 Projects/`、`05 Notes/`、`06 Tasks/`、`07 Habits/`、`99 Conflict/`
- ❌ **禁改**：`🏠 Home.md`、`AGENTS.md`、`README.md`、`.obsidian/`、`99 Templates/`、`scripts/`、`.gitignore`（需要变更时向人类报告，由人类执行）

### 操作纪律

1. **写前必读**：修改任何卡片前先完整读取目标文件。
2. **幂等**：打卡 / 补全 / 标记完成类操作，先检查目标状态再写入。例：`checkins` 已含今日日期则跳过，不得重复插入。
3. **单文件短事务**：批量操作逐文件完成，不长时间持有多个文件的半成品状态。
4. **校验闭环**：任何批量写入后必须运行 `uv run scripts/validate_cards.py` 并达到 **0 ERROR**；达不到则回滚本次修改后报告。
5. **冲突处理**：目标文件内容与预期不符（疑似并发修改）时——后写胜前，但把预期版本保存到 `99 Conflict/<YYYYMMDD-HHmm>_<原文件名>`，并报告人类。
6. **不删除有内容的卡片**：废弃用 status 表达（`archived` / `abandoned` / `superseded`）。
7. **附件**：图片等资源放入该卡片所在目录的 `_assets/` 子目录（Newton `save_attachment` 同此路径）。
8. **优先用运行时工具**：捕获任务 / 完成任务 / 习惯打卡 / Inbox 检索优先调用 `uv run scripts/sb.py <子命令>`（内置上述纪律），不要手写等价逻辑；MCP 客户端直接挂 `scripts/mcp_server.py`。
9. **操作先读手册**：AI 需要操作本 Vault 时，先读 `05 Notes/Handbook/📋 AI 操作手册.md`（操作目录 + 触发词 + 各操作契约规则 + 执行面）；Newton 对话运行时自动加载该手册与本文件。
10. **记忆优先**：操作某类型卡片前先读 `05 Notes/Handbook/📋 记忆-<类型>.md`（存在时）；全局个人口径在 `📋 记忆-全局.md`——两者是用户的历史纠正与偏好，优先级高于一般推断；发现新的用户纠正时提示用户可让 Newton 记入（remember 动作）。

---

## 1. 目录结构

```
/
├── 🏠 Home.md                   # 单页仪表盘（禁改；启动页；dataviewjs）
├── 🗺️ Atlas.md                  # 全局拓扑（生成文件；scripts/gen_atlas.py 重建）
├── .claude/skills/              # Claude Code 技能（sb-triage 分诊等）
├── AGENTS.md                    # 本文件（机器契约）
├── README.md                    # 人类文档（产品说明）
├── scripts/
│   ├── validate_cards.py        # 契约校验器（pre-commit 钩子入口）
│   ├── sb.py                    # Agent 幂等操作 CLI（capture/complete/set_field/checkin/inbox）
│   ├── gen_atlas.py             # 全局拓扑生成器（确定性，无 AI）
│   └── mcp_server.py            # MCP 网关（Agent 原生接入）
├── 01 Goals/                    # 目标（YYYY[/Qn[/MM]]，长期目标在根）
├── 02 Areas/                    # 领域 + 子领域（各带 📂 卡片 + _assets/）
├── 03 Projects/                 # 项目（YYYY/项目名/🚀 项目名.md + _assets/）
├── 05 Notes/
│   ├── Journal/Daily/YYYY/MM/   # 📅 YYYY-MM-DD.md
│   ├── Journal/Weekly/          # 📊 周报_YYYY-Www.md
│   ├── Journal/Monthly/         # 📊 月报_YYYY-MM.md
│   ├── Learning/YYYY/MM/        # 📖 渐进式阅读笔记
│   ├── Handbook/                # 📋 手册
│   ├── Blog/YYYYMM/文章名/      # ✍️ 文章名.md
│   ├── Topics/主题名/           # 📓 主题名.md
│   ├── Meetings/YYYY/MM/        # 🤝 标题_YYYY-MM-DD.md
│   ├── Contacts/                # 👤 姓名.md
│   ├── Clip/YYYY/MM/            # 📎 标题.md
│   ├── Knowledge/               # 📌 知识卡片
│   └── Inspiration/             # 💡 灵感
├── 06 Tasks/YYYY/MM/            # 标题_MMDD.md
├── 07 Habits/                   # 🔄 标题.md
├── 99 Conflict/                 # 冲突副本（Agent 写入）
└── 99 Templates/                # 模板（禁改）
```

---

## 2. 卡片类型目录

### 🎯 Goal（目标）

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `"goal"` | |
| `level` | `"annual"\|"quarterly"\|"monthly"\|"longterm"` | 层级 |
| `title` | `string` | |
| `status` | `"active"\|"completed"\|"abandoned"` | |
| `parent` | `wikilink`（可选） | 上级目标 |
| `progress` | `number` 0-100（可选） | |
| `tags` | `string[]` | 含 `goal` |

- **模板**：`99 Templates/Goals/Goal-*.md`；**位置**：`01 Goals/YYYY/🎯 标题.md`，季度 `YYYY/Qn/`，月度 `YYYY/Qn/MM/`，长期 `01 Goals/🎯 标题.md`

### 📂 Area（领域）

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `"area"` | |
| `name` | `string` | 纯名称（无 emoji） |
| `status` | `"active"\|"dormant"` | |
| `description` | `string` | 一句话 |
| `parent` | `string`（可选） | 父领域 name |
| `icon` | `string`（可选） | emoji |

- **位置**：`02 Areas/领域名/📂 领域名.md`；子领域同理

### 🚀 Project（项目）

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `"project"` | |
| `name` | `string` | 去 emoji |
| `status` | `"planning"\|"active"\|"done"\|"archived"` | |
| `deadline` | `date` | |
| `area` | `wikilink` | 所属领域 |
| `progress` | `number` 0-100 | |
| `priority` | `"high"\|"medium"\|"low"` | |

- **位置**：`03 Projects/YYYY/项目名/🚀 项目名.md`

### ✅ Task（任务）

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `"task"` | |
| `title` | `string` | 文件名去掉 `_MMDD` 后缀 |
| `status` | `"todo"\|"in-progress"\|"paused"\|"done"` | paused=搁置（不计逾期、不进开放清单） |
| `priority` | `"urgent"\|"high"\|"medium"\|"low"` | |
| `due` | `date`（可选 ` HH:MM` 后缀） | **一律当真**：字段有值即真截止（提醒/逾期/报告按日期部分判）；没说截止就留空——写入端禁止播种创建日假 due |
| `area` / `project` / `topic` | `wikilink` | 关联（领域/项目/主题；三关联任一非空即不进 Inbox） |
| `owner` | `wikilink`（可选） | 负责人（👤 联系人卡，受控词表强制，可只说人名不带前缀）；委托他人时才填，空 = 自己；开放任务 owner 非空即「等待中」（GTD waiting-for，读取时推导，不动 status 枚举）；due 顺手记约定回收日（逾期 = 催办时机） |
| `collaborators` | `list[string]`（可选） | 参与人（人名数组，与会议 attendees 同款；共同完成非交办；写入合并去重、wikilink 输入归一成人名） |
| `source` | `wikilink`（可选） | 来源卡 stem；`capture_task --source` 创建时校验可解析 |
| `createdAt` | `datetime` | |
| `completedAt` | `datetime`（done 时必填） | Agent 打卡精确到分钟（`YYYY-MM-DD HH:MM`） |
| `pausedAt` | `date`（可选） | status=paused 自动记、恢复自动清（搁置时长溯源） |
| `activeSince` | `datetime`（可选） | 当前工作段起点；status→in-progress 自动盖、离开（paused/done/退回）自动结算成 sessions 条目并清除（<1 分钟丢弃）；仅 in-progress 状态应存在（残留校验 WARN） |
| `sessions` | `list[string]`（可选） | 投入时段条目 `"YYYY-MM-DD HH:MM ~ YYYY-MM-DD HH:MM"`（引号包裹、日期须真实存在、按时间序、单段 ≤24h）；自动结算（状态流转）或 `log_session` 补录（「我两点到三点半在做 X」）；写入端全条目合法时自动按起始时间排序、任意残值形态归一成块列表；统计按起始日归属（进行中未结算段按当下折算另行标注，不写回卡片） |

- **完成方式**：`status` → `done` 且补 `completedAt`（Agent 或手动）；有未结 `activeSince` 一并结算
- **退役字段**（2026-11 元数据治理，出现即校验 WARN）：`scheduled`/`energy`/`assignee`/`duration`/`context`/`actionable`/`delegate`
- **位置**：`06 Tasks/YYYY/MM/标题_MMDD.md`
- **Inbox 判定**：`area`/`project`/`topic` 三关联均为空 → Reports Inbox 可见

### 🔄 Habit（习惯）

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `"habit"` | |
| `title` | `string` | |
| `goal` | `wikilink`（可选） | |
| `frequency` | `"daily"\|"weekly"` | |
| `checkins` | `date[]` | YAML 多行列表，**不得重复** |
| `note` | `string`（可选） | 单行备注，Home 习惯卡副行展示 |
| `evidence` | `bool`（可选） | true 时打卡建议补注记 |
| `checkin_notes` | `map<date,string>`（可选） | 打卡注记（这次做了/看了什么）；checkins 有日期而此处缺键 = 待补注 |
| `daily_checklist` | `string[]` | Reports 展示 |

- **位置**：`07 Habits/🔄 标题.md`

### 🤝 Meeting（会议）

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `"meeting"` | |
| `title` | `string` | 文件名去掉 `🤝 ` 与 `_YYYY-MM-DD` |
| `status` | `"scheduled"\|"done"\|"cancelled"` | |
| `date` | `date`；`time` | `HH:MM` 或 `HH:MM-HH:MM` |
| `attendees` | `string[]` | |
| `area` / `project` / `topic` | `wikilink` | 关联（三关联任一非空即不进待分诊） |
| `minedAt` | `date`（可选） | 行动项挖掘日期；sb-triage 幂等门 |

- **位置**：`05 Notes/Meetings/YYYY/MM/🤝 标题_YYYY-MM-DD.md`

### 👤 Contact（联系人）

`type: "contact"`，`name` / `role` / `org`。**位置**：`05 Notes/Contacts/👤 姓名.md`

### 📓 Topic（学习主题）

`type: "topic"`，`title` / `status(active|done|archived)` / `area` / `progress`。**位置**：`05 Notes/Topics/主题名/📓 主题名.md`

### 📅 Journal（日记）

`type: "journal"`，`subtype: "daily"|"weekly"|"monthly"`，`date`。**位置**：`Journal/Daily/YYYY/MM/📅 YYYY-MM-DD.md`、`Journal/Weekly/`、`Journal/Monthly/`

### 📝 Note（笔记族，按 subtype 分化）

| subtype | 位置 | status 枚举 | 专属字段 |
|---------|------|-------------|----------|
| `clip` | `Clip/YYYY/MM/📎 标题.md` | `inbox\|processing\|archived` | `source`(URL) |
| `inspiration` | `Inspiration/💡 标题.md` | `spark\|developing\|live\|planned\|archived` | |
| `knowledge` | `Knowledge/📌 标题.md` | `active\|superseded\|archived` | `source`(wikilink) |
| `blog` | `Blog/YYYYMM/文章名/✍️ 文章名.md` | `draft\|published` | `url` |
| `learning` | `Learning/YYYY/MM/📖 标题.md` | `reading\|done\|archived` | `source`/`author`/`topic` |
| `handbook` | `Handbook/📋 标题.md` | `active\|archived` | |

---

## 3. 关联规则

- wikilink 可用短名（卡片 stem，如 `[[📂 技术]]`）或全路径（如 `[[02 Areas/技术/📂 技术]]`）
- `area` → Area 卡片；`project` → Project 卡片；`goal` → Goal 卡片；`parent`（目标/领域）→ 上级
- 联系人通过会议卡 `attendees` 字符串引用 `contact.name`

---

## 4. 界面

- **🏠 Home.md（单页仪表盘，启动页）**，自上而下 15 个区块：
1. 顶部统计（可点击跳转） | 2. Inbox | 3. 今日任务 | 4. 进行中 | 5. 今日会议 | 6. 习惯打卡（可交互）
7. 近 7 天 | 8. 灵感火花 | 9. 学习主题 | 10. 最近笔记 | 11. 今日完成 | 12. 活跃项目
13. 精进领域 | 14. 逾期任务 | 15. 目标进度

---

## 5. Agent 运行时与校验器

```bash
uv run scripts/validate_cards.py   # 退出码 0 = 0 ERROR；任何批量写入后的完成标准
uv run scripts/sb.py capture_task "标题" [--due …] [--priority …] [--area …] [--project …] [--topic "📓 主题stem"] [--source "🤝 会议stem"] [--owner 人名] [--collaborators 人名 …]
                                    # 全局同名查重：未完成同名任务（跨月）拒绝创建；owner 须为现有 👤 联系人（可只说人名）
uv run scripts/sb.py complete_task "标题片段"      # 幂等：status→done + completedAt
uv run scripts/sb.py set_field "标题片段" field value [--type …]  # 通用标量写入，校验失败自动回滚
uv run scripts/sb.py checkin_habit "习惯片段"      # 幂等：checkins 追加今日
uv run scripts/sb.py inbox                         # 无 area/project/topic 关联的未完成任务
uv run scripts/gen_atlas.py                        # 重建 🗺️ Atlas 全局拓扑
uv run scripts/check_reminders.py                  # 逾期/今日到期单行摘要（无命中静默；launchd 每日 08:57 推系统通知）
uv run scripts/mcp_server.py                       # MCP 网关（capture/complete/checkin/inbox + search/brief/validate；不含 set_field/--source，挖矿走 sb.py CLI）
uv run scripts/stamp_new_vault.py /path/to/new     # 盖章新 vault（分发脚手架）
```

Obsidian 插件 **Newton**（对话/捕获/分诊/搜索）与上述 CLI 共享同一契约；其对话动作块（create_task / complete_task / checkin_habit / enrich_card + 查询 count_tasks / list_tasks / search_cards / list_inbox / today_brief）语义与 `sb.py` 幂等子命令一一对应（enrich_card 受控词表由执行器强制、只补空字段）；附件动作 save_attachment / read_attachment、改名动作 rename_card 与记忆动作 remember / read_memory 仅 Newton（CLI 无二进制通道/暂无对应子命令），操作目录见 `05 Notes/Handbook/📋 AI 操作手册.md`。
校验范围：frontmatter 可解析、type/必填/枚举、日期格式、wikilink 可解析（短名/全路径/附件）、路径规范（含双层嵌套检测）、checkins 去重、命名规范。

---

## 6. 不可变规则

- ❌ 不要修改 `🏠 Home.md`、`AGENTS.md`、`README.md`、`99 Templates/`、`.obsidian/`、`scripts/`
- ❌ 不要在 `99 Templates/` 外创建模板
- ✅ 所有卡片必须含 `type`；所有日期 ISO 格式
- ✅ 批量写入后校验必须 0 ERROR
- ✅ 附件入就近 `_assets/`
