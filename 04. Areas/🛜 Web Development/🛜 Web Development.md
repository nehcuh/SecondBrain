---
createdAt: 2024-01-12 17:04
tags:
  - "#area"
cssclasses:
  - banner-image
rootArea: 
goals:
---
# ⚡️ Quick Actions

````ad-function
```button
name ✅ New Task
type command
action QuickAdd: ✅ Create A Task
```
```button
name 🔔 New Meeting
type command
action QuickAdd: 🔔 Create A Meeting
```
```button
name 🗂️ New Notebook
type command
action QuickAdd: 🗂️ Create A Notebook
```
```button
name 📖 New Readwise Note
type command
action QuickAdd: 📖 Create A Readwise Note
```
```button
name 📒 New Common Note
type command
action QuickAdd: 📒 Create A Common Note
```
```button
name ✂️ New Clipping
type command
action QuickAdd: ✂️ Create A Clipping
```
```button
name 🏔️ New Area
type command
action QuickAdd: 🏔️ Create Area
```
```button
name 🏞️ New Resource
type command
action QuickAdd: 🏞️ Create Resource
```
````
# 🏗️ Processing Projects
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) as Title,
	area AS Area,
	rootProject AS RootProject,
	dateformat(due, "DD") AS Due,
	dateformat(scheduled, "DD") AS Scheduled
FROM [[]]
WHERE 
	contains(file.tags, "#project") 
AND 
	!archived 
AND 
	!done
AND
	status = "processing"
AND !contains(file.path, "99. Hidden")
```

# ✅ Tasks
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	dateformat(due, "DD") AS Due
FROM [[]]
WHERE !archived AND !done
AND !contains(file.path, "99. Hidden")
AND contains(file.tags, "#task")
```

# 🏔️ Sub Areas
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	createdAt AS CreatedTime
FROM [[]]
WHERE contains(file.tags, "#area")
```


# 📚 Knowledge Base
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	createdAt as CreatedTime
FROM [[]]
WHERE (contains(file.tags, "#clipping") or contains(file.tags, "#reference"))
AND !contains(file.path, "99. Hidden")
```

## 💦 Efforts
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title
FROM [[]]
WHERE !contains(file.path, "99. Hidden")
AND contains(file.tags, "#task")
AND !done
```
