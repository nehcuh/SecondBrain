---
created_at: <% tp.date.now("YYYY-MM-DD HH:mm:ss") %>
tags:
  - "#area"
  - "#resource"
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
