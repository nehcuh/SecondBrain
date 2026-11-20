#!/usr/bin/env python3
"""SecondBrain 卡片契约校验器.

用法:
    uv run scripts/validate_cards.py [--root <vault_root>]

退出码: 0 = 无 ERROR; 1 = 存在 ERROR.
契约定义与 AGENTS.md v3 保持同步（单源在 AGENTS.md，本文件是其可执行化）。
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

import yaml

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}$")
SESSION_ENTRY_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} ([01]\d|2[0-3]):[0-5]\d)"
    r" ~ (\d{4}-\d{2}-\d{2} ([01]\d|2[0-3]):[0-5]\d)$")
NEST_RE = re.compile(r"\d{4}/\d{2}/\d{4}/\d{2}")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")

SKIP_DIRS = {".obsidian", ".vibe", ".git", ".trash", ".venv", "node_modules",
             "99 Templates", "99 Conflict", "scripts", "Excalidraw", "_assets",
             ".smart-env", ".githooks", ".claude"}
SKIP_FILES = {"README.md", "AGENTS.md", "CLAUDE.md", "MEMORY.md",
              "🏠 Home.md", "🗺️ Atlas.md"}

# 各类型的路径深度规范（root 下的相对层级，正则；None=仅检查 root）
PATH_PATTERNS: dict[str, str | None] = {
    "goal": r"^(\d{4}(/Q\d(/\d{2})?)?/)?[^/]+\.md$",
    "task": r"^\d{4}/\d{2}/[^/]+\.md$",
    "meeting": r"^\d{4}/\d{2}/[^/]+\.md$",
    "clip": r"^Clip/\d{4}/\d{2}/[^/]+\.md$",
    "learning": r"^Learning/\d{4}/\d{2}/[^/]+\.md$",
    "blog": r"^Blog/\d{6}/[^/]+/[^/]+\.md$",
    "journal:daily": r"^Daily/\d{4}/\d{2}/[^/]+\.md$",
    "journal:weekly": r"^Weekly/[^/]+\.md$",
    "journal:monthly": r"^Monthly/[^/]+\.md$",
}

TYPE_SPEC: dict[str, dict] = {
    "goal": dict(
        root="01 Goals", required=["level", "status"],
        enums={"level": {"annual", "quarterly", "monthly", "longterm"},
               "status": {"active", "completed", "abandoned"}},
        fmts={"progress": "number", "deadline": "date", "createdAt": "datetime"},
        emoji="🎯"),
    "area": dict(
        root="02 Areas", required=["name", "status"],
        enums={"status": {"active", "dormant"}},
        fmts={}, emoji="📂"),
    "project": dict(
        root="03 Projects", required=["name", "status"],
        enums={"status": {"planning", "active", "done", "archived"},
               "priority": {"high", "medium", "low"}},
        fmts={"deadline": "date", "progress": "number", "createdAt": "datetime"},
        emoji="🚀"),
    "task": dict(
        root="06 Tasks", required=["title", "status"],
        enums={"status": {"todo", "in-progress", "paused", "done"},
               "priority": {"urgent", "high", "medium", "low"}},
        fmts={"due": "datetime_or_date", "createdAt": "datetime",
              "completedAt": "datetime_or_date", "pausedAt": "datetime_or_date",
              "activeSince": "datetime"},
        emoji=None, mmdd=True),
    "habit": dict(
        root="07 Habits", required=["title", "frequency"],
        enums={"frequency": {"daily", "weekly"}},
        fmts={}, emoji="🔄", checkins=True),
    "meeting": dict(
        root="05 Notes/Meetings", required=["title", "status"],
        enums={"status": {"scheduled", "done", "cancelled"}},
        fmts={"date": "date", "time": "time", "createdAt": "datetime",
              "minedAt": "date"}, emoji="🤝"),
    "contact": dict(
        root="05 Notes/Contacts", required=["name"],
        enums={}, fmts={}, emoji="👤"),
    "topic": dict(
        root="05 Notes/Topics", required=["title", "status"],
        enums={"status": {"active", "done", "archived"}},
        fmts={"progress": "number"}, emoji="📓"),
    "journal": dict(
        root="05 Notes/Journal", required=["subtype"],
        enums={"subtype": {"daily", "weekly", "monthly"}},
        fmts={"date": "date"}, emoji=None),
}

NOTE_SPEC: dict[str, dict] = dict(
    root="05 Notes", required=["subtype"],
    fmts={"createdAt": "datetime", "updatedAt": "datetime"},
    subtype_enums={
        "clip": {"status": {"inbox", "processing", "archived"}},
        "inspiration": {"status": {"spark", "developing", "live", "planned", "archived"}},
        "knowledge": {"status": {"active", "superseded", "archived"}},
        "blog": {"status": {"draft", "published"}},
        "learning": {"status": {"reading", "done", "archived"}},
        "handbook": {"status": {"active", "archived"}},
    },
    subtype_emoji={"clip": "📎", "blog": "✍️", "inspiration": "💡",
                   "knowledge": "📌", "handbook": "📋", "learning": "📖"},
)

WIKILINK_FIELDS = {"area", "project", "goal", "parent", "topic", "owner"}

# 已退役任务字段（GTD 残留/只写不读，2026-11 元数据治理拍板）：出现即 WARN 提醒清理
RETIRED_TASK_FIELDS = ("scheduled", "energy", "assignee", "duration",
                       "context", "actionable", "delegate")


class Findings:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str]] = []  # (severity, file, message)

    def err(self, f: str, m: str) -> None:
        self.items.append(("ERROR", f, m))

    def warn(self, f: str, m: str) -> None:
        self.items.append(("WARN", f, m))

    @property
    def errors(self) -> int:
        return sum(1 for s, _, _ in self.items if s == "ERROR")

    @property
    def warns(self) -> int:
        return sum(1 for s, _, _ in self.items if s == "WARN")


def parse_frontmatter(text: str, rel: str, f: Findings) -> dict | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        f.err(rel, "缺少 frontmatter（首行必须为 ---）")
        return None
    try:
        idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        f.err(rel, "frontmatter 未闭合")
        return None
    raw = "\n".join(lines[1:idx])
    if idx == 1:
        f.err(rel, "frontmatter 为空（疑似 ---\\n--- 双闭合）")
        return None
    try:
        fm = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        f.err(rel, f"YAML 解析失败: {e}")
        return None
    if not isinstance(fm, dict):
        f.err(rel, "frontmatter 不是 YAML 映射")
        return None
    return fm


def check_fmt(val, fmt: str) -> bool:
    if val is None or val == "" or val == "[]":
        return True
    if isinstance(val, dt.datetime):
        return fmt in ("datetime", "datetime_or_date")
    if isinstance(val, dt.date):
        return fmt in ("date", "datetime", "datetime_or_date")
    if isinstance(val, bool):
        return False
    if isinstance(val, (int, float)):
        return fmt == "number"
    s = str(val)
    if fmt == "date":
        return bool(DATE_RE.match(s))
    if fmt == "datetime":
        return bool(DATETIME_RE.match(s))
    if fmt == "datetime_or_date":
        return bool(DATE_RE.match(s) or DATETIME_RE.match(s))
    if fmt == "number":
        return bool(re.match(r"^\d+(\.\d+)?$", s))
    if fmt == "time":
        return bool(re.match(r"^\d{2}:\d{2}(-\d{2}:\d{2})?$", s))
    return True


def iter_md_cards(root: Path):
    for p in root.rglob("*.md"):
        if p.name.endswith(".excalidraw.md"):
            continue
        rel_parts = p.relative_to(root).parts
        if rel_parts[0] in SKIP_DIRS or p.name in SKIP_FILES:
            continue
        if any(seg in SKIP_DIRS for seg in rel_parts[:-1]):
            continue
        yield p


def build_link_index(root: Path) -> tuple[set[str], set[str]]:
    """返回 (可解析目标集合, 全路径无扩展名集合)。

    目标含：所有 md 的 stem、所有附件（含 _assets 内）的完整文件名、
    以及所有文件的 vault 相对路径（去扩展名）——对应 Obsidian 的
    短链接、附件嵌入、全路径 wikilink 三种解析方式。
    注意：附件目录（_assets）不扫卡片但必须入索引。
    """
    idx_skip = SKIP_DIRS - {"_assets", "Excalidraw"}
    stems: set[str] = set()
    paths: set[str] = set()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel_parts = p.relative_to(root).parts
        if rel_parts[0] in idx_skip or any(seg in idx_skip for seg in rel_parts[:-1]):
            continue
        if p.suffix == ".md" and not p.name.endswith(".excalidraw.md"):
            stems.add(p.stem)
        else:
            stems.add(p.name)
        paths.add(str(p.relative_to(root).with_suffix("")))
    return stems, paths


def resolves(target: str, stems: set[str], paths: set[str]) -> bool:
    t = target.strip()
    return t in stems or t in paths


def validate(root: Path) -> Findings:
    f = Findings()
    stems, paths = build_link_index(root)
    cards = list(iter_md_cards(root))
    for p in cards:
        rel = str(p.relative_to(root))
        text = p.read_text(encoding="utf-8")
        fm = parse_frontmatter(text, rel, f)
        if fm is None:
            continue
        ctype = fm.get("type")
        if not ctype:
            f.err(rel, "缺少 type 字段")
            continue
        if ctype == "note":
            spec = NOTE_SPEC
        elif ctype in TYPE_SPEC:
            spec = TYPE_SPEC[ctype]
        else:
            f.err(rel, f"未知 type: {ctype}")
            continue

        # 路径归属
        expect_root = spec["root"]
        if not rel.startswith(expect_root + "/"):
            f.err(rel, f"type={ctype} 应位于 {expect_root}/ 下")
            continue

        # 路径深度规范
        pat_key = ctype
        if ctype == "journal":
            pat_key = f"journal:{fm.get('subtype', '')}"
        if ctype == "note":
            pat_key = fm.get("subtype", "")
        pat = PATH_PATTERNS.get(pat_key)
        if pat:
            sub_rel = rel[len(expect_root) + 1:]
            if not re.match(pat, sub_rel):
                f.err(rel, f"路径不符合 {pat_key} 约定（期望模式 {pat}）")

        if NEST_RE.search(rel):
            f.err(rel, "路径出现 YYYY/MM/YYYY/MM 双层嵌套")

        # 必填字段
        for field in spec["required"]:
            v = fm.get(field)
            if v is None or v == "" or v == "[]":
                f.err(rel, f"缺少必填字段 {field}")

        # 枚举
        enums: dict[str, set] = dict(spec.get("enums", {}))
        if ctype == "note":
            sub = fm.get("subtype")
            if sub not in NOTE_SPEC["subtype_enums"]:
                f.err(rel, f"未知 note.subtype: {sub}")
            else:
                enums.update({k: v for k, v in NOTE_SPEC["subtype_enums"][sub].items()
                              if k == "status" and "status" in fm})
        for field, allowed in enums.items():
            v = fm.get(field)
            if v is not None and v != "" and str(v) not in allowed:
                f.err(rel, f"{field}='{v}' 不在枚举 {sorted(allowed)} 内")

        # 格式
        for field, fmt in spec.get("fmts", {}).items():
            v = fm.get(field)
            if v is not None and v != "" and not check_fmt(v, fmt):
                f.warn(rel, f"{field}={v!r} 不符合 {fmt} 格式")

        # 退役字段（警告级）：scheduled/energy 等只写不读的残留
        if ctype == "task":
            for fld in RETIRED_TASK_FIELDS:
                if fld in fm:
                    f.warn(rel, f"{fld} 为退役字段（只写不读），建议清除")

        # 投入时段（v0.9）：sessions 条目格式/顺序/跨度；activeSince 滞留检测
        if ctype == "task":
            ss = fm.get("sessions")
            if ss is not None and not isinstance(ss, list):
                f.err(rel, "sessions 必须是 YAML 列表")
            prev_end = ""
            for s in (ss if isinstance(ss, list) else []):
                sv = str(s).strip()
                m = SESSION_ENTRY_RE.match(sv)
                if not m:
                    f.warn(rel, f"sessions 条目 {sv!r} 须为 \"YYYY-MM-DD HH:MM ~ YYYY-MM-DD HH:MM\"")
                    continue
                start, end = m.group(1), m.group(3)
                if start > end:
                    f.warn(rel, f"sessions 条目 {sv!r} 结束早于开始")
                if prev_end and start < prev_end:
                    f.warn(rel, f"sessions 条目 {sv!r} 早于上一条结束（应按时间排序）")
                # 只比相邻：乱序一次 WARN 即止，不抬高水位传染后续合法条目
                prev_end = end
                try:
                    span = (dt.datetime.strptime(end, "%Y-%m-%d %H:%M")
                            - dt.datetime.strptime(start, "%Y-%m-%d %H:%M")).total_seconds()
                    if span > 86400:
                        f.warn(rel, f"sessions 条目 {sv!r} 跨度超 24 小时，请核实")
                except ValueError:
                    f.warn(rel, f"sessions 条目 {sv!r} 日期不存在（如 2026-02-31）")
            if fm.get("activeSince") is not None and str(fm.get("status")) != "in-progress":
                f.warn(rel, f"activeSince={fm.get('activeSince')!r} 残留"
                       "（仅 status=in-progress 应有；手动改过状态请结算进 sessions 或清除）")

        # icon（可选）：单个 emoji（允许 ZWJ 组合/旗帜），勿用类型标记
        iv = fm.get("icon")
        if iv is not None and str(iv).strip() != "":
            ivs = str(iv).strip()
            segs = re.sub("[\ufe0f\U0001F3FB-\U0001F3FF\u20e3]", "", ivs).split("\u200d")
            seg_ok = lambda s: (len(s) == 1 and ord(s) >= 0x2100) or (
                len(s) == 2 and all(0x1F1E6 <= ord(c) <= 0x1F1FF for c in s))
            if re.search(r"[\w\s]", ivs) or not (1 <= len(segs) <= 4) or not all(map(seg_ok, segs)):
                f.err(rel, f"icon={ivs!r} 应为单个 emoji（勿用文字/类型标记）")
            elif any(c in "\U0001F4C2\U0001F680\U0001F3AF\U0001F4D3\U0001F4A1\U0001F4CC\U0001F4CE" for c in "".join(segs)):
                f.err(rel, f"icon={ivs!r} 勿用类型标记 emoji")

        # 条件必填：task done 必须有 completedAt
        if ctype == "task" and str(fm.get("status")) == "done":
            v = fm.get("completedAt")
            if v is None or v == "":
                f.err(rel, "status=done 但缺少 completedAt")

        # 数值范围：progress 0-100
        pv = fm.get("progress")
        if isinstance(pv, (int, float)) and not isinstance(pv, bool) and not (0 <= pv <= 100):
            f.err(rel, f"progress={pv} 超出 0-100")

        # wikilink 字段可解析（字段内可含多个链接）
        for field in WIKILINK_FIELDS:
            v = fm.get(field)
            if isinstance(v, str) and "[[" in v:
                for m in WIKILINK_RE.finditer(v):
                    if not resolves(m.group(1), stems, paths):
                        f.err(rel, f"{field} 断链: {m.group(1)}")

        # 习惯打卡
        if spec.get("checkins"):
            cis = fm.get("checkins")
            if cis is None:
                cis = []
            if not isinstance(cis, list):
                f.err(rel, "checkins 必须是 YAML 列表")
            else:
                vals = [str(c) for c in cis]
                if len(vals) != len(set(vals)):
                    dup = sorted({v for v in vals if vals.count(v) > 1})
                    f.err(rel, f"checkins 存在重复日期: {dup}")
                for c in cis:
                    iso = isinstance(c, dt.date) and not isinstance(c, dt.datetime)
                    if not iso and not (isinstance(c, str) and DATE_RE.match(c)):
                        f.err(rel, f"checkins 条目非 ISO 日期(YYYY-MM-DD): {c!r}")

        # 打卡注记：可选映射，键为 ISO 日期、值为字符串；注记日期必须在 checkins 内
        if spec.get("checkins"):
            cn = fm.get("checkin_notes")
            if cn is not None:
                if not isinstance(cn, dict):
                    f.err(rel, "checkin_notes 必须是映射（日期 -> 文本）")
                else:
                    cis_keys = {str(c) for c in (fm.get("checkins") or [])}
                    for k, v in cn.items():
                        # 未加引号的日期键被 pyyaml 解析成 date 对象——归一化后再判
                        ks = k.isoformat() if isinstance(k, dt.date) else str(k)
                        if not DATE_RE.match(ks):
                            f.err(rel, f"checkin_notes 键非 ISO 日期: {k!r}")
                        if not isinstance(v, str) or not v.strip():
                            f.err(rel, f"checkin_notes[{ks!r}] 值须为非空文本")
                        if ks not in cis_keys:
                            f.err(rel, f"checkin_notes[{ks!r}] 对应日期不在 checkins 内")

        # 命名规范（警告级）
        emoji = spec.get("emoji")
        if ctype == "note":
            emoji = NOTE_SPEC["subtype_emoji"].get(str(fm.get("subtype")))
        if ctype == "journal" and fm.get("subtype") == "daily":
            emoji = "📅"
        if emoji and not p.stem.startswith(emoji):
            f.warn(rel, f"文件名未以 {emoji} 前缀命名")
        if spec.get("mmdd") and not re.search(r"_\d{4}$", p.stem) and not re.search(r"_\d{2}\d{2}$", p.stem):
            f.warn(rel, "任务文件名缺 _MMDD 后缀")

        # 正文断链（警告级；剥离行内代码与代码块，示例文本不算链接）
        body = text.split("---", 2)[-1] if text.startswith("---") else text
        body = re.sub(r"```.*?```", "", body, flags=re.S)
        body = re.sub(r"`+[^`\n]*`+", "", body)
        for m in WIKILINK_RE.finditer(body):
            target = m.group(1).strip()
            if not resolves(target, stems, paths):
                f.warn(rel, f"正文断链: [[{target}]]")

    return f


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args()
    root = Path(args.root).resolve()
    f = validate(root)
    for sev, file, msg in f.items:
        print(f"{sev}  {file}  {msg}")
    n_cards = sum(1 for _ in iter_md_cards(root))
    print(f"\n=== 校验完成: {n_cards} 张卡片, {f.errors} ERROR / {f.warns} WARN ===")
    return 1 if f.errors else 0


if __name__ == "__main__":
    sys.exit(main())
