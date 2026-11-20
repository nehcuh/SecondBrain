---
cssclasses:
  - dashboard
  - home-page
tags: [dashboard]
---


> [!tip] 今日一页：待办 → 打卡 → 捕获（⌘P QuickAdd）

```dataviewjs
// ── 顶部统计 ──
const areaName = a => { if (!a) return ''; if (typeof a === 'string') return a.replace(/^\[\[.*\||\]\]$/g, ''); try { return a.path.split('/').pop().replace(/^📂 /, ''); } catch { return ''; } };
const today = dv.date("today");
const todayStr = today.toFormat("yyyy-MM-dd");
// 分钟级时间戳（v0.8.3+ 的 "YYYY-MM-DD HH:MM" 空格分隔）luxon 不认——统一 T 化再解析；解析失败返回 null，防整块崩
const dstr = v => { if (!v) return null; const d = dv.date(typeof v === "string" ? v.replace(" ", "T") : v); return d ? d.toFormat("yyyy-MM-dd") : null; };

const allTasks = dv.pages('"06 Tasks"').where(p => p.type === "task" && !p.archived && p.status !== "done" && p.status !== "paused");
// 有效截止日：due 一律当真——字段有值即真截止（v3.12.3 起 capture 不播种创建日假 due）——与提醒 Agent/Newton/手册 §7 同口径
const dueOf = p => {
  if (!p.due) return null;
  const raw = typeof p.due === "string" ? p.due.replace(" ", "T") : p.due;
  const d = dv.date(raw); if (!d) return null;
  return d;
};
const overdue = allTasks.where(p => { const d = dueOf(p); return d && d < today; });
const inbox = dv.pages('"06 Tasks"').where(p => p.type === "task" && !areaName(p.area) && !p.project && !p.topic && !p.archived);
const todayTasks = allTasks.where(p => dstr(p.due) === todayStr);
const todayMeetings = dv.pages('"05 Notes/Meetings"').where(p => p.type === "meeting" && p.status === "scheduled" && dstr(p.date) === todayStr);
const habits = dv.pages('"07 Habits"').where(p => p.type === "habit" && !p.archived);
const habitsUndone = habits.filter(h => {
  const ci = Array.isArray(h.checkins) ? h.checkins : [];
  return !ci.some(d => { try { return dv.date(d).toFormat("yyyy-MM-dd") === todayStr; } catch { return d === todayStr; } });
});
const noArea = p => { const a = p.area; if (!a) return true; if (typeof a === "string") return !a.includes("[["); try { return !a.path; } catch { return true; } };
const unprocessedClips = dv.pages('"05 Notes/Clip"').where(p => p.subtype === "clip" && !p.archived && noArea(p));

const wrap = dv.container.createEl("div", {cls: "sb-stats-row"});
const leaf = wrap.closest(".workspace-leaf") || document;
const jump = async (title) => {
  const scrollTo = () => {
    const h = [...leaf.querySelectorAll("h2")].find(x => x.textContent.includes(title));
    if (h) { h.scrollIntoView({behavior: "smooth", block: "start"}); return true; }
    return false;
  };
  if (scrollTo()) return;
  // Live Preview 长页虚拟化：目标区块未物化，按源码注释定位后强制滚动再重试
  const mv = app.workspace.getActiveViewOfType(MarkdownView);
  if (mv?.editor) {
    const content = await app.vault.read(mv.file);
    const line = content.split("\n").findIndex(l => l.includes(`── ${title} ──`));
    if (line >= 0) {
      mv.editor.setCursor({line, ch: 0});
      for (const ms of [200, 500, 1000]) setTimeout(scrollTo, ms);
      return;
    }
  }
  // 阅读模式（无 editor）长页也是增量渲染：等区块渲染出来再跳，别急着判失败
  for (const ms of [200, 500, 1000]) {
    await new Promise(r => setTimeout(r, ms));
    if (scrollTo()) return;
  }
  new Notice(`未找到「${title}」区块`);
};
const stats = [
  { label: "Inbox", value: inbox.length, color: inbox.length > 0 ? "amber" : "gray", go: () => jump("待办中心") },
  { label: "今日待办", value: todayTasks.length, color: "teal", go: () => jump("待办中心") },
  { label: "逾期", value: overdue.length, color: overdue.length > 0 ? "coral" : "gray", go: () => jump("逾期任务") },
  { label: "今日会议", value: todayMeetings.length, color: "purple", go: () => jump("待办中心") },
  { label: "待整理", value: unprocessedClips.length, color: unprocessedClips.length > 0 ? "pink" : "gray", go: () => jump("待整理剪藏") },
  { label: "习惯", value: habitsUndone.length, color: habitsUndone.length > 0 ? "blue" : "gray", go: () => jump("今日习惯") },
];
for (const s of stats) {
  const card = wrap.createEl("div", {cls: `sb-stat-card sb-${s.color}`});
  card.createEl("div", {text: String(s.value), cls: "sb-stat-num"});
  card.createEl("div", {text: s.label, cls: "sb-stat-label"});
  card.title = `查看${s.label}`;
  card.onclick = s.go;
}
```

