---
created_at: 2024-01-06 17:53:41
tags:
  - "#area"
Area/Resource: 
archived:
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

```button
name 🏗️ Create Project
type command
action QuickAdd: 🏗️ Create Project
```

# 👀 Views

## 📥 Tasks Inbox

```dataview
TABLE due FROM [[]] WHERE contains(tags, "#task") AND !done AND !archived AND scheduled = null
```

## 📒 Notes Inbox

```dataview
TABLE created_at FROM [[]] WHERE contains(tags, "#note")
```


# 🏗️ Projects

```dataview
TABLE Deadline, Progress FROM [[]] WHERE contains(tags, "#project")
```


# 🎯 Goals

- [ ] 体脂率降到 20% 📅 2024/12/31 🛫 2024-01-06 ⏫ #goal
- [ ] 引体向上 5 个 📅 2024/06/30🛫 2024-01-06 ⏫ #goal

# 💦Efforts
```dataview
TABLE WITHOUT ID (link(file.path, title)) AS Title, due AS Due FROM [[]] WHERE contains(tags, "#task") AND !archived
```
