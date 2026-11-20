---
type: journal
subtype: daily
date: <% tp.date.now("YYYY-MM-DD") %>
tags: [journal, daily]
---

# <% tp.date.now("YYYY-MM-DD dddd") %>

## 今日任务

```dataviewjs
const today = dv.date(dv.current().date);
const tasks = dv.pages('"06 Tasks"')
  .where(p => p.type === "task" && !p.archived)
  .where(p => p.due && dv.date(p.due).toFormat("yyyy-MM-dd") === today.toFormat("yyyy-MM-dd"))
  .sort(p => p.priority, "desc");
if (tasks.length === 0) { dv.el("p", "暂无今日任务"); }
else { dv.table(["任务", "优先级", "状态"], tasks.map(p => [p.file.link, p.priority, p.status])); }
```

## 习惯打卡

```dataviewjs
const today = dv.date(dv.current().date).toFormat("yyyy-MM-dd");
const habits = dv.pages('"07 Habits"').where(p => p.type === "habit" && !p.archived);
if (habits.length === 0) { dv.el("p", "暂无习惯"); }
else {
  for (let h of habits) {
    const ci = Array.isArray(h.checkins) ? h.checkins : [];
    const done = ci.some(d => { try { return dv.date(d).toFormat("yyyy-MM-dd") === today; } catch { return d === today; } });
    dv.el("li", `${done ? "- [x]" : "- [ ]"} ${h.title}`);
  }
}
```

## 今日会议

```dataviewjs
const today = dv.date(dv.current().date).toFormat("yyyy-MM-dd");
const meetings = dv.pages('"05 Notes/Meetings"').where(p => p.date && dv.date(p.date).toFormat("yyyy-MM-dd") === today);
if (meetings.length === 0) { dv.el("p", "无会议"); }
else { dv.table(["会议", "时间", "状态"], meetings.map(p => [p.file.link, p.time || "—", p.status === "done" ? "✅" : p.status === "cancelled" ? "❌" : "📅"])); }
```

## 今日 Effort

```dataviewjs
const today = dv.date(dv.current().date).toFormat("yyyy-MM-dd");

const doneTasks = dv.pages('"06 Tasks"').where(p => p.type === "task" && p.status === "done" && p.completedAt && dv.date(p.completedAt).toFormat("yyyy-MM-dd") === today);
const meetings = dv.pages('"05 Notes/Meetings"').where(p => p.date && dv.date(p.date).toFormat("yyyy-MM-dd") === today);
const notes = dv.pages('"05 Notes"').where(p => p.createdAt && dv.date(p.createdAt).toFormat("yyyy-MM-dd") === today);
const contacts = dv.pages('"05 Notes/Contacts"').where(p => p.createdAt && dv.date(p.createdAt).toFormat("yyyy-MM-dd") === today);

let md = "";
if (doneTasks.length) { md += `- ✅ 完成 ${doneTasks.length} 个任务: ${doneTasks.map(p => p.file.link).join(", ")}\n`; }
if (meetings.length) { md += `- 🤝 参加 ${meetings.length} 场会议: ${meetings.map(p => p.file.link).join(", ")}\n`; }
if (notes.length) { md += `- 📝 新建 ${notes.length} 篇笔记: ${notes.map(p => p.file.link).join(", ")}\n`; }
if (contacts.length) { md += `- 👤 新增 ${contacts.length} 个联系人: ${contacts.map(p => p.file.link).join(", ")}\n`; }

if (!md) { dv.el("p", "今日暂无记录"); }
else { dv.el("div", md); }
```

## 今日思考


## 明日计划


