#!/usr/bin/env python3
"""从模板源仓库盖章一个全新的 SecondBrain vault（分发脚手架）.

用法:
    uv run scripts/stamp_new_vault.py /path/to/new-vault

规则:
- 清单 = git 跟踪文件（git ls-files -z），即"出厂态"；未跟踪的个人态
  （workspace.json、.venv、_assets 个人附件等）天然排除
- 内容目录（01-07、99 Conflict）不复制个人卡片，只建空骨架 + .gitkeep
- 模板资产（99 Templates、scripts、.obsidian 配置、AGENTS/README、两页看板）完整复制
- 目标目录必须不存在或为空
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent

CONTENT_DIRS = ["01 Goals", "02 Areas", "03 Projects", "05 Notes",
                "06 Tasks", "07 Habits", "99 Conflict"]

NEXT_STEPS = """\
盖章完成: {dst}

下一步:
  1. 用 Obsidian 打开该目录，允许社区插件
  2. cd {dst} && uv sync && uv run scripts/validate_cards.py   # 应为 0 ERROR
  3. (推荐) 接线版本控制与提交钩子:
       cd {dst} && git init && git config core.hooksPath .githooks && git add -A && git commit -m init
  4. 捕获第一个任务: uv run scripts/sb.py capture_task "你好，第二大脑"
"""


def manifest() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=SRC,
                         capture_output=True, check=True).stdout
    return [SRC / p for p in out.decode().split("\0") if p]


def is_content(path: Path) -> bool:
    rel = path.relative_to(SRC)
    return rel.parts[0] in CONTENT_DIRS


def stamp(dst: Path) -> None:
    if dst.exists() and any(dst.iterdir()):
        sys.exit(f"目标目录非空: {dst}")
    dst.mkdir(parents=True)

    copied = skipped = 0
    for f in manifest():
        if is_content(f):
            skipped += 1
            continue
        target = dst / f.relative_to(SRC)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
        copied += 1

    for d in CONTENT_DIRS:
        (dst / d).mkdir(exist_ok=True)
        keep = dst / d / ".gitkeep"
        keep.write_text("", encoding="utf-8")

    # 目录级空的子目录占位（Notes 族 + Excalidraw 画板 + Templater Inbox 引用）
    for sub in ["05 Notes/Journal/Daily", "05 Notes/Journal/Weekly",
                "05 Notes/Learning", "05 Notes/Handbook", "05 Notes/Blog",
                "05 Notes/Topics", "05 Notes/Meetings", "05 Notes/Contacts",
                "05 Notes/Clip", "05 Notes/Knowledge", "05 Notes/Inspiration",
                "Excalidraw", "06 Tasks/Inbox"]:
        p = dst / sub
        p.mkdir(parents=True, exist_ok=True)
        if not any(p.iterdir()):
            (p / ".gitkeep").write_text("", encoding="utf-8")

    print(f"复制模板资产 {copied} 个文件；跳过个人内容 {skipped} 个")
    print(NEXT_STEPS.format(dst=dst))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", type=Path, help="新 vault 目标目录（须为空）")
    a = ap.parse_args()
    stamp(a.target.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
