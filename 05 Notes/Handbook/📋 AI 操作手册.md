---
type: note
subtype: handbook
title: "AI 操作手册"
area: "[[02 Areas/个人成长/📂 个人成长]]"
tags: [handbook, ai, operations, newton]
createdAt: 2026-11-17
updatedAt: 2026-11-17
archived: false
---

# 📋 AI 操作手册

> [!info] AI 操作本库的唯一目录与规则源。任何 AI（Newton 插件 / Claude Code / 夜间分诊）需要读写本 Vault 时，先读本卡。Newton 对话启动时自动加载本卡与 AGENTS.md 契约。

## 纪律（先于一切操作）

1. **行级手术**：只改目标行/字段，禁止整段 YAML 或全文重写
2. **幂等**：重复执行同一操作 = 安全跳过，且必须明示「已存在/已跳过」，永不静默失败
3. **写后校验**：写完必须校验（Newton 内置契约校验；Claude Code 跑 `uv run scripts/validate_cards.py`），失败回滚
4. **受控词表**：area/project/goal/topic 只能引用现有**未归档**卡片 wikilink stem（如 `[[📂 工作]]`、`[[📓 英语]]`），禁止编造；tags 一律小写
5. **git 是回滚底线**：每批变更一个 commit；用户未提交的工作区改动绝不混入
6. **禁改**（除非用户明确要求）：🏠 Home.md / AGENTS.md / README.md / .obsidian/ / 99 Templates/ / scripts/ / .gitignore

## 操作目录

### 1. 创建待办 create_task
- **触发**：「记个待办…」「帮我建任务：明天体检」「别忘了 X」
- **参数**：title（必填，短语化标题）；可选 area/project/goal/topic/priority/tags——语义能明确匹配词表时直接带上（捕获即分诊），不确定就留空待夜间分诊；可选 source（库内卡完整名，任务从某张卡派生时用，如从阅读材料派生的练习）；可选 due（YYYY-MM-DD，可选 HH:MM）——**不用主动带**：执行器默认播种当日（新建当天首页可见，当天没做完次日进逾期属预期催办口径）；只有用户说了别的截止时间才带；可选 owner（👤 联系人卡名，可只说人名不带前缀——「这事交给 X」「等 X 回复」时带，owner 非空即「等待中」，due 顺手记约定回收日）；可选 collaborators（人名数组——「我和 X 一起做」类共同完成）
- **规则**：路径 `06 Tasks/YYYY/MM/<标题>_MMDD.md`；status: todo、priority: medium、**due 未指定默认播种当日**（格式非法回退当日并说明）；area/project/goal/topic 受控词表校验（无效词不阻塞捕获——忽略并在回报中说明）；owner 同样受控词表（👤 联系人卡，无效不阻塞、忽略并说明）；goal 同时写 frontmatter 与正文「相关」节双链；source 校验须为库内唯一卡名，同样写 frontmatter + 正文「源材料」双链
- **执行面**：Newton 动作块 ｜ Claude Code：`uv run scripts/sb.py capture_task --title "…"` ｜ URL：`obsidian://newton?capture=…`

### 2. 完成任务 complete_task
- **触发**：「XX 做完了」「完成 XX」
- **参数**：title = 任务标题片段，必须唯一定位 06 Tasks 下一张卡
- **规则**：status→done 且 completedAt=今天（本地日期，精确到分钟 `YYYY-MM-DD HH:MM`）；已完成则幂等跳过
- **执行面**：Newton 动作块 ｜ `uv run scripts/sb.py complete_task --query "…"`

### 3. 习惯打卡 checkin_habit
- **触发**：「打卡」「今天 XX 了」
- **参数**：title = 习惯名片段（07 Habits 下唯一匹配）；note（可选）= 这次做了/看了什么，≤200 字
- **规则**：checkins 列表追加今天；当日已打卡则幂等跳过；带 note 时同步写 `checkin_notes`（日期 → 注记）；当日已打卡再收 note → 补注记不重复打卡
- **证据打卡**：卡片 `evidence: true` 的习惯，打卡时用户应描述具体内容（AI 主动带上 note）；checkins 有日期而 checkin_notes 缺键 = 待补注，Home 卡片显示 ⚠️ 徽章
- **执行面**：Newton 动作块（`{"action":"checkin_habit","title":"…","note":"…"}`）｜ `uv run scripts/sb.py checkin_habit "…" --note "…"`

