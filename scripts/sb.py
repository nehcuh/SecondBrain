#!/usr/bin/env python3
"""SecondBrain Agent 操作 CLI —— 幂等卡片操作。

用法:
    uv run scripts/sb.py capture_task "标题" [--due YYYY-MM-DD（默认当日）] [--priority high] \
        [--area "[[📂 X]]"] [--project "[[🚀 Y]]"] [--source "🤝 会议_2026-10-08"]
    uv run scripts/sb.py complete_task "标题或路径片段"
    uv run scripts/sb.py set_field "标题片段" field value [--type meeting]
    uv run scripts/sb.py checkin_habit "习惯名片段" [--date YYYY-MM-DD]
    uv run scripts/sb.py inbox
    uv run scripts/sb.py validate

设计约束（对应 AGENTS.md §0）:
- 写前必读：所有写入前先解析现有 frontmatter
- 幂等：重复完成/重复打卡为 no-op 并明示
- 校验闭环 + 自动回滚：写入后自动校验，非 0 ERROR 即恢复原文件内容
- 原子写：临时文件 + os.replace，避免半成品落盘
- 纯库函数：不 print、不 sys.exit、不改全局状态（并发安全，供 MCP 复用）
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

import yaml

VAULT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_cards  # noqa: E402


class CardError(Exception):
    """写入失败（已回滚）或输入非法。message 面向调用方展示。"""


def today() -> dt.date:
    return dt.date.today()


def sanitize_stem(title: str) -> str:
    """文件名安全化：去路径分隔符/换行/引号/平台非法字符。"""
    s = re.sub(r'[/\\\n\r\t":*?|<>]+', "-", title.strip())
    s = re.sub(r"\s+", " ", s)
    return s.strip(" -") or "未命名任务"


def parse_fm(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}
    fm = yaml.safe_load("\n".join(lines[1:idx]))
    return fm if isinstance(fm, dict) else {}


def split_fm(text: str) -> tuple[list[str], list[str], list[str]]:
    """返回 (前置定界行, frontmatter 行, 含尾定界符及其后的行)。"""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return [], [], lines
    idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    return lines[:1], lines[1:idx], lines[idx:]


def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def run_validation(root: Path) -> tuple[bool, str]:
    f = validate_cards.validate(root)
    lines = [f"{sev}  {file}  {msg}" for sev, file, msg in f.items]
    lines.append(f"校验: {f.errors} ERROR / {f.warns} WARN")
    return (f.errors == 0, "\n".join(lines))


def write_card(path: Path, root: Path, mutate) -> str:
    """手术式修改 frontmatter；写后校验，失败自动恢复原内容。"""
    original = path.read_text(encoding="utf-8")
    pre, fm, body = split_fm(original)
    fm = mutate(fm, parse_fm(original))
    atomic_write(path, "".join(pre + fm + body))
    ok, msg = run_validation(root)
    if not ok:
        atomic_write(path, original)
        raise CardError(f"写入未通过契约校验，已回滚 {path.name}:\n{msg}")
    return msg


def set_field(fm_lines: list[str], field: str, value: str) -> list[str]:
    """设置单值标量字段（存在则替换，不存在则追加）。仅用于标量字段。"""
    pat = re.compile(rf"^{re.escape(field)}:[ \t].*$|^{re.escape(field)}:$")
    for i, ln in enumerate(fm_lines):
        if pat.match(ln):
            fm_lines[i] = f"{field}: {value}\n"
            return fm_lines
    fm_lines.append(f"{field}: {value}\n")
    return fm_lines


def replace_checkins(fm_lines: list[str], dates: list[str]) -> list[str]:
    """整体重建 checkins 块，兼容行内数组 / 空数组 / 标量 / 块列表。"""
    block = ["checkins:\n"] + [f"  - {d}\n" for d in dates]
    ci = re.compile(r"^checkins:")
    for i, ln in enumerate(fm_lines):
        if not ci.match(ln):
            continue
        j = i + 1
        # 吃掉行内残留值之后的所有既有列表项（含零缩进：YAML 允许与键同级的 - 项）
        while j < len(fm_lines) and re.match(r"^\s*-\s", fm_lines[j]):
            j += 1
        return fm_lines[:i] + block + fm_lines[j:]
    if not fm_lines:
        return block
    if not fm_lines[-1].endswith("\n"):
        fm_lines[-1] += "\n"
    return fm_lines + block


DEAD_FIELDS = ("energy", "assignee", "duration", "context", "actionable",
               "delegate", "scheduled")


def yaml_scalar(v: str) -> str:
    """标量转 YAML 文本：wikilink 等特殊起始必须加引号，防 flow 序列误解析；
    带时刻的 datetime 值也加引号——防 Obsidian 缓存/其他解析器收成日期对象。"""
    if (v.startswith("[") or v.startswith("{") or any(c in v for c in ":#\"'")
            or re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", v)):
        return '"' + v.replace('"', "'") + '"'
    return v


SESSION_STAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2} ([01]\d|2[0-3]):[0-5]\d$")
SESSION_ENTRY_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} ([01]\d|2[0-3]):[0-5]\d)"
    r" ~ (\d{4}-\d{2}-\d{2} ([01]\d|2[0-3]):[0-5]\d)$")


def valid_stamp(s: str) -> bool:
    """格式合法且日历真实（2026-02-31 这类溢出日期 strptime 抛 ValueError，即非法）。"""
    if not SESSION_STAMP_RE.match(s):
        return False
    try:
        dt.datetime.strptime(s, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def append_session(fm_lines: list[str], entry: str) -> list[str]:
    """sessions 块追加一条（块缺失则新建）；条目恒加引号防日期解析歧义。
    任意残值形态（单行/多行 flow、标量、>/| 折叠块）先归一成块列表——
    flow 序列后面接块条目是非法 YAML，会整卡丢 frontmatter。
    全部条目格式合法时按起始时间排序（补录昨天不再留乱序 WARN）。"""

    def unq(s: str) -> str:
        return s.strip().strip("\"'")

    out = list(fm_lines)
    for i, ln in enumerate(out):
        if not ln.startswith("sessions:"):
            continue
        j = i + 1
        items: list[str] = []
        inline_val = ln[len("sessions:"):].strip()
        if inline_val.startswith("["):
            items = [s for s in (unq(x) for x in re.sub(r"^\[|\]$", "", inline_val).split(",")) if s]
            if not inline_val.endswith("]"):
                for k in range(j, len(out)):
                    t = out[k].strip()
                    if not out[k][:1].isspace() and t != "]":
                        break  # 未闭合 flow 遇顶格键：按已收条目收尾
                    j = k + 1
                    if t == "]":
                        break
                    items.extend(s for s in (unq(x) for x in t.rstrip("]").split(",")) if s)
                    if t.endswith("]"):
                        break
        elif re.match(r"^[>|]", inline_val):
            for k in range(j, len(out)):
                if not re.match(r"^\s+\S", out[k]):
                    break
                if unq(out[k]):
                    items.append(unq(out[k]))
                j = k + 1
        elif inline_val and not inline_val.startswith("#"):
            items = [unq(inline_val)]
        while j < len(out) and re.match(r"^\s*-\s", out[j]):
            it = unq(re.sub(r"^\s*-\s*", "", out[j]))
            if it:
                items.append(it)
            j += 1
        items.append(entry)
        if all(SESSION_ENTRY_RE.match(e) for e in items):
            items.sort(key=lambda e: e[:16])
        block = ["sessions:\n"] + [f'  - "{e}"\n' for e in items]
        return out[:i] + block + out[j:]
    if out and not out[-1].endswith("\n"):
        out[-1] += "\n"
    out.append("sessions:\n")
    out.append(f'  - "{entry}"\n')
    return out


def session_minutes(entry: str) -> int:
    """sessions 条目时长（分钟）；格式或日历非法、止早于起返回 0
    （不抛——整库统计不能被一张手改坏卡炸掉）。"""
    m = SESSION_ENTRY_RE.match(str(entry).strip())
    if not m:
        return 0
    try:
        t0 = dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M")
        t1 = dt.datetime.strptime(m.group(3), "%Y-%m-%d %H:%M")
    except ValueError:
        return 0
    return max(0, int((t1 - t0).total_seconds() // 60))


def fmt_dur(m: int) -> str:
    """分钟 → 「2h15m / 40m」紧凑时长（与 Newton report.fmtDur 同形）。"""
    if m < 60:
        return f"{m}m"
    return f"{m // 60}h" + (f"{m % 60}m" if m % 60 else "")


def replace_tags(fm_lines: list[str], tags: list[str], field: str = "tags") -> list[str]:
    items = ", ".join(re.sub(r"[][,:\"']", "", t).strip() for t in tags)
    line = f"{field}: [{items}]\n"
    for i, ln in enumerate(fm_lines):
        if re.match(rf"^{field}:", ln):
            j = i + 1
            while j < len(fm_lines) and re.match(r"^\s*-\s", fm_lines[j]):
                j += 1
            return fm_lines[:i] + [line] + fm_lines[j:]
    if fm_lines and not fm_lines[-1].endswith("\n"):
        fm_lines[-1] += "\n"
    return fm_lines + [line]


def icon_ok(v: str) -> bool:
    """单个内容相关 emoji（允许 ZWJ 组合/肤色/旗帜）；拒绝文字与类型标记。与 validate_cards.py 同源。"""
    s = v.strip()
    if not s or re.search(r"[\w\s]", s):
        return False
    if any(m in s for m in "\U0001F4C2\U0001F680\U0001F3AF\U0001F4D3\U0001F4A1\U0001F4CC\U0001F4CE"):
        return False
    segs = re.sub("[\ufe0f\U0001F3FB-\U0001F3FF\u20e3]", "", s).split("\u200d")
    if not 1 <= len(segs) <= 4:
        return False
    def seg(sg: str) -> bool:
        if len(sg) == 1:
            return ord(sg) >= 0x2100
        if len(sg) == 2:
            return all(0x1F1E6 <= ord(c) <= 0x1F1FF for c in sg)
        return False
    return all(map(seg, segs))


def enrich_card(root: Path, query: str, ctype: str, area: str | None,
                project: str | None, priority: str | None, tags: list[str] | None,
                strip_dead: bool, force: bool, icon: str | None = None,
                owner: str | None = None,
                collaborators: list[str] | None = None) -> str:
    """AI 分诊写入路径：手术式补全 area/project/priority/tags/owner/collaborators。

    幂等保护：字段已有非空值且与新值不同 → 跳过该字段（--force 覆盖），
    不覆盖用户手填值。写入走 write_card：校验失败自动回滚。
    owner/collaborators 仅任务卡：owner 受控词表（👤 联系人卡，可只说人名）；
    collaborators 人名数组与既有值合并去重（attendees 同款）。
    """
    p = pick_one(find_cards(root, query, ctype), "卡片", root)
    fm = parse_fm(p.read_text(encoding="utf-8"))
    changes: list[str] = []
    skipped: list[str] = []

    if icon is not None and not icon_ok(icon):
        raise CardError("icon 应为单个内容相关 emoji（勿用文字/类型标记 📂🚀🎯📓💡📌📎）")
    owner_link: str | None = None
    collab_merge: list[str] | None = None
    if owner is not None:
        if str(fm.get("type", "")) != "task":
            raise CardError("owner 字段仅任务卡支持")
        plain = lambda s: re.sub(r"^\W+", "", s.strip())
        contacts = {plain(cp.stem): cp.stem
                    for cp in (root / "05 Notes/Contacts").rglob("*.md")
                    if str(parse_fm(cp.read_text(encoding="utf-8")).get("type", "")) == "contact"}
        o = owner.strip().removeprefix("[[").removesuffix("]]")
        if plain(o) not in contacts:
            raise CardError(f"--owner 不在联系人词表: {owner!r}。"
                            f"现有: {', '.join(contacts.values()) or '（无）'}")
        owner_link = f"[[{contacts[plain(o)]}]]"
    if collaborators:
        if str(fm.get("type", "")) != "task":
            raise CardError("collaborators 字段仅任务卡支持")
        existing = [str(c).strip() for c in (fm.get("collaborators") or []) if str(c).strip()]
        incoming = [re.sub(r"^\[\[|\]\]$", "", str(c)).strip() for c in collaborators]
        merged = list(dict.fromkeys(existing + [c for c in incoming if c]))
        if merged != existing:
            collab_merge = merged
    planned = [("area", area), ("project", project), ("priority", priority),
               ("icon", icon), ("owner", owner_link)]
    todo = [(f, v) for f, v in planned if v is not None]
    tags_differs = tags is not None and [str(t) for t in (fm.get("tags") or [])] != tags
    has_dead = strip_dead and any(re.match(rf"^{f}:", ln) for ln in
                                  split_fm(p.read_text(encoding="utf-8"))[1]
                                  for f in DEAD_FIELDS)
    if not todo and not tags_differs and not has_dead and collab_merge is None:
        return f"无变更: {p.relative_to(root)}"

    def mutate(fm_lines, _):
        if strip_dead:
            pat = re.compile(r"^(" + "|".join(DEAD_FIELDS) + r"):")
            fm_lines = [ln for ln in fm_lines if not pat.match(ln)]
        for field, val in todo:
            cur = fm.get(field)
            cur_s = "" if cur is None else str(cur)
            if cur_s == val:
                continue
            if cur_s and not force:
                skipped.append(f"{field}={cur_s!r} 已有值，保留")
                continue
            fm_lines = set_field(fm_lines, field, yaml_scalar(val))
            changes.append(f"{field}: {cur_s or '∅'} → {val}")
        if tags_differs:
            fm_lines = replace_tags(fm_lines, list(tags))
            changes.append(f"tags: {fm.get('tags')} → {tags}")
        if collab_merge is not None:
            fm_lines = replace_tags(fm_lines, collab_merge, field="collaborators")
            changes.append(f"collaborators: {fm.get('collaborators')} → {collab_merge}")
        return fm_lines

    msg = write_card(p, root, mutate)
    report = [f"enrich: {p.relative_to(root)}"]
    report += [f"  {c}" for c in changes] + [f"  跳过 {s}" for s in skipped]
    report.append(msg)
    return "\n".join(report)


def iter_card_files(root: Path):
    """库内 md 卡遍历：跳过顶层隐藏目录（.venv/.obsidian/.git 等，防全库读盘）。"""
    for d in root.iterdir():
        if not d.name.startswith("."):
            if d.is_dir():
                yield from d.rglob("*.md")
            elif d.suffix == ".md":
                yield d


def find_cards(root: Path, query: str, ctype: str) -> list[Path]:
    q = query.lower()
    hits = []
    for p in iter_card_files(root):
        if q in p.stem.lower():
            fm = parse_fm(p.read_text(encoding="utf-8"))
            if fm.get("type") == ctype:
                hits.append(p)
    return hits


def pick_one(hits: list[Path], what: str, root: Path) -> Path:
    if not hits:
        raise CardError(f"未找到匹配的{what}")
    if len(hits) > 1:
        cands = "\n".join(f"候选: {h.relative_to(root)}" for h in hits)
        raise CardError(f"匹配到 {len(hits)} 个，请细化关键词:\n{cands}")
    return hits[0]


def capture_task(root: Path, title: str, due: str | None, priority: str,
                 area: str, project: str, source: str | None = None,
                 topic: str = "", owner: str = "",
                 collaborators: list[str] | None = None) -> str:
    if due and not re.match(r"^\d{4}-\d{2}-\d{2}( ([01]\d|2[0-3]):[0-5]\d)?$", due):
        raise CardError(f"due 格式非法: {due!r}（应为 YYYY-MM-DD，可选 HH:MM）")
    # owner 受控词表：只能引用现有 👤 联系人卡（GTD waiting-for，空 = 自己）。
    # 卡名带 👤 装饰前缀而人只说人名：按去前缀纯名匹配，落盘 wikilink 用完整卡名。
    owner_link = ""
    if owner:
        o = owner.strip().removeprefix("[[").removesuffix("]]")
        plain = lambda s: re.sub(r"^\W+", "", s.strip())
        contacts = {plain(p.stem): p.stem
                    for p in (root / "05 Notes/Contacts").rglob("*.md")
                    if str(parse_fm(p.read_text(encoding="utf-8")).get("type", "")) == "contact"}
        if plain(o) not in contacts:
            raise CardError(f"--owner 不在联系人词表: {owner!r}。"
                            f"现有: {', '.join(contacts.values()) or '（无）'}")
        owner_link = f"[[{contacts[plain(o)]}]]"
    t = today()
    month_dir = root / "06 Tasks" / f"{t.year}" / f"{t.month:02d}"
    month_dir.mkdir(parents=True, exist_ok=True)
    stem = sanitize_stem(title)
    # 全局同名查重：存在未完成的同名任务即拒绝（跨月/跨年也算）
    for p in (root / "06 Tasks").rglob("*.md"):
        if not p.stem.startswith(stem + "_"):
            continue
        fm0 = parse_fm(p.read_text(encoding="utf-8"))
        if fm0.get("type") == "task" and fm0.get("status") != "done":
            raise CardError(f"同名任务未完成，拒绝重复创建:\n  {p.relative_to(root)}\n"
                            f"（先完成它，或换标题）")
    path = month_dir / f"{stem}_{t.month:02d}{t.day:02d}.md"
    if path.exists():
        return f"已存在: {path.relative_to(root)}（拒绝重复创建）"
    src_link = ""
    if source:
        s = source.strip().removeprefix("[[").removesuffix("]]")
        hits = [p for p in iter_card_files(root) if p.stem == Path(s).stem]
        if not hits:
            raise CardError(f"--source 无法解析: {source!r}（须为库内完整卡名 stem）")
        if len(hits) > 1:
            cands = "\n".join(f"  候选: {h.relative_to(root)}" for h in hits)
            raise CardError(f"--source 匹配到 {len(hits)} 张同名卡:\n{cands}")
        src_link = f"[[{hits[0].stem}]]"
    fm = {
        "type": "task",
        "title": stem,
        "status": "todo",
        "priority": priority,
        # v3.12.5：未指定 due 默认播种当日（用户拍板——新建当天首页可见，未完成次日进逾期属预期）
        "due": due or t.isoformat(),
        "area": area,
        "project": project,
        "topic": topic,
        "source": src_link,
        "owner": owner_link,
        "collaborators": [str(c).strip() for c in (collaborators or []) if str(c).strip()],
        "tags": ["task"],
        "createdAt": f"{t.isoformat()}T{dt.datetime.now().strftime('%H:%M')}",
        "completedAt": "",
        "archived": False,
    }
    # yaml.safe_dump 负责全部转义（引号/冒号/emoji），杜绝标题注入
    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True,
                             default_flow_style=False).rstrip("\n")
    body = f"\n# {stem}\n"
    atomic_write(path, f"---\n{fm_text}\n---\n{body}")
    ok, msg = run_validation(root)
    if not ok:
        path.unlink(missing_ok=True)
        raise CardError(f"新建卡片未通过契约校验，已删除 {path.name}:\n{msg}")
    return f"创建: {path.relative_to(root)}\n{msg}"


def complete_task(root: Path, query: str) -> str:
    p = pick_one(find_cards(root / "06 Tasks", query, "task"), "任务", root)
    fm = parse_fm(p.read_text(encoding="utf-8"))
    if fm.get("status") == "done" and fm.get("completedAt"):
        return f"幂等跳过: 已完成于 {fm.get('completedAt')}"
    stamp = f"{today().isoformat()} {dt.datetime.now().strftime('%H:%M')}"
    # 投入结算：未结工作段落一条 session（<1 分钟丢弃），再清 activeSince
    active = fm.get("activeSince")
    if isinstance(active, dt.datetime):
        active = active.strftime("%Y-%m-%d %H:%M")
    else:
        active = str(active or "")
    # 畸形 activeSince 也一并清除（防 done 卡残留触发校验 WARN），仅合法值结算成条目
    has_active = bool(active)
    settled = has_active and valid_stamp(active) and stamp > active

    def mutate(fm_lines, _):
        fm_lines = set_field(fm_lines, "status", "done")
        fm_lines = set_field(fm_lines, "completedAt", yaml_scalar(stamp))
        if has_active:
            if settled:
                fm_lines = append_session(fm_lines, f"{active} ~ {stamp}")
            fm_lines = [ln for ln in fm_lines if not ln.startswith("activeSince:")]
        return fm_lines

    if settled:
        tail = "（投入段已结算进 sessions）"
    elif has_active and valid_stamp(active):
        tail = "（activeSince 已清除，时段不足一分钟未记 session）"
    elif has_active:
        tail = f"（activeSince={active} 值非法已清除，未记 session）"
    else:
        tail = ""
    return f"完成: {p.relative_to(root)}{tail}\n" + write_card(p, root, mutate)


def checkin_habit(root: Path, query: str, date: str | None, note: str | None = None) -> str:
    d = date or today().isoformat()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
        raise CardError(f"date 格式非法: {d!r}（应为 YYYY-MM-DD）")
    p = pick_one(find_cards(root / "07 Habits", query, "habit"), "习惯", root)
    fm = parse_fm(p.read_text(encoding="utf-8"))
    cis = fm.get("checkins")
    if cis is None:
        cis = []
    elif not isinstance(cis, list):
        cis = [str(cis)]  # 标量归一化为列表（契约要求列表）
    cis = [str(c) for c in cis if str(c).strip()]
    raw_notes = fm.get("checkin_notes")
    # 键归一化：未加引号的日期键会被 pyyaml 解析成 date 对象，统一转 ISO 字符串
    notes = ({k.isoformat() if isinstance(k, dt.date) else str(k): v
              for k, v in raw_notes.items()}
             if isinstance(raw_notes, dict) else {})
    clean = (note or "").strip()[:200]
    if d in cis:
        if clean and d not in notes:
            def add_note(fm_lines, _):
                return replace_checkin_notes(fm_lines, {**notes, d: clean})
            return f"补注记: {p.stem} {d}\n" + write_card(p, root, add_note)
        tail = "" if (d in notes or fm.get("evidence") is not True) else "（可用 --note 补注记）"
        return f"幂等跳过: {p.stem} 已于 {d} 打卡{tail}"

    def mutate(fm_lines, _):
        lines = replace_checkins(fm_lines, cis + [d])
        if clean:
            lines = replace_checkin_notes(lines, {**notes, d: clean})
        return lines

    tail = "" if clean else ("（待补注 --note）" if fm.get("evidence") is True else "")
    return f"打卡: {p.stem} -> {d}{tail}\n" + write_card(p, root, mutate)


def replace_checkin_notes(fm_lines: list[str], notes: dict[str, str]) -> list[str]:
    """整块重写 checkin_notes 映射（日期 -> 文本），键按日期排序。与 contract.ts setCheckinNotes 同源。"""
    # 日期键一律加引号：不加引号会被 YAML 解析成 date 对象（Obsidian/pyyaml 同病）
    block = ["checkin_notes:\n"] + [f'  "{k}": {yaml_scalar(v)}\n' for k, v in sorted(notes.items())]
    out = list(fm_lines)
    for i, ln in enumerate(out):
        if ln.startswith("checkin_notes:"):
            j = i + 1
            while j < len(out) and re.match(r"^ {2}\S", out[j]):
                j += 1
            out[i:j] = block
            return out
    if out and not out[-1].endswith("\n"):
        out[-1] += "\n"
    return out + block


def set_card_field(root: Path, query: str, field: str, value: str, ctype: str) -> str:
    """通用标量字段写入（如 meeting.minedAt）。校验失败自动回滚。"""
    if not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", field):
        raise CardError(f"字段名非法: {field!r}")
    p = pick_one(find_cards(root, query, ctype), "卡片", root)

    def mutate(fm_lines, _):
        return set_field(fm_lines, field, yaml_scalar(value))

    msg = write_card(p, root, mutate)
    return f"set {field}: {p.relative_to(root)}\n{msg}"


def list_inbox(root: Path) -> str:
    rows = []
    for p in (root / "06 Tasks").rglob("*.md"):
        fm = parse_fm(p.read_text(encoding="utf-8"))
        if fm.get("type") != "task" or fm.get("status") == "done":
            continue
        if not fm.get("area") and not fm.get("project") and not fm.get("topic"):
            rows.append(f"{p.relative_to(root)}  due={fm.get('due', '?')}  "
                        f"priority={fm.get('priority', '?')}")
    return "\n".join(rows) if rows else "Inbox 清空"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture_task")
    c.add_argument("title")
    c.add_argument("--due")
    c.add_argument("--priority", default="medium",
                   choices=["urgent", "high", "medium", "low"])
    c.add_argument("--area", default="")
    c.add_argument("--project", default="")
    c.add_argument("--topic", default="", help="主题卡 wikilink（须为库内现有主题卡）")
    c.add_argument("--owner", help="负责人（👤 联系人卡名，可不带前缀只说人名；委托他人时才填，空 = 自己）")
    c.add_argument("--collaborators", nargs="+", default=[],
                   help="参与人（空格分隔多人，共同完成）")
    c.add_argument("--source", help="来源卡完整 stem（wikilink 可选包裹），创建时校验可解析")
    sub.add_parser("complete_task").add_argument("query")
    s = sub.add_parser("set_field", help="设置标量字段（如 minedAt）")
    s.add_argument("query")
    s.add_argument("field")
    s.add_argument("value")
    s.add_argument("--type", default="task")
    h = sub.add_parser("checkin_habit")
    h.add_argument("query")
    h.add_argument("--date")
    h.add_argument("--note", help="打卡注记：这次做了/看了什么（≤200 字）")
    sub.add_parser("inbox")
    sub.add_parser("validate")
    e = sub.add_parser("enrich_card", help="AI 分诊：补全 area/project/priority/tags")
    e.add_argument("query")
    e.add_argument("--type", default="task")
    e.add_argument("--area")
    e.add_argument("--project")
    e.add_argument("--priority", choices=["urgent", "high", "medium", "low"])
    e.add_argument("--tags", help="逗号分隔，整体替换（含基础标签）")
    e.add_argument("--icon", help="单个内容相关 emoji（勿用类型标记）")
    e.add_argument("--owner", help="负责人（👤 联系人卡名，可不带前缀只说人名；仅任务卡，非空即等待中）")
    e.add_argument("--collaborators", nargs="+",
                   help="参与人（空格分隔多人，与既有值合并去重；仅任务卡）")
    e.add_argument("--strip-dead", action="store_true",
                   help="顺带删除 energy/assignee/duration 残留")
    e.add_argument("--force", action="store_true", help="覆盖已有非空值")
    a = ap.parse_args()

    try:
        if a.cmd == "capture_task":
            print(capture_task(VAULT, a.title, a.due, a.priority, a.area,
                               a.project, a.source, a.topic, a.owner,
                               a.collaborators))
        elif a.cmd == "complete_task":
            print(complete_task(VAULT, a.query))
        elif a.cmd == "set_field":
            print(set_card_field(VAULT, a.query, a.field, a.value, a.type))
        elif a.cmd == "checkin_habit":
            print(checkin_habit(VAULT, a.query, a.date, a.note))
        elif a.cmd == "inbox":
            print(list_inbox(VAULT))
        elif a.cmd == "validate":
            ok, msg = run_validation(VAULT)
            print(msg)
            return 0 if ok else 1
        elif a.cmd == "enrich_card":
            print(enrich_card(VAULT, a.query, a.type, a.area, a.project,
                              a.priority, a.tags.split(",") if a.tags else None,
                              a.strip_dead, a.force, a.icon,
                              a.owner, a.collaborators))
    except CardError as e:
        print(f"[失败] {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