```dataviewjs
// ── 待办中心 ──
// Inbox / 今日任务 / 进行中 / 今日会议 四栏合一——本质都是待办跟踪，合并省空间
const areaName = a => { if (!a) return ""; if (typeof a === "string") return a.replace(/^\[\[.*\||\]\]$/g, ""); try { return a.path.split("/").pop().replace(/^📂 /, ""); } catch { return ""; } };
const dot = pr => pr === "urgent" ? "🔴" : pr === "high" ? "🟠" : pr === "medium" ? "🟡" : "⚪";
const due = d => { try { const dt = dv.date(typeof d === "string" ? d.replace(" ", "T") : d); return dt.toFormat("MM/dd") + " 周" + ["日","一","二","三","四","五","六"][dt.weekday % 7]; } catch { return "—"; } };
const created = d => { try { return dv.date(typeof d === "string" ? d.replace(" ", "T") : d).toFormat("MM/dd"); } catch { return ""; } };
const today = dv.date("today");
const todayStr = today.toFormat("yyyy-MM-dd");
const dstr = v => { if (!v) return null; const d = dv.date(typeof v === "string" ? v.replace(" ", "T") : v); return d ? d.toFormat("yyyy-MM-dd") : null; };

const inbox = dv.pages('"06 Tasks"')
  .where(p => p.type === "task" && !areaName(p.area) && !p.project && !p.topic && !p.archived)
  .sort(p => p.createdAt, "asc");
const tasks = dv.pages('"06 Tasks"')
  .where(p => p.type === "task" && !p.archived && p.status !== "done" && p.status !== "paused" && dstr(p.due) === todayStr)
  .sort(p => ["urgent","high","medium","low"].indexOf(p.priority));
const inProgress = dv.pages('"06 Tasks"')
  .where(p => p.type === "task" && !p.archived && p.status === "in-progress")
  .sort(p => String(p.due || "9999-12-31"), "asc");
// 今日会议只列未开完的（done 移入已完成栏，cancelled 不显示）
const meetings = dv.pages('"05 Notes/Meetings"')
  .where(p => p.type === "meeting" && p.status === "scheduled" && dstr(p.date) === todayStr)
  .sort(p => p.time);

dv.el("h2", "📋 待办中心");
const grid = dv.container.createEl("div", {cls: "sb-todo-grid"});
const column = (emoji, name, rows, emptyText, render) => {
  const c = grid.createEl("div", {cls: "sb-todo-col"});
  const head = c.createEl("div", {cls: "sb-todo-head"});
  head.createEl("span", {text: emoji});
  head.createEl("span", {text: name, cls: "sb-todo-name"});
  head.createEl("span", {text: String(rows.length), cls: `sb-todo-count${rows.length ? " hot" : ""}`});
  const body = c.createEl("div", {cls: "sb-todo-body"});
  if (!rows.length) { body.createEl("div", {text: emptyText, cls: "sb-todo-empty"}); return; }
  for (const p of rows) {
    const row = body.createEl("a", {cls: "sb-todo-row", href: "#"});
    row.onclick = (e) => { e.preventDefault(); app.workspace.openLinkText(p.file.path, p.file.path, false); };
    render(row, p);
  }
};
const title = (r, p) => r.createEl("span", {text: (p.icon ? p.icon + " " : "") + (p.title || p.file.name), cls: "sb-todo-title"});
const meta = (r, t) => { if (t) r.createEl("span", {text: String(t), cls: "sb-todo-meta"}); };

column("📥", "Inbox", inbox, "已清空 ✓", (r, p) => { meta(r, dot(p.priority)); title(r, p); meta(r, created(p.createdAt)); });
column("☑️", "今日任务", tasks, "今天没有 ✨", (r, p) => { meta(r, dot(p.priority)); title(r, p); meta(r, areaName(p.area)); });
column("🔄", "进行中", inProgress, "暂无 ✓", (r, p) => { title(r, p); meta(r, due(p.due)); });
column("🤝", "今日会议", meetings, "今天没有 ✓", (r, p) => { meta(r, p.time || "—"); title(r, p); });
const doneAt = d => { try { return dv.date(typeof d === "string" ? d.replace(" ", "T") : d).toFormat("HH:mm"); } catch { return ""; } };
// 已完成 = 今日完成的任务（completedAt）+ 今天开完的会议（status=done；会议无 completedAt，以会议日为准）
const doneTasks = dv.pages('"06 Tasks"')
  .where(p => p.type === "task" && p.status === "done" && dstr(p.completedAt) === todayStr)
  .sort(p => p.priority);
const doneMeetings = dv.pages('"05 Notes/Meetings"')
  .where(p => p.type === "meeting" && p.status === "done" && dstr(p.date) === todayStr)
  .sort(p => p.time);
const doneToday = [...doneTasks, ...doneMeetings];
column("✅", "已完成", doneToday, "今天还没有 ✓", (r, p) => { r.classList.add("done"); title(r, p); meta(r, doneAt(p.completedAt || p.time)); });
```