### 4. 卡片分诊（AI 补全属性）
- **触发**：每晚 22:17 launchd 自动 ｜ 「帮我整理收件箱」（Newton 对话内直接可用，iPad 同样生效）
- **规则**：只补空字段、非空不覆盖（覆盖需显式 force）；area/project/goal/topic 用受控词表（Newton 由执行器强制，只能引用现有**未归档**领域/项目/目标/主题卡——已归档卡会被拒并提示）；**Inbox 判定 = area/project/topic 三关联均为空**（任务与会议同规则：任一关联非空即视为已分诊）；低置信保留原状标「待人工」；夜间流程完成后 Atlas 重生成 + 变更报告 + git commit
- **领域三测**（Newton v0.6.3 起内置同款准则）：领域 = 持续经营的责任，须同时过 ①无终点 ②有后果 ③是角色 三关；学习型兴趣主题（AI 实践/编程/知识管理类）不是领域，归 `05 Notes/Topics` 主题卡——不要给这类主题建领域或建议建领域
- **执行面**：Newton 动作块 list_inbox（列待分诊）+ enrich_card（补全与属性更新，query 定位卡片，可选 area/project/goal/topic/priority/tags/icon/status/time/due/owner/collaborators；status 按类型枚举校验——任务含 paused（搁置：自动记 pausedAt、不计逾期，恢复自动清），time 仅会议卡、due 仅任务卡（`YYYY-MM-DD` 或带时刻 `YYYY-MM-DD HH:MM`），owner 仅任务卡且须为现有 👤 联系人卡名（可只说人名不带前缀，编造直接拒绝——「这事交给 X」「等 X 弄完」时用，非空即等待中），collaborators 仅任务卡（人名数组合并去重，「我和 X 共同完成」时用），更新已有值须 force；icon 为单个内容相关 emoji，勿用类型标记）——「会议结束了改已完成」（顺带确认结束时间把 time 补成区间）「这事延期到 X」「这事先放放」同类属性变更也走 enrich_card ｜ Claude Code 遵循 `.claude/skills/sb-triage` ｜ 单卡：`uv run scripts/sb.py enrich_card 06 "查询" --area "[[📂 工作]]" --owner 人名 --collaborators 人名 … --strip-dead`（--owner 同受控词表可只说人名；--collaborators 合并去重；--strip-dead 清退役字段：scheduled/energy 等）
- **投入计时（v0.9）**：「开始做 X」→ in-progress 自动盖 `activeSince` 开始计时；暂停/完成/退回自动结算成 `sessions` 条目（`"起 ~ 止"` 分钟精度，<1 分钟丢弃，日期须真实存在）；**事后补录是主路径**——「我两点到三点半在做 X」「昨天上午花了两小时弄 Y」→ log_session（start/end 须用户明说，禁止猜测；单段 ≤24h；写入自动按起始时间排序，手改的行内数组/折叠等残值形态自动归一）。统计：today_brief 显示今日投入合计（进行中任务另标「另有进行中 Xm 未结算」，按当下折算不写卡）；周报/月报含 ⏱ 投入统计（按任务+领域汇总，窗口按 session 起始日归属）
- **记住用户口径 remember**（v0.10.0）：用户纠正你的理解（「不是 X 是 Y」）、说明长期习惯偏好、约定术语（「我说 X 指 Y」）时主动记——content 一句话（≤120 字），type 选 全局（默认）/任务/会议/习惯/目标/领域/项目/联系人；写入 `05 Notes/Handbook/📋 记忆-<类型>.md`（惰性建卡，条目 `- 日期 内容`）；重复内容自动去重；记忆满（全局 50/类型 30 条）先 read_memory 再 mode:"rewrite" 全量整理（content 为完整条目清单，每行一条）。不用请示，记完报告即可
- **查看记忆 read_memory**（v0.10.0，query 类）：type 同上，默认全局——改写记忆前必读；用户问「你记得我哪些习惯」时用它如实回答。记忆的加载机制：全局记忆每轮注入系统提示；类型记忆在动作涉及该类型时随结果回喂（另：沉淀循环会顺带从会话提取个人口径候选写入记忆卡，设置「沉淀挖记忆」可关）
- **改卡片标题 rename_card**（v0.9.2）：「把这个任务改名为 X」「标题里的部门名写错了」——query 定位唯一卡，title 传新标题（纯文字，不带 emoji 前缀/日期后缀）；一次同步四处：文件名（保留类型 emoji 前缀与 `_MMDD`/`_日期` 后缀）、frontmatter 名称字段（title/name）、正文一级标题、全库 wikilink 引用（目标全路径/短名 + 别名）；领域/项目/主题/博客目录名与标题同名，连带目录一起改（`_assets` 随迁）；日记卡（文件名即日期）不支持；目标撞名一律拒绝不覆盖。执行面：仅 Newton（sb.py / MCP 暂无对应子命令）

