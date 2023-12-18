---
created_at: 2023-12-16 20:36:38
tags:
  - "#project"
Area/Resource: 
Archived: 
deadline: 
banner: 
banner_x: 
banner_y: 
Progress: <progress max=100 value=0> </progress> 100%
---
Bar:: `$= dv.view('progress-bar', {file: '🏗️ hello world'})`

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
TABLE scheduled_date FROM [[]] WHERE contains(tags, "#meeting") AND !Archived
```

# 🎖️ Milestones


# 🎯 Goals


# 📂 Input


# 🗂️ Output

