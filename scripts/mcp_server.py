#!/usr/bin/env python3
"""SecondBrain MCP Server —— Agent 原生网关.

把 AGENTS.md §0 的行为守则（幂等 / 写前读 / 校验闭环 + 自动回滚）封装为
MCP 工具。服务端只操作自身所在的 vault（启动时固定），不暴露 vault 参数
（避免路径穿越）。写入失败会抛 CardError 并转为错误文本返回，文件已回滚。

启动:
    uv run scripts/mcp_server.py

客户端注册（Claude Code 示例，在 vault 根执行）:
    claude mcp add secondbrain -- uv run scripts/mcp_server.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer

VAULT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sb  # noqa: E402
import validate_cards  # noqa: E402

mcp = MCPServer(name="secondbrain", instructions=(
    "SecondBrain vault 操作网关。写入工具内置幂等、契约校验与自动回滚"
    "（0 ERROR 才算成功，失败时文件已恢复原状）。卡片 schema 见 vault 根 AGENTS.md。"))


def guarded(fn, *a, **kw) -> str:
    try:
        return fn(*a, **kw)
    except sb.CardError as e:
        return f"[ERROR·已回滚] {e}"
    except Exception as e:  # IO/权限等意外错误也不让网关进程崩
        return f"[ERROR] {type(e).__name__}: {e}"


@mcp.tool()
def capture_task(title: str, due: str | None = None,
                 priority: str = "medium", area: str = "",
                 project: str = "", topic: str = "", owner: str = "",
                 collaborators: list[str] | None = None) -> str:
    """捕获一个任务到 06 Tasks/YYYY/MM/（status: todo）。重复标题同日拒绝重建。

    Args:
        title: 任务标题（路径分隔符/引号会被安全化）
        due: 截止日 YYYY-MM-DD（可选 HH:MM）；用户没说截止就不传——due 一律当真，留空比假日期好
        priority: urgent|high|medium|low
        area: 关联领域 wikilink，如 "[[📂 技术]]"
        project: 关联项目 wikilink
        topic: 关联主题卡 wikilink
        owner: 负责人（👤 联系人卡名，可不带前缀只说人名；委托他人时才填；空 = 自己——GTD waiting-for，非空即等待中）
        collaborators: 参与人列表（共同完成，非交办）
    """
    return guarded(sb.capture_task, VAULT, title, due, priority, area, project,
                   None, topic, owner, collaborators)


@mcp.tool()
def complete_task(query: str) -> str:
    """完成任务（status→done 且补 completedAt）。已完成的任务幂等跳过。

    Args:
        query: 任务文件名/标题的独有片段
    """
    return guarded(sb.complete_task, VAULT, query)


@mcp.tool()
def checkin_habit(query: str, date: str | None = None) -> str:
    """习惯打卡（checkins 追加日期）。同日重复打卡幂等跳过。

    Args:
        query: 习惯文件名/标题的独有片段
        date: YYYY-MM-DD，缺省为今天（可补卡）
    """
    return guarded(sb.checkin_habit, VAULT, query, date)


@mcp.tool()
def inbox() -> str:
    """列出无 area/project/topic 关联的未完成任务（待归档 Inbox）。"""
    return sb.list_inbox(VAULT)


@mcp.tool()
def validate() -> str:
    """运行契约校验，返回逐条结果与统计行（ERROR/WARN 前缀）。"""
    ok, msg = sb.run_validation(VAULT)
    return msg


def iter_cards():
    """只遍历内容卡片，排除模板/配置/内部目录（与校验器同一套规则）。"""
    for p in VAULT.rglob("*.md"):
        parts = p.relative_to(VAULT).parts
        if parts[0] in validate_cards.SKIP_DIRS or p.name in validate_cards.SKIP_FILES:
            continue
        if any(seg in validate_cards.SKIP_DIRS for seg in parts[:-1]):
            continue
        yield p


@mcp.tool()
def search_cards(query: str, ctype: str | None = None) -> str:
    """按标题/文件名子串搜索卡片，可按 type 过滤。返回 JSON 列表（path/title/type/status）。

    Args:
        query: 文件名子串（不区分大小写）
        ctype: 可选，限定卡片 type（task/goal/habit/...）
    """
    q = query.lower()
    hits = []
    for p in iter_cards():
        if q in p.stem.lower():
            fm = sb.parse_fm(p.read_text(encoding="utf-8"))
            t = fm.get("type")
            if ctype and t != ctype:
                continue
            hits.append({"path": str(p.relative_to(VAULT)), "type": t,
                         "title": fm.get("title") or fm.get("name") or p.stem,
                         "status": fm.get("status")})
    return json.dumps(hits, ensure_ascii=False, indent=1)


@mcp.tool()
def today_brief() -> str:
    """今日简报：到期/逾期任务、今日完成、今日会议、习惯打卡状态。"""
    d = dt.date.today().isoformat()
    tasks, meetings, habits = [], [], []
    focus = 0
    open_now = 0
    for p in iter_cards():
        fm = sb.parse_fm(p.read_text(encoding="utf-8"))
        t = fm.get("type")
        if t == "task":
            # 进行中未结算段：按当下时刻折算，不写回卡片（结算以离开 in-progress 为准）
            raw_as = fm.get("activeSince")
            as_ = raw_as.strftime("%Y-%m-%d %H:%M") if isinstance(raw_as, dt.datetime) else str(raw_as or "")
            if str(fm.get("status")) == "in-progress" and sb.valid_stamp(as_) and as_[:10] == d:
                elapsed = (dt.datetime.now() - dt.datetime.strptime(as_, "%Y-%m-%d %H:%M")).total_seconds() / 60
                open_now += min(max(int(elapsed), 0), 24 * 60)
            # 与 check_reminders/Newton 同口径：due 一律当真（v3.12.3 起 capture 不播种假 due）；paused 搁置不计
            raw = fm.get("due")
            ds = raw.isoformat() if isinstance(raw, dt.date) else str(raw or "")
            eff = ds[:10]
            st = str(fm.get("status"))
            if st in ("todo", "in-progress") and eff and eff <= d:
                tasks.append((eff, p.stem, "逾期" if eff < d else "今日到期"))
            elif st == "done" and str(fm.get("completedAt", "")).startswith(d):
                tasks.append((d, p.stem, "今日完成"))
            # 今日投入：sessions 按起始日归属（跨零点段整体记起始日）
            sess = fm.get("sessions")
            for e in (sess if isinstance(sess, list) else []):
                es = str(e)
                if es[:10] == d:
                    focus += sb.session_minutes(es)
        elif t == "meeting" and str(fm.get("date")) == d \
                and str(fm.get("status")) == "scheduled":
            meetings.append(f"{fm.get('time', '')} {p.stem}")
        elif t == "habit":
            cis = fm.get("checkins")
            cis = [str(c) for c in cis] if isinstance(cis, list) else []
            habits.append(f"{'✅' if d in cis else '⬜'} {p.stem}")
    out = [f"## {d} 简报", "### 任务"]
    out += [f"- [{tag}] {name} (due {due})" for due, name, tag in sorted(tasks)] or ["- 无"]
    if focus or open_now:
        out.append(f"（今日投入 {sb.fmt_dur(focus)}"
                   + (f"，另有进行中 {sb.fmt_dur(open_now)} 未结算" if open_now else "") + "）")
    out.append("### 会议")
    out += [f"- {m}" for m in meetings] or ["- 无"]
    out.append("### 习惯")
    out += [f"- {h}" for h in habits] or ["- 无"]
    return "\n".join(out)


if __name__ == "__main__":
    mcp.run()