### 5. 查询操作（只读）
- **触发**：「我有多少待办」「列一下任务」「搜一下 X 相关的卡片」「今天有什么安排」
- **规则**：凡数量/统计/清单/查找类问题，必须先发查询动作块、用回报的真实数据回答，禁止编造数字
- **执行面**：Newton 动作块 count_tasks（统计，开放数含「等待中」拆分）/ list_tasks（scope: open|overdue|waiting|done|all，filter 可选；waiting = 委托出去等回收的，行内 ⏳人名 标记，due = 约定回收日）/ search_cards（query 必填，文件名+正文匹配）/ list_inbox（待分诊清单）/ today_brief（今日简报：到期/逾期/今日完成/会议/习惯打卡）/ read_attachment（卡片附件：name 省略列清单、指定则读回对话）｜ Claude Code `uv run scripts/sb.py inbox` + grep ｜ 拓扑看 🗺️ Atlas.md
- 回答中引用卡片一律用 `[[文件名]]`

### 6. 语音输入
- **触发**：对话输入区 / 捕获弹窗的麦克风按钮
- **规则**：配置了转写 API 时录音 → HTTP 转写，两种**接口风格**（设置 → Newton → 语音转写）：
  - **openai**：`/audio/transcriptions`（model+language+file，whisper 系，MediaRecorder webm 直传）
  - **deepseek**：`/v1/tools/asr`（仅 file 字段、语种自动检测；只收 16 位 PCM WAV / Ogg Opus，故插件直录 PCM 前端编码 WAV 再上传）
  - 未配置时 Mac 自动调**系统听写**（点击系统注入的"开始听写…"菜单项，文字直接落输入框；首次需在 系统设置 → 隐私与安全性 → 辅助功能 允许 Obsidian）；iPad 用键盘听写键
- **执行面**：仅 Newton 插件

### 7. 提醒推送（逾期/今日到期）
- **触发**：launchd 每日 08:57 自动（com.benniu.sb.remind）
- **规则**：扫描 06 Tasks 开放任务；**due 一律当真**——字段有值即真截止，到期就提醒、过期就报逾期（capture 默认播种当日：新建当天可见，当天没做完次日进逾期，属预期催办信号）；owner 非空的委托任务逾期即催办信号（due = 约定回收日）；status=paused 的搁置任务不扫；同日只推一次；无命中静默
- **执行面**：`uv run scripts/check_reminders.py`（stdout 单行摘要；退出码 0=无命中/1=有提醒/2=失败）→ wrapper 发 macOS 通知

### 8. 会议行动项挖掘
- **触发**：夜间分诊流程内（sb-triage 步骤 6）自动
- **规则**：只挖 `status=done` 且无 `minedAt`、date 近 30 天、无 `<!-- no-mine -->` 的会议卡；每晚 ≤3 张；行动项必须动词开头有交付物；新任务 priority ≤ medium，经 `--source` 关联会议卡 stem；挖完（含挖出 0 条）必写 `minedAt`，这是幂等门
- **执行面**：`uv run scripts/sb.py capture_task "行动项" --source "🤝 会议stem"` + `uv run scripts/sb.py set_field "会议片段" minedAt 2026-11-17 --type meeting`

