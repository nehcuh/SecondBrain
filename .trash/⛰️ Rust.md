---
created_at: 2023-12-17 10:56:26
tags:
  - "#area"
Area/Resource: 
banner: 
banner_x: 
banner_y: 
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

- [ ] 使用 rust 接入恒生制品下载接口 #goal 📅 2023-12-31