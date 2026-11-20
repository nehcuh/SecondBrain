#!/usr/bin/env python3
"""SecondBrain 全局拓扑生成器 —— 重建 🗺️ Atlas.md。

用法:
    uv run scripts/gen_atlas.py

确定性脚本（无 AI 参与），供 sb-triage 技能 / launchd / 插件复用。
输出 mermaid 图（graph TD）：目标 → 领域 → 项目 → 任务簇（按计数聚合），
无 area/project/topic 关联的活跃任务汇入「📥 待分诊」节点；含逾期任务的簇标红。
"""
from __future__ import annotations

import datetime as dt
import os
import re
import tempfile
from pathlib import Path

import yaml

VAULT = Path(__file__).resolve().parent.parent
OUT = VAULT / "🗺️ Atlas.md"

GOAL_ACTIVE = {"active"}
PROJ_ACTIVE = {"planning", "active"}
TASK_OPEN = {"todo", "in-progress"}
STEM_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def fm_of(p: Path) -> dict:
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0].strip() != "---":
            return {}
        idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        v = yaml.safe_load("\n".join(lines[1:idx]))
        return v if isinstance(v, dict) else {}
    except (yaml.YAMLError, OSError, StopIteration):
        return {}


def wl_links(v) -> list[str]:
    """仅提取 [[wikilink]] 目标 stem（用于 area/project/goal 关联字段）。"""
    if isinstance(v, list):
        return [s for x in v for s in wl_links(x)]
    if not isinstance(v, str):
        return []
    return [t.strip().split("/")[-1] for t in STEM_RE.findall(v)]


def mlabel(name: str) -> str:
    """mermaid 节点标签安全化。"""
    s = name.replace('"', "'").replace("<", "‹").replace(">", "›")
    s = s.replace("#", "♯").replace("\n", " ")
    return s


