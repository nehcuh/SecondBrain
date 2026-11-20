---
name: sb-triage
description: SecondBrain 卡片 AI 分诊——为 Inbox/缺关联卡片自动补全 area/project/priority/tags，挖掘已完成会议的行动项建任务（minedAt 幂等门），重建 🗺️ Atlas 拓扑，输出变更报告并 git 提交。当用户说"分诊"、"整理 Inbox"、"sb-triage"或要求批量补全卡片属性时使用。
---

# sb-triage：AI 分诊

目标：把"快速捕获 → 空属性卡片"的整理负担从用户转移到 AI。写入策略为**直接写入 + 变更报告**（用户已确认），git 提交即回滚点。

## 步骤（严格按序）

1. **收集待分诊卡**
   - `uv run scripts/sb.py inbox` → 无 area/project 的开放任务
   - 补充扫描：`05 Notes/Meetings` 下 `area` 为空的会议卡；`05 Notes/Clip`（status=inbox）与 `05 Notes/Inspiration` 中 `area` 为空的卡
   - 全部为空 → 记"无待分诊卡"，仍跳到第 6 步（会议挖掘有自己的候选门，与分诊互不阻塞）

2. **加载受控词汇**
   - Area 词表 = `02 Areas` 下所有 `type: area` 且 **未归档**（archived ≠ true）的卡片 stem（含子领域）
   - Project 词表 = `03 Projects` 下所有 `type: project` 卡片 stem
   - area/project **只能引用现有卡片**（validator 会查断链）。语义不合任何子领域时用父领域；确需新领域/新项目时在报告中提出建议，经用户同意后先建卡再关联
   - **领域三测**（建议新领域前自检）：领域 = 持续经营的责任，须同时满足 ①无终点（有终点线的是项目）②有后果（荒废三个月有真实代价）③是角色（能填「我是自己人生中____的____」）。学习型兴趣主题（某技术/方法论/语言）不是领域——归 `05 Notes/Topics` 主题卡，不建领域

3. **逐卡推断**（读标题 + 正文，卡片通常是空骨架，标题即主信号）
   - `area`: `[[卡片stem]]`，从标题语义映射（例：课题/评审/汇报 → 工作；体重/跑步 → 健康）
   - `project`: 仅当明确属于某现有项目，宁缺毋滥
   - `priority`: 逾期已久或含外部依赖 → `high`；默认维持 `medium`
   - `tags`: 保留基础标签（task/meeting），追加语义标签，优先复用 vault 现有标签词汇
   - **不改**：status、due、scheduled、createdAt、completedAt 等事实字段；不动正文

4. **契约原生写入**（单卡短事务，禁止整段 YAML 重写）
   - 每卡一条命令：`uv run scripts/sb.py enrich_card <标题片段> --type <task|meeting|note> --area "[[📂 X]]" [--project …] [--priority …] --tags "基础标签,语义标签" [--icon 🛡️] --strip-dead`
   - enrich_card 走行级手术 + 写后校验失败自动回滚；已有非空值自动跳过（不覆盖用户手填）
   - note 类（clip/inspiration）需先确认 enrich_card 的 `--type note` 匹配唯一卡片，歧义时用完整标题

5. **校验闭环**：每批写完运行 `uv run scripts/validate_cards.py`，必须 **0 ERROR**；某卡引入 ERROR → 恢复该卡原文并在报告中标红

6. **会议行动项挖掘**（上限约束，宁缺毋滥）
   - 候选门：`05 Notes/Meetings` 下 `status=done` 且无 `minedAt`、`date` 在近 30 天内、正文无 `<!-- no-mine -->` 标记
   - 每晚最多挖 **3 张**（从 date 最旧开始）；行动项必须动词开头、有明确交付物——"讨论了/同步了/了解了"不算行动项
   - 建任务：`uv run scripts/sb.py capture_task "行动项" --due <仅明确死线才给> --source "🤝 会议完整stem" --area "<会议卡 area>"`；`--source` 校验失败或同名任务未完成被拒 → 跳过该条并在报告注明
   - 挖完必标记：`uv run scripts/sb.py set_field <会议标题片段> minedAt <今日日期> --type meeting`（即使挖出 0 条也标记，防重复扫描；这是幂等门）
   - 新任务 `priority` 一律 ≤ `medium`，不代用户拔高紧迫度

7. **重建拓扑**：`uv run scripts/gen_atlas.py`

8. **变更报告**（对话中输出，表格）：
   `卡片 | 字段 | 旧值 → 新值 | 判断依据 | 置信度(高/中/低)`
   会议挖掘单列小节：`会议 → 新建任务 [[链接]] 列表`（含拒绝原因）；低置信项明确提醒用户纠错；统计待分诊数变化

9. **提交回滚点**：`git add` 涉及卡片 + Atlas，commit 信息格式 `triage(cards): 分诊 N 张卡片补全 area/tags + 挖掘 M 条会议行动项`（无挖掘时省略后半）

## 纪律

- 幂等：已有非空 area/project 的卡跳过，不覆盖用户手填值
- 单文件短事务，一次会话内完成读写
- 报告先于提交展示；用户在场时先报告再提交