```dataviewjs
// ── 领域概览 ──
const areaName = a => { if (!a) return ""; if (typeof a === "string") return a.replace(/^\[\[.*\||\]\]$/g, ""); try { return a.path.split("/").pop().replace(/^📂 /, ""); } catch { return ""; } };
const areas = dv.pages('"02 Areas"').where(p => p.type === "area" && !p.archived && p.status === "active" && (!p.parent || p.parent === ""));

if (areas.length > 0) {
  dv.el("h2", "📂 精进领域");
  const grid = dv.container.createEl("div", {cls: "sb-area-grid"});
  for (const a of areas.sort(p => p.name)) {
    const card = grid.createEl("div", {cls: "sb-area-card"});
    card.style.cursor = "pointer";
    card.onclick = () => app.workspace.openLinkText(a.file.path, a.file.path, false);
    
    const head = card.createEl("div", {cls: "sb-area-head"});
    head.createEl("span", {text: a.icon || "📂", cls: "sb-area-icon"});
    head.createEl("span", {text: a.name || a.file.name, cls: "sb-area-name"});
    
    if (a.description) {
      card.createEl("div", {text: a.description, cls: "sb-area-desc"});
    }
    
    const tasks = dv.pages('"06 Tasks"').where(p => areaName(p.area) === a.name && !p.archived && p.status !== "done");
    const habits = dv.pages('"07 Habits"').where(p => {
      if (p.type !== "habit" || p.archived) return false;
      const ol = p.file.outlinks;
      return ol && ol.some(l => l.path === a.file.path);
    });
    const goals = dv.pages('"01 Goals"').where(p => {
      if (p.archived || p.status !== "active") return false;
      const ol = p.file.outlinks;
      return ol && ol.some(l => l.path === a.file.path);
    });
    
    const meta = card.createEl("div", {cls: "sb-area-meta"});
    if (goals.length) meta.createEl("span", {text: `🎯 ${goals.length}`, cls: "sb-area-stat"});
    if (tasks.length) meta.createEl("span", {text: `✅ ${tasks.length}`, cls: "sb-area-stat"});
    if (habits.length) meta.createEl("span", {text: `🔄 ${habits.length}`, cls: "sb-area-stat"});
    if (!goals.length && !tasks.length && !habits.length) {
      meta.createEl("span", {text: "点击进入 →", cls: "sb-area-stat"});
    }
  }
}
```

