---
created_at: 2023-12-17 10:48:09
tags:
  - "#project"
Area/Resource: "[[⛰️ Rust]]"
Archived: 
Deadline: 2023-12-31
Progress: <progress max=100 value=0> </progress> 0%
status: "#🟩"
banner: 
banner_x: 
banner_y:
---

# 🚀 Actions

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

# 🕹️ Planning

```dataview
TABLE title, scheduled, due FROM [[]] 
WHERE (contains(tags, "#task") OR contains(tags, "#meeting"))
AND !Archived AND !contains(file.path, "99. Hidden")
SORT schedule ASC
```

# 👀 Views
## 📥 Tasks Inbox

```dataview
TABLE scheduled, due FROM [[]] WHERE contains(tags, "#task") AND !done AND !Archived AND scheduled = null
```

##  🔔 Meetings Inbox

```dataview
TABLE due AS "Schedule" FROM [[]] WHERE contains(tags, "#meeting") AND !Archived
```

# 🎖️ Milestones


# 🎯 Goals
- [ ] 使用 rust 接入恒生制品下载接口 #goal 📅 2023-12-31

# 📂 Input


# 🗂️ Output

