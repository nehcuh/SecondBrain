---
tags:
  - "#dailyNote"
created_at: <% tp.date.now("YYYY-MM-DD HH:mm") %>
mood: 🙂
---
<< [[02 Notes/Periodic Notes/Daily/<% moment(tp.file.title,'YYYY-MM-DD').add(-1,'days').format("YYYY-MM-DD_ddd")%>|<% moment(tp.file.title,'YYYY-MM-DD').add(-1,'days').format("YYYY-MM-DD_ddd") %>]] | [[02 Notes/Periodic Notes/Weekly/<% moment(tp.file.title,'YYYY-MM-DD').format("YYYY-[W]WW") %>|<% moment(tp.file.title,'YYYY-MM-DD').format("YYYY-[W]WW") %>]] | [[02 Notes/Periodic Notes/Daily/<% moment(tp.file.title,'YYYY-MM-DD').add(1,'days').format("YYYY-MM-DD_ddd") %>|<% moment(tp.file.title,'YYYY-MM-DD').add(1,'days').format("YYYY-MM-DD_ddd") %>]] >> 

# 💡 Reminders

> [!DANGER] Today's Highlight
> %% What am I most looking forward to today? %%

# 🛠️ Quick Actions

```button
name ✅ Create Task
type command
action QuickAdd: ✅ Create Task
```

```button
name 🔔 Create Meeting
type command
action QuickAdd: 🔔 Create Meeting
```

```button
name 📝 Create Note
type command
action QuickAdd: 📝 Create Note
```

```button
name 🏗️ Create Project
type command
action QuickAdd: 🏗️ Create Note
```

```button
name ⛰️ Create Area/Resource
type command
action QuickAdd: ⛰️ Create Area/Resource
```

# 📆 Today

## ✅ Tasks

```dataview
TABLE title, due, startTime, endTime, contacts
FROM #task
WHERE dateformat(date(due), "YYYY-MM-DD") <= dateformat(date(today), "YYYY-MM-DD") AND !contains(file.path, "99. Hidden") AND !done AND !Archived SORT startTime asc
```

## 📘 Notes

```dataview
TABLE title, startTime, endTime
FROM #note
WHERE dateformat(date(Due), "YYYY-MM-DD") = dateformat(date(today), "YYYY-MM-DD") AND !contains(file.path, "99. Hidden") AND !done AND !Archived SORT startTime asc
```

## 🔔 Meeting

```dataview
TABLE title, due, startTime, endTime
FROM #meeting
WHERE date(due) <= date(today) + dur(1 days) AND !contains(file.path, "99. Hidden") AND !done AND !Archived SORT startTime asc
```

# 💦 Efforts

```dataview
TABLE title, due, startTime, endTime
FROM ""
WHERE 
(contains(tags, "#task") or contains(tags, "#meeting") or contains(tags, "#note")) 
AND 
(
dateformat(date(due), "YYYY-MM-DD") = dateformat(date(today), "YYYY-MM-DD")
OR 
dateformat(date(scheduled_date), "YYYY-MM-DD") = dateformat(date(today), "YYYY-MM-DD")
OR
dateformat(date(scheduled), "YYYY-MM-DD") = dateformat(date(today), "YYYY-MM-DD")
)
AND done AND !contains(file.path, "99. Hidden")
SORT startTime asc
```


# ♻️ Habit Tracker
- [ ] 有氧锻炼 30 分钟 🔁 every day 
- [ ] 器械锻炼 5 组 🔁 every day 
- [ ] 视频学习 30 分钟  🔁 every day 
- [ ] 有效阅读 15 分钟 🔁 every day 


# 🔐 Archived

```dataview
TABLE title, due, startTime, endTime
FROM ""
WHERE 
(contains(tags, "#task") or contains(tags, "#meeting")) 
AND 
(
dateformat(date(due), "YYYY-MM-DD") = dateformat(date(today), "YYYY-MM-DD")
OR 
dateformat(date(scheduled_date), "YYYY-MM-DD") = dateformat(date(today), "YYYY-MM-DD")
)
AND Archived AND !contains(file.path, "99. Hidden")
SORT startTime asc
```
