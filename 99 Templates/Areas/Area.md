---
type: area
name: "<% tp.file.title.replace('📂 ', '') %>"
status: active
description: 
icon: 
parent: 
tags: [area]
createdAt: <% tp.date.now("YYYY-MM-DD") %>
updatedAt: <% tp.date.now("YYYY-MM-DD") %>
archived: false
---

# 📂 <% tp.file.title.replace('📂 ', '') %>

> 💡 一句话描述这个领域，你在持续精进什么？

## 🎯 目标

```dataview
TABLE status, progress, level
FROM "01 Goals"
WHERE contains(file.outlinks, this.file.link) AND !archived
SORT level ASC
```

## 📦 活跃项目

```dataview
TABLE status, progress
FROM "03 Projects"
WHERE contains(string(area), this.name) AND !archived AND status != "done"
SORT createdAt DESC
```

## 🔄 习惯

```dataview
TABLE frequency, goal
FROM "07 Habits"
WHERE contains(file.outlinks, this.file.link) AND !archived
```

## ✅ 待办

```dataviewjs
const tasks = dv.pages('"06 Tasks"')
  .where(p => p.type === "task" && p.area && String(p.area).includes(dv.current().name) && !p.archived && p.status !== "done")
  .sort(p => p.priority, "asc");
if (tasks.length === 0) { dv.el("p", "暂无待办"); }
else { dv.table(["任务", "优先级", "截止"], tasks.map(p => [dv.fileLink(p.file.path, false, p.title || p.file.name), p.priority, p.due])); }
```

## ✅ 已完成

```dataviewjs
const done = dv.pages('"06 Tasks"')
  .where(p => p.type === "task" && p.area && String(p.area).includes(dv.current().name) && p.status === "done" && !p.archived)
  .sort(p => p.completedAt, "desc")
  .limit(5);
if (done.length > 0) {
  dv.el("h2", "");
  dv.table(["任务", "优先级", "完成时间"], done.map(p => [dv.fileLink(p.file.path, false, p.title || p.file.name), p.priority, p.completedAt]));
}
```

## 🤝 最近会议

```dataviewjs
const meetings = dv.pages('"05 Notes/Meetings"')
  .where(p => p.type === "meeting" && p.area && String(p.area).includes(dv.current().name) && !p.archived)
  .sort(p => p.date, "desc")
  .limit(5);
if (meetings.length === 0) { dv.el("p", "暂无会议"); }
else { dv.table(["会议", "日期", "时间", "状态"], meetings.map(p => [dv.fileLink(p.file.path, false, p.title || p.file.name), p.date, p.time || "—", p.status === "done" ? "✅" : p.status === "cancelled" ? "❌" : "📅"])); }
```

## 📝 相关笔记

```dataviewjs
const notes = dv.pages('"05 Notes"')
  .where(p => p.type === "note" && p.area && String(p.area).includes(dv.current().name) && !p.archived)
  .sort(p => p.updatedAt, "desc");
if (notes.length === 0) { dv.el("p", "暂无笔记"); }
else { dv.table(["笔记", "类型", "更新"], notes.map(p => [dv.fileLink(p.file.path, false, p.title || p.file.name), p.subtype || "—", p.updatedAt || p.createdAt])); }
```

## 🌿 子领域

```dataviewjs
const children = dv.pages('"02 Areas"').where(p => p.type === "area" && p.parent === dv.current().name && !p.archived);

if (children.length === 0) {
  dv.el("p", "暂无子领域");
} else {
  const grid = dv.el("div", "", {cls: "sb-subarea-grid"});
  for (const c of children) {
    const card = grid.createEl("div", {cls: "sb-subarea-card"});
    card.style.cursor = "pointer";
    card.onclick = () => app.workspace.openLinkText(c.file.path, c.file.path, false);
    
    card.createEl("span", {text: c.icon || "📂", cls: "sb-subarea-icon"});
    card.createEl("span", {text: c.name, cls: "sb-subarea-name"});
    if (c.description) {
      card.createEl("div", {text: c.description, cls: "sb-subarea-desc"});
    }
  }
}
```

## 📊 本周动态

```dataviewjs
const areaName = a => { if (!a) return ''; if (typeof a === 'string') return a.replace(/^\[\[.*\||\]\]$/g, ''); try { return a.path.split('/').pop().replace(/^📂 /, ''); } catch { return ''; } };
const weekStart = dv.date("today").startOf("week");
const weekEnd = weekStart.plus({days: 6});

const tasks = dv.pages('"06 Tasks"')
  .where(p => areaName(p.area) === dv.current().name && p.completedAt && dv.date(p.completedAt) >= weekStart && dv.date(p.completedAt) <= weekEnd);
const meetings = dv.pages('"05 Notes/Meetings"')
  .where(p => areaName(p.area) === dv.current().name && p.date && dv.date(p.date) >= weekStart && dv.date(p.date) <= weekEnd);
const notes = dv.pages('"05 Notes"')
  .where(p => areaName(p.area) === dv.current().name && p.updatedAt && dv.date(p.updatedAt) >= weekStart && dv.date(p.updatedAt) <= weekEnd);

let md = [];
if (tasks.length) md.push(`- ✅ 完成任务 ${tasks.length} 个`);
if (meetings.length) md.push(`- 🤝 会议 ${meetings.length} 场`);
if (notes.length) md.push(`- 📝 更新笔记 ${notes.length} 篇`);

if (md.length === 0) dv.el("p", "本周暂无动态");
else dv.el("div", md.join("\n"));
```

## 📚 资料库

| 类型 | 存放路径 | 说明 |
|------|----------|------|
| 📄 文献 | `_assets/文献/` | PDF、论文、网页存档 |
| 🎬 音视频 | `_assets/音视频/` | 录屏、播客、课程 |
| 📎 附件 | `_assets/附件/` | 图片、表格、其他 |

> 💡 资料直接拖进 Obsidian 或 `[[链接]]` 引用，全在这个领域文件夹里，不乱跑