```dataviewjs
// ── 目标进度 ──
// 目标=有终点可判定的成果（与领域三测互为镜像：领域无终点，目标必须有）
const goals = dv.pages('"01 Goals"').where(p => p.type === "goal" && !p.archived && p.status === "active")
  .sort((a, b) => ["longterm","annual","quarterly","monthly"].indexOf(a.level) - ["longterm","annual","quarterly","monthly"].indexOf(b.level));

dv.el("h2", "🎯 目标进度");
if (goals.length) {
  const LV = { longterm: ["长远", "sb-purple"], annual: ["年度", "sb-blue"], quarterly: ["季度", "sb-amber"], monthly: ["月度", "sb-teal"] };
  const grid = dv.container.createEl("div", {cls: "sb-goal-grid"});
  for (const g of goals) {
    const [lab, color] = LV[g.level] || ["目标", "sb-gray"];
    const pct = Math.min(100, Math.max(0, Number(g.progress) || 0));
    const card = grid.createEl("a", {cls: "sb-goal-card", href: "#"});
    card.onclick = (e) => { e.preventDefault(); app.workspace.openLinkText(g.file.path, g.file.path, false); };
    const head = card.createEl("div", {cls: "sb-goal-card-head"});
    head.createEl("span", {text: lab, cls: `sb-goal-lv ${color}`});
    head.createEl("span", {text: pct + "%", cls: "sb-goal-pct"});
    card.createEl("div", {text: g.title || g.file.name, cls: "sb-goal-card-title"});
    const bar = card.createEl("div", {cls: "sb-progress-bar sb-goal-bar"});
    const fill = bar.createEl("div", {cls: "sb-progress-fill"});
    fill.style.width = pct + "%";
  }
}
```

```dataviewjs
// ── 活跃项目 ──
const projects = dv.pages('"03 Projects"')
  .where(p => p.type === "project" && !p.archived && (p.status === "active" || p.status === "planning"))
  .sort(p => p.status === "active" ? 0 : 1, "asc")
  .sort(p => p.deadline, "asc");

if (projects.length > 0) {
  dv.el("h2", "🚀 项目");
  const grid = dv.container.createEl("div", {cls: "sb-project-list"});
  for (const p of projects) {
    const row = grid.createEl("a", {cls: "sb-project-row", href: p.file.path});
    row.style.textDecoration = "none";
    row.onclick = (e) => { e.preventDefault(); app.workspace.openLinkText(p.file.path, p.file.path, false); };
    
    const left = row.createEl("div", {cls: "sb-project-left"});
    const statusIcon = p.status === "active" ? "▶" : "⏸";
    left.createEl("span", {text: statusIcon, cls: `sb-project-status ${p.status}`});
    left.createEl("span", {text: p.name, cls: "sb-project-name"});
    
    const right = row.createEl("div", {cls: "sb-project-right"});
    if (p.deadline) {
      const dl = dv.date(typeof p.deadline === "string" ? p.deadline.replace(" ", "T") : p.deadline);
      const days = dl ? Math.floor(dl.diff(dv.date("today"), "days").days) : null;
      if (days !== null) {
      const urgency = days < 0 ? "overdue" : days < 3 ? "soon" : days < 7 ? "close" : "far";
      right.createEl("span", {text: days < 0 ? `${Math.abs(days)}d overdue` : `${days}d`, cls: `sb-project-deadline ${urgency}`});
      }
    }
    const pct = Math.min(100, Math.max(0, Number(p.progress) || 0));
    const bar = right.createEl("div", {cls: "sb-mini-bar"});
    bar.createEl("div", {cls: "sb-mini-fill", attr: {style: `width:${pct}%`}});
    right.createEl("span", {text: pct + "%", cls: "sb-project-pct"});
  }
}
```

```dataviewjs
// ── 待整理剪藏 ──
const fmt = d => { try { const dt = dv.date(typeof d==="string" ? d.replace(' ','T') : d); return dt.toFormat("MM/dd"); } catch { return String(d||"—"); } };
const noArea = p => { const a = p.area; if (!a) return true; if (typeof a === "string") return !a.includes("[["); try { return !a.path; } catch { return true; } };
const clips = dv.pages('"05 Notes/Clip"')
  .where(p => p.subtype === "clip" && !p.archived && noArea(p))
  .sort(p => p.createdAt, "desc");

dv.el("h2", "📎 待整理剪藏");
if (clips.length) {
  dv.table(["剪藏", "捕获"], clips.limit(8).map(p => [
    dv.fileLink(p.file.path, false, (p.icon ? p.icon + " " : "") + (p.title || p.file.name)),
    fmt(p.createdAt)
  ]));
  if (clips.length > 8) dv.el("p", `…还有 ${clips.length - 8} 条，处理完会自动收进这里`);
}
```