def main() -> None:
    goals, areas, projects, tasks = [], [], [], []
    for p in (VAULT / "01 Goals").rglob("*.md"):
        fm = fm_of(p)
        if (fm.get("type") == "goal" and str(fm.get("status")) in GOAL_ACTIVE
                and not fm.get("archived")):
            goals.append({"stem": p.stem, "fm": fm})
    for p in (VAULT / "02 Areas").rglob("*.md"):
        fm = fm_of(p)
        if fm.get("type") == "area" and not fm.get("archived"):
            areas.append({"stem": p.stem, "fm": fm})
    for p in (VAULT / "03 Projects").rglob("*.md"):
        fm = fm_of(p)
        if (fm.get("type") == "project" and str(fm.get("status")) in PROJ_ACTIVE
                and not fm.get("archived")):
            projects.append({"stem": p.stem, "fm": fm})
    today = dt.date.today()
    for p in (VAULT / "06 Tasks").rglob("*.md"):
        fm = fm_of(p)
        if (fm.get("type") != "task" or str(fm.get("status")) not in TASK_OPEN
                or fm.get("archived")):
            continue
        # 逾期口径与 check_reminders/Newton 同步：due 一律当真（v0.10.3 起 capture 不播种假 due）
        raw = fm.get("due")
        ds = raw.isoformat() if isinstance(raw, dt.date) else str(raw or "")
        eff = ds[:10]
        tasks.append({"fm": fm, "overdue": bool(eff) and eff < today.isoformat()})

    area_stems = {a["stem"] for a in areas}
    proj_stems = {pr["stem"] for pr in projects}
    stem_by_name = {str(a["fm"].get("name", "")).strip(): a["stem"] for a in areas
                    if a["fm"].get("name")}

    # 任务按归属聚合；簇记录是否含逾期
    clusters: dict[tuple[str, str], int] = {}
    overdue_in: dict[tuple[str, str], int] = {}
    orphan = 0
    for t in tasks:
        area_l = [x for x in wl_links(t["fm"].get("area")) if x in area_stems]
        proj_l = [x for x in wl_links(t["fm"].get("project")) if x in proj_stems]
        key = (("project", proj_l[0]) if proj_l
               else ("area", area_l[0]) if area_l else None)
        if key is None:
            # 三关联口径与 Inbox 判定同步：仅 topic 关联的任务不算待分诊（不进簇也不进待分诊节点）
            if wl_links(t["fm"].get("topic")):
                continue
            orphan += 1
            continue
        clusters[key] = clusters.get(key, 0) + 1
        if t["overdue"]:
            overdue_in[key] = overdue_in.get(key, 0) + 1

    lines: list[str] = ["graph TD"]
    id_of: dict[str, str] = {}
    counter = 0

    def emit(node_key: str, text: str, cls: str) -> str:
        nonlocal counter
        counter += 1
        n = f"n{counter}"
        id_of[node_key] = n
        lines.append(f'    {n}["{mlabel(text)}"]:::{cls}')
        return n

    def resolve_area(ref: str) -> str | None:
        """领域引用：stem 直配或纯名 → stem（Area 卡 parent 存纯名）。"""
        if "a:" + ref in id_of:
            return "a:" + ref
        stem = stem_by_name.get(ref)
        if stem and "a:" + stem in id_of:
            return "a:" + stem
        return None

    for g in goals:
        emit("g:" + g["stem"], g["stem"], "goal")
    for a in areas:
        emit("a:" + a["stem"], a["stem"], "area")
    for pr in projects:
        emit("p:" + pr["stem"], pr["stem"], "proj")

    for g in goals:
        for parent in wl_links(g["fm"].get("parent")):
            if "g:" + parent in id_of:
                lines.append(f"    {id_of['g:' + g['stem']]} --- {id_of['g:' + parent]}")
    for a in areas:
        for parent in (wl_links(a["fm"].get("parent"))
                       + [str(a["fm"].get("parent", "")).strip()]
                       if a["fm"].get("parent") else []):
            src = resolve_area(parent)
            if src and src != "a:" + a["stem"]:
                lines.append(f"    {id_of[src]} --- {id_of['a:' + a['stem']]}")
    for pr in projects:
        for a in wl_links(pr["fm"].get("area")):
            src = resolve_area(a)
            if src:
                lines.append(f"    {id_of[src]} --> {id_of['p:' + pr['stem']]}")

    ci = 0
    for (kind, target), n in sorted(clusters.items()):
        ci += 1
        hot = overdue_in.get((kind, target), 0) > 0
        cls = "hot" if hot else "task"
        mark = " ⚠️逾期" if hot else ""
        tn = f"tc{ci}"
        lines.append(f'    {tn}["✅ 任务×{n}{mark}"]:::{cls}')
        src = id_of[("p:" if kind == "project" else "a:") + target]
        lines.append(f"    {src} --> {tn}")

    if orphan:
        lines.append(f'    INBOX["📥 待分诊 ×{orphan}"]:::hot')

    lines.append("    classDef goal fill:#2f6f4f,color:#fff;")
    lines.append("    classDef area fill:#3b5b8f,color:#fff;")
    lines.append("    classDef proj fill:#8f5b3b,color:#fff;")
    lines.append("    classDef task fill:#4a4a5a,color:#ccc;")
    lines.append("    classDef hot fill:#a03030,color:#fff;")

    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    overdue_n = sum(1 for t in tasks if t["overdue"])
    md = f"""---
generated: {now}
generator: scripts/gen_atlas.py
---

# 🗺️ Atlas — 全局拓扑

> ⚠️ 生成文件，勿手改。运行 `uv run scripts/gen_atlas.py` 或触发 AI 分诊（/sb-triage）时重建。
> 数据流：🎯 目标 → 📂 领域 → 🚀 项目 → ✅ 任务簇（聚合计数）。红色 = 含逾期任务的簇 / 活跃项目下游 / 待分诊积压。

## 拓扑

```mermaid
{chr(10).join(lines)}
```

## 体检摘要 · {now}

| 指标 | 值 |
|------|-----|
| 活跃目标 | {len(goals)} |
| 领域（含子领域） | {len(areas)} |
| 活跃项目 | {len(projects)} |
| 开放任务 | {len(tasks)}（逾期 {overdue_n}） |
| 待分诊（无领域/项目） | {orphan} |

"""
    fd, tmp = tempfile.mkstemp(dir=str(VAULT), suffix=".md.tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(md)
        os.replace(tmp, OUT)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    print(f"Atlas 重建完成: 活跃目标 {len(goals)} / 领域 {len(areas)} / "
          f"项目 {len(projects)} / 开放任务 {len(tasks)}（逾期 {overdue_n}）/ 待分诊 {orphan}")


if __name__ == "__main__":
    main()