### 9. 对话分支与自定义提示（Newton 界面，人类操作）
- **消息动作条**（hover 消息浮现；iPad 触屏常显）：**复制** ｜ **重新生成**（末条助手消息，重放末轮）｜ **编辑重发**（改历史提问，截断其后对话重新开始）｜ **从此分支**（fork 出新会话，原会话保留，历史面板中分支带 ᛘ git-branch 徽章）
- **自定义提示**：设置 → Newton → 自定义系统提示（角色/风格指令，附加默认提示后）+ 用户背景（"你是谁"，每轮注入，相当于 Custom Instructions）
- **规则**：分支/编辑重发期间原会话不动，探索式提问优先开分支；AI 不感知分支结构，无需特殊指令

### 10. 附件解析（Newton 界面，人类操作）
- **入口**：输入栏回形钉选文件（图片/PDF/md/txt/csv/json 等）或直接**粘贴截图**；chip 预览可移除
- **规则**：图片自动降尺度（>4MB 或边>2048 重编码）后走多模态识别；PDF 由 Anthropic/Responses 协议原生直读（chat/completions 协议不可读，模型会如实说明）；文本类内联进消息。仅最近 6 条消息的附件参与请求，更早的自动降为占位（省 token）；会话持久化只存附件名不存内容
- **存为卡片附件 save_attachment**：「把这张图存到 X 卡上」——对话内贴入的文件（最近 12 个具名附件）落目标卡就近 `_assets/` 目录（与本库附件路径规则同源），正文 `## 附件` 节（可用 section 参数自定义）自动插 `![[嵌入]]`；同名同内容幂等（只补嵌入），同名不同内容自动加 `-N` 后缀永不覆盖；会话里有多个附件时用 name 指明文件名
- **读取卡片附件 read_attachment**：「看看 X 卡的附件」——name 省略列清单；指定后图/PDF 转 dataUrl、文本内联，随附件通道回喂下一轮对话（多模态）；只认卡片正文引用的库内非 md 文件，路径全匹配 > 尾段 > 文件名；不支持类型（如 .bin）与超限（图 >4MB / PDF >10MB / 文本 >200KB）诚实拒绝
- **执行面**：仅 Newton 插件（多模态需模型支持，如 claude-sonnet / gpt-4o / glm-4v 系）；sb.py / MCP 无对应子命令——CLI 无二进制数据源、MCP 通道不消费多模态，附件存取只走 Newton 对话