```dataviewjs
// ── 学习主题 ──
const areasInfo = dv.pages('"02 Areas"').where(p => p.type === "area" && !p.archived);
const areaLabel = a => {
  if (!a) return "—";
  const raw = typeof a === "string" ? a : (a.path || String(a));
  const stem = raw.split("/").pop().replace(/\.md$/, "").replace(/^📂 /, "");
  const ac = areasInfo.find(x => x.file.name === stem || (x.file.name || "").endsWith(stem));
  return ac ? `${ac.icon || "📂"} ${ac.name || ac.file.name}` : (stem || "—");
};
const topics = dv.pages('"05 Notes/Topics"')
  .where(p => p.type === "topic" && !p.archived)
  .sort(p => p.updatedAt, "desc")
  .limit(5);
dv.el("h2", "📓 学习主题");
if (topics.length) { dv.table(["主题", "进度", "领域"], topics.map(p => [dv.fileLink(p.file.path, false, p.file.name), (p.progress || 0) + "%", areaLabel(p.area)])); }
```

```dataviewjs
// ── 今日习惯 ──
const today = dv.date("today");
const todayStr = today.toFormat("yyyy-MM-dd");
const habits = dv.pages('"07 Habits"').where(p => p.type === "habit" && !p.archived);

dv.el("h2", "🔄 今日习惯");
// evidence 习惯打卡补注弹窗（Esc/空 = 仅打卡记待补注）
const askNote = (title, dateStr, backfill) => new Promise(resolve => {
  const overlay = dv.container.createEl("div", {cls: "sb-note-pop"});
  const box = overlay.createEl("div", {cls: "sb-note-box"});
  box.createEl("div", {text: `${title} · 这次做了/看了什么？${dateStr !== todayStr ? `（${dateStr}）` : ""}`, cls: "sb-note-title"});
  const ta = box.createEl("textarea", {cls: "sb-note-input", attr: {placeholder: "补充注记，可留空稍后补（≤200 字）", maxlength: "200"}});
  const btns = box.createEl("div", {cls: "sb-note-btns"});
  const close = val => { overlay.remove(); resolve(val); };
  const okBtn = btns.createEl("button", {text: backfill ? "补注" : "打卡 + 注记", cls: "sb-note-ok mod-cta"});
  okBtn.onclick = () => close(ta.value.trim());
  const skipBtn = btns.createEl("button", {text: "仅打卡", cls: "sb-note-skip"});
  skipBtn.onclick = () => close(null);
  ta.onkeydown = e => { if (e.key === "Escape") close(null); if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) close(ta.value.trim()); };
  overlay.onclick = e => { if (e.target === overlay) close(null); };
  setTimeout(() => ta.focus(), 50);
});
// checkin_notes 行级写入（键带引号防 YAML 日期对象化；与 sb.py replace_checkin_notes 同源）
const yamlEsc = v => /[[{}:#']/.test(v) ? `"${v.replace(/"/g, "'")}"` : v;
const writeNote = (lines, dateStr, text) => {
  const idx = lines.findIndex(l => l.trim() === "checkin_notes:");
  const entry = `  "${dateStr}": ${yamlEsc(text)}`;
  if (idx === -1) {
    const fmEnd = lines.findIndex((l, i) => i > 0 && l.trim() === "---");
    lines.splice(fmEnd, 0, "checkin_notes:", entry);
    return;
  }
  let j = idx + 1;
  const merged = {};
  while (j < lines.length && /^ {2}\S/.test(lines[j])) {
    const m = lines[j].match(/^ {2}"?([^":]+)"?:\s*(.*)$/);
    if (m) merged[m[1].trim()] = m[2];
    j++;
  }
  merged[dateStr] = yamlEsc(text);
  const block = ["checkin_notes:", ...Object.keys(merged).sort().map(k => `  "${k}": ${merged[k]}`)];
  lines.splice(idx, j - idx, ...block);
};
if (habits.length > 0) {
  const container = dv.container.createEl("div", {cls: "sb-habit-grid"});
  for (const h of habits) {
    const checkins = Array.isArray(h.checkins) ? h.checkins : [];
    const ds = c => { try { return dv.date(c).toFormat("yyyy-MM-dd"); } catch { return String(c); } };
    const evidence = h.evidence === true;
    const noteMap = (() => {
      const cn = h.checkin_notes;
      if (!cn || typeof cn !== "object" || Array.isArray(cn)) return {};
      const out = {};
      for (const [k, v] of Object.entries(cn)) out[ds(k)] = String(v);
      return out;
    })();
    const pendingDates = evidence ? [...new Set(checkins.map(ds))].filter(d => !(d in noteMap)).sort() : [];
    const doneTodayRaw = checkins.find(d => {
      try { return dv.date(d).toFormat("yyyy-MM-dd") === todayStr; } catch { return d === todayStr; }
    });
    const doneToday = !!doneTodayRaw;
    const streak = (() => {
      let s = 0, d = today;
      while (true) {
        const ds = d.toFormat("yyyy-MM-dd");
        const hit = checkins.find(c => { try { return dv.date(c).toFormat("yyyy-MM-dd") === ds; } catch { return c === ds; } });
        if (!hit) break;
        s++; d = d.minus({days: 1});
      }
      return s;
    })();

    const row = container.createEl("div", {cls: `sb-habit-card${doneToday ? " done" : ""}`});
    const top = row.createEl("div", {cls: "sb-habit-top"});
    const cb = top.createEl("input", {type: "checkbox"});
    cb.checked = doneToday;
    cb.setAttribute("style", "margin-right:10px;cursor:pointer;width:16px;height:16px;");
    cb.onchange = async () => {
      try {
        const file = app.vault.getAbstractFileByPath(h.file.path);
        if (!file) { new Notice(`❌ 文件未找到: ${h.file.path}`, 5000); return; }
        let note = null;
        if (cb.checked && evidence) note = await askNote(h.title || h.file.name, todayStr);
        let content = await app.vault.read(file);
        const lines = content.split("\n");
        const ciIdx = lines.findIndex(l => l.trim().startsWith("checkins:"));
        if (cb.checked) {
          if (ciIdx === -1) {
            const fmEnd = lines.findIndex((l, i) => i > 0 && l.trim() === "---");
            lines.splice(fmEnd, 0, "checkins:", `  - ${todayStr}`);
          } else {
            lines.splice(ciIdx + 1, 0, `  - ${todayStr}`);
          }
          if (note) writeNote(lines, todayStr, note);
        } else {
          const rmIdx = lines.findIndex(l => l.trim() === `- ${todayStr}`);
          if (rmIdx !== -1) lines.splice(rmIdx, 1);
        }
        await app.vault.modify(file, lines.join("\n"));
        new Notice(note ? `✅ ${h.title} 已打卡 + 注记` : (cb.checked && evidence ? `✅ ${h.title} 已打卡（待补注）` : `✅ ${h.title} 打卡成功`));
      } catch (e) {
        new Notice(`❌ 打卡失败: ${e.message}`, 8000);
      }
    };
    const nameWrap = top.createEl("div", {cls: "sb-habit-header"});
    nameWrap.createEl("span", {text: h.title || h.file.name, cls: "sb-habit-name"});
    if (streak > 0) nameWrap.createEl("span", {text: `🔥 ${streak}天`, cls: "sb-habit-streak"});
    if (pendingDates.length) {
      const badge = nameWrap.createEl("span", {text: `⚠️ 待补注 ${pendingDates.length}`, cls: "sb-habit-note-badge", attr: {title: "打卡了但没写注记，点击补注"}});
      badge.onclick = async () => {
        const target = pendingDates.includes(todayStr) ? todayStr : pendingDates[pendingDates.length - 1];
        const file = app.vault.getAbstractFileByPath(h.file.path);
        if (!file) return;
        const note = await askNote(h.title || h.file.name, target, true);
        if (!note) return;
        try {
          const lines = (await app.vault.read(file)).split("\n");
          writeNote(lines, target, note);
          await app.vault.modify(file, lines.join("\n"));
          new Notice(`✅ 已补注 ${target}`);
        } catch (e) { new Notice(`❌ 补注失败: ${e.message}`, 8000); }
      };
    }
    if (h.goal) {
      const gp = typeof h.goal === "string" ? (h.goal.match(/\[\[([^|\]]+)/)?.[1] ?? h.goal) : (h.goal.path || String(h.goal));
      const gl = row.createEl("span", {text: `→ ${gp.split("/").pop().replace(/^🎯\s*/, "")}`, cls: "sb-habit-goal"});
      gl.onclick = () => app.workspace.openLinkText(gp, "", false);
    }
    if (h.note) row.createEl("span", {text: String(h.note), cls: "sb-habit-note"});
    
    // 补打卡按钮
    const catchUp = nameWrap.createEl("span", {text: "📅", attr: {title: "补签昨天", style: "cursor:pointer;margin-left:4px;font-size:12px;"}});
    catchUp.onclick = async (e) => {
      e.stopPropagation();
      const y = new Date(); y.setDate(y.getDate() - 1);
      const d = y.getFullYear() + "-" + String(y.getMonth()+1).padStart(2,"0") + "-" + String(y.getDate()).padStart(2,"0");
      if (!window.confirm(`补打卡 ${h.title} → ${d}?`)) return;
      try {
        const file = app.vault.getAbstractFileByPath(h.file.path);
        let content = await app.vault.read(file);
        const lines = content.split("\n");
        const ciIdx = lines.findIndex(l => l.trim().startsWith("checkins:"));
        if (ciIdx === -1) {
          const fmEnd = lines.findIndex((l, i) => i > 0 && l.trim() === "---");
          lines.splice(fmEnd, 0, `checkins:\n  - ${d}`);
        } else {
          lines.splice(ciIdx + 1, 0, `  - ${d}`);
        }
        await app.vault.modify(file, lines.join("\n"));
        new Notice(`✅ 补签 ${h.title} → ${d}`);
      } catch (e) { new Notice(`❌ ${e.message}`, 5000); }
    };
    
    const checklist = h.daily_checklist;
    if (checklist && checklist.length > 0) {
      const chips = row.createEl("div", {cls: "sb-habit-chips"});
      for (const item of checklist) {
        chips.createEl("span", {text: item, cls: "sb-chip"});
      }
    }
  }
}
```

```dataviewjs
// ── 近 7 天 ──
const fmt = d => { try { const dt = dv.date(typeof d==="string" ? d.replace(' ','T') : d); return dt.toFormat("yyyyMMdd") + "_周" + ["日","一","二","三","四","五","六"][dt.weekday % 7]; } catch { return String(d||"—"); } };
const today = dv.date("today");
const todayStr = today.toFormat("yyyy-MM-dd");
const next7 = today.plus({days: 7}).toFormat("yyyy-MM-dd");
const dstr = v => { if (!v) return null; const d = dv.date(typeof v === "string" ? v.replace(" ", "T") : v); return d ? d.toFormat("yyyy-MM-dd") : null; };
const upcoming = dv.pages('"06 Tasks"')
  .where(p => p.type === "task" && !p.archived && p.status !== "done" && p.status !== "paused" && p.due)
  .where(p => { const d = dstr(p.due); return d && d > todayStr && d <= next7; })
  .sort(p => dstr(p.due));

dv.el("h2", "📅 近 7 天");
if (upcoming.length) { dv.table(["任务", "截止", "状态"], upcoming.map(p => [dv.fileLink(p.file.path, false, p.title || p.file.name), fmt(p.due), p.status === "in-progress" ? "🔄" : p.status === "todo" ? "⏳" : "—"])); }
```

```dataviewjs
// ── 灵感火花 ──
const areasInfo = dv.pages('"02 Areas"').where(p => p.type === "area" && !p.archived);
const areaLabel = a => {
  if (!a) return "—";
  const raw = typeof a === "string" ? a : (a.path || String(a));
  const stem = raw.split("/").pop().replace(/\.md$/, "").replace(/^📂 /, "");
  const ac = areasInfo.find(x => x.file.name === stem || (x.file.name || "").endsWith(stem));
  return ac ? `${ac.icon || "📂"} ${ac.name || ac.file.name}` : (stem || "—");
};
const sparks = dv.pages('"05 Notes/Inspiration"')
  .where(p => p.subtype === "inspiration" && !p.archived)
  .sort(p => p.updatedAt, "desc")
  .limit(5);
dv.el("h2", "💡 灵感火花");
if (sparks.length) { dv.table(["想法", "状态", "领域"], sparks.map(p => [dv.fileLink(p.file.path, false, p.file.name), p.status === "spark" ? "✨ 火花" : p.status === "developing" ? "🔨 孵化中" : p.status === "live" ? "🚀 试运行中" : "📋 已规划", areaLabel(p.area)])); }
```

```dataviewjs
// ── 最近笔记 ──
const fmt = d => { try { const dt = dv.date(typeof d==="string" ? d.replace(' ','T') : d); return dt.toFormat("yyyyMMdd") + "_周" + ["日","一","二","三","四","五","六"][dt.weekday % 7]; } catch { return String(d||"—"); } };
const latestNotes = dv.pages('"05 Notes"')
  .where(p => (p.subtype === "learning" || p.subtype === "handbook" || p.subtype === "blog" || p.subtype === "clip" || p.subtype === "knowledge") && !p.archived)
  .sort(p => p.updatedAt, "desc")
  .limit(5);
dv.el("h2", "📝 最近笔记");
if (latestNotes.length) { dv.table(["笔记", "类型", "更新"], latestNotes.map(p => [dv.fileLink(p.file.path, false, p.title || p.file.name), p.subtype === "learning" ? "📖" : p.subtype === "handbook" ? "📋" : p.subtype === "blog" ? "✍️" : p.subtype === "clip" ? "📎" : "📌", fmt(p.updatedAt || p.createdAt)])); }
```

```dataviewjs
// ── 逾期任务 ──
const fmt = d => { try { const dt = dv.date(typeof d==="string" ? d.replace(' ','T') : d); return dt.toFormat("yyyyMMdd") + "_周" + ["日","一","二","三","四","五","六"][dt.weekday % 7]; } catch { return String(d||"—"); } };
const today = dv.date("today");
// due 一律当真——字段有值即真截止（与顶部统计/提醒 Agent 同口径）；paused 搁置不算逾期
const dueOf = p => {
  if (!p.due) return null;
  const d = dv.date(typeof p.due === "string" ? p.due.replace(" ", "T") : p.due); if (!d) return null;
  return d;
};
const overdue = dv.pages('"06 Tasks"')
  .where(p => p.type === "task" && !p.archived && p.status !== "done" && p.status !== "paused")
  .where(p => { const d = dueOf(p); return d && d < today; })
  .sort(p => dueOf(p));

dv.el("h2", "⚠️ 逾期任务");
if (overdue.length) {
  dv.table(["任务", "截止", "逾期天数"], overdue.map(p => {
    const days = Math.floor(today.diff(dueOf(p), "days").days);
    return [dv.fileLink(p.file.path, false, (p.icon ? p.icon + " " : "") + (p.title || p.file.name)), fmt(p.due), `${days} 天`];
  }));
}
```


```dataviewjs
// ── AI 助手 ──
const open = dv.pages('"06 Tasks"').where(p => p.type === "task" && ["todo", "in-progress"].includes(p.status) && !p.archived);
const inbox = open.where(p => !p.area && !p.project && !p.topic);
const meetNoinbox = dv.pages('"05 Notes/Meetings"').where(p => p.type === "meeting" && p.status === "scheduled" && !p.area && !p.project && !p.topic);

dv.el("h2", "🤖 AI 助手");
const foot = dv.container.createEl("div", {cls: "sb-ai-footer"});
const fh = foot.createEl("div", {cls: "sb-ai-footer-head"});
fh.createEl("span", {text: inbox.length + meetNoinbox.length > 0 ? `📥 待分诊 ${inbox.length + meetNoinbox.length} 张` : "✓ 无待分诊", cls: inbox.length + meetNoinbox.length > 0 ? "sb-ai-hot" : "sb-ai-ok"});
const atlasLink = fh.createEl("a", {text: "🗺️ 全局拓扑 Atlas", href: "#"});
atlasLink.onclick = (e) => { e.preventDefault(); app.workspace.openLinkText("🗺️ Atlas.md", "", false); };
for (const tip of [
  "Mac/iPad：侧边栏 Newton 对话——记待办/完成任务/习惯打卡直接写入 vault（遵循 📋 AI 操作手册）",
  "Mac：vault 目录打开 Claude Code → /sb-triage 自动补全 area/project/tags（直接写入，git 可回滚）",
  "全库问答/检索：Claude Code 挂载 scripts/mcp_server.py（secondbrain MCP，7 工具）",
  "iPad：QuickAdd 快速捕获（⌘P），属性留给 AI 分诊补全",
]) foot.createEl("div", {text: tip, cls: "sb-ai-tip"});
```

