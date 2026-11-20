#!/usr/bin/env python3
"""提醒 Agent：扫描逾期与今日到期的开放任务。确定性，无 LLM。

逾期口径：due 一律当真——字段有值即真截止（v0.10.3 起 capture_task /
Newton 不再播种创建日假 due，没说截止就留空）。status=paused 的搁置
任务不扫。

输出约定：stdout 恰好一行摘要（供 osascript 通知使用）；
无命中时不输出。退出码：0=无命中，1=有提醒，2+=执行失败。
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sb import parse_fm  # noqa: E402

OPEN = {"todo", "in-progress"}


def scan(root: Path, today: dt.date) -> tuple[list[str], list[str]]:
    overdue: list[str] = []
    due_today: list[str] = []
    for p in sorted((root / "06 Tasks").rglob("*.md")):
        try:
            fm = parse_fm(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if str(fm.get("type", "")) != "task":
            continue
        if str(fm.get("status", "")) not in OPEN:
            continue
        if str(fm.get("archived", "")).lower() == "true":
            continue
        due = str(fm.get("due", "") or "")
        if not due:
            continue
        due10 = due[:10]
        title = str(fm.get("title", "") or p.stem)
        if due10 < today.isoformat():
            overdue.append(f"{title}（{due}）")
        elif due10 == today.isoformat():
            due_today.append(title)
    return overdue, due_today


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    overdue, due_today = scan(root, dt.date.today())
    if not overdue and not due_today:
        return 0
    parts: list[str] = []
    if overdue:
        names = "、".join(overdue[:4]) + ("…" if len(overdue) > 4 else "")
        parts.append(f"逾期 {len(overdue)} 项：{names}")
    if due_today:
        names = "、".join(due_today[:3]) + ("…" if len(due_today) > 3 else "")
        parts.append(f"今日到期 {len(due_today)} 项：{names}")
    print("；".join(parts) + "。")
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:  # 未捕获异常不得与 rc=1（有提醒）撞码
        print(f"check_reminders 崩溃: {e}", file=sys.stderr)
        raise SystemExit(2) from e