### 11. 长任务模式（Newton 界面，sb-plan）
- **触发**：用户要求多步执行、盘点、批量整理类任务（如"盘点所有逾期任务并整理成清单"）时，Newton 先发计划块再逐轮执行
- **规则**：
  - 计划块 `{"steps":[{"text":"…","tool":"动作名"},…]}`（```sb-plan 围栏），2–8 步；绑定动作的步骤由**系统在动作执行成功后打勾**（模型自报完成不构成证据）；无绑定动作的步骤（如"写总结"）由用户在清单上点**确认**
  - 三重熔断：轮数上限（默认 12）/ 墙钟（默认 10 分钟）/ 连续 3 轮无进展——任一触发即**诚实中止**（列出未完成步骤，绝不虚报），清单上出现**继续执行**按钮（重开预算窗，绝不自动复活）
  - 查询类动作（count/list/search）并发执行（共享槽池，设置可调并发数），写类动作永远串行
- **执行面**：仅 Newton 插件；任务状态随会话持久化，中断后重开会话可从清单继续

### 12. 后台沉淀循环（自动，用户无感）
- **触发**：Newton 启动 15 秒后扫一轮 + 每 60 分钟 + 命令"立即运行沉淀循环"；**仅应用打开时运行**（移动端杀后台即停，重启后幂等门防重复写卡）
- **规则**：
  - 候选：≥6 条消息（可调）、最后更新已稳定 5 分钟、未沉淀过、非当前打开会话；对话进行中自动让路
  - 产物：LLM 抽取摘要（一句话 tldr + 要点）→ **脱敏**（PEM/sk-/ghp_/api-key 等形状一律替换 `[已脱敏]`）→ 写成 `05 Notes/Knowledge/📌 <标题>.md` 知识卡（type: note / subtype: knowledge / status: active，**契约校验通过才落卡**，路径冲突加序号后缀）
  - 无要点的会话只记指纹不写卡（防反复重试）；空会话/单轮纯壳会话自动清理（有动作块/附件/分支/任务的一律保留）
  - 报告：Notice + 设置页"上次循环"展示；知识卡不自动 git 提交，随夜间 sb-triage 流程入库
- **执行面**：仅 Newton 插件（设置 → 后台沉淀与长任务，可关）

### 13. 工作区感知（自动，模型侧）
- 每轮系统提示自动附「当前工作区状态」：打开的标签页（≤10，标出活动）、活动文件路径及其开头摘录（≤600 字，含 frontmatter）
- 用户说「这篇笔记」「当前文件」即指活动文件——直接基于摘录整理/讨论；需要更多内容时用 search_cards 定位，不让用户贴路径
- 长任务模式下每轮刷新快照：用户中途切换标签页，模型下一轮即跟上

### 14. 代码练习生成（读什么练什么）
- **触发**：「出这周的代码练习」「来一道练习题」
- **流程**：search_cards 搜最近阅读材料（📖 学习卡 / 📌 知识卡 / 技术阅读打卡注记）→ 从源材料抽关键概念 → 推导一个具体编码场景 create_task（动词开头、明确交付物、source 双链回源材料、tags 带「代码练习」）
- **硬约束**：场景必须从源材料内容推导，回复中说明推导依据；找不到近期阅读材料时如实说明并请用户指定方向，不凭空编通用练习
- **闭环**：完成练习任务卡（complete_task）后，勾选习惯 [[07 Habits/🔄 每周代码练习（读什么练什么）]] 打卡

### 15. 日记与周期报告（自动 + 手动）
- **触发**：自动——每天 21:00 后出当天日记（当天没打开的次日补昨天，更早不追）；手动——「记日记」「出今天的日记」「这周干了啥」
- **产物**：`05 Notes/Journal/Daily/YYYY/MM/📅 YYYY-MM-DD.md`（周报/月报同目录族）；数据节由执行器从库内卡片聚合（今日到期（含逾期结转）/完成/新建任务、会议、习惯打卡、笔记、知识沉淀、⏱ 投入），AI 只写洞察段；留「今日思考/明日计划」空节给手写
- **纪律**：日记卡已存在则跳过（绝不覆盖手写内容）；当天库内无任何动静不生成空日记；设置「自动日记」默认开
- **执行面**：仅 Newton（range day|week|month；sb.py / MCP 暂无对应子命令）

## Newton 动作块格式

用户明确要求记待办/完成/打卡时，回复末尾必须附动作块（口头答应 ≠ 已写入）；数量/统计/查找类问题必须先发查询动作块：

```sb-action
{"action":"create_task","title":"..."}
```

规则：独立 fenced code block、语言标注 sb-action、内容为单个 JSON 对象、无注释、每轮最多一个（长任务模式内除外）。动作执行后系统自动回报结果，基于回报数据回答，禁止编造。

## Newton 长任务块格式（v0.5.0+）

多步任务先发计划、后发完成声明（均独立 fenced block，JSON 同动作块纪律）：

```sb-plan
{"steps":[{"text":"统计逾期任务","tool":"count_tasks"},{"text":"整理成清单"}]}
```

```sb-done
{"items":["live:0","live:2"]}
```

规则：steps 2–8 条、text ≤60 字是可验证步骤；tool 只填六个动作名之一；绑定动作的步骤由系统在其动作执行成功后打勾；无绑定动作的纯综合步骤（如"整理成清单"）把成果写进回复、随 sb-done 一并声明即被勾掉；声明 items 引用已打勾或无绑定动作的 id，空声明无效；受阻时如实说明并继续其余步骤，禁止虚报完成。

## 修改本卡

新增/变更操作时四处同步：本卡 + AGENTS.md §5 + scripts/sb.py + Newton `src/actions.ts`。
