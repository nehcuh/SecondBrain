---
cssclasses:
  - banner-image
---
>![!banner-image] ![[乘着热气球向上飞.jpg]]
>
# ⚡️ Quick Actions


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
name 💡 New Handbook
type command
action QuickAdd: 💡 Create A Handbook
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
```button
name 🏆 New Goal
type command
action QuickAdd: 🏆 Create A Goal
```
```button
name 💎 New Milestone
type command
action QuickAdd: 💎 Create A Milestone
```

# ✅ Todos

## 📅 Today Tasks

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	done AS Done,
	startTime AS Start,
	dateformat(date, "DD") AS Date,
	dateformat(due, "DD") AS Due,
	dateformat(scheduled, "DD") AS Scheduled
WHERE 
	contains(file.tags, "#task") 
AND actionable
AND date != null 
AND !done
AND (date = date(today) OR due = date(today) OR scheduled = date(today))
SORT startTime asc
```

## 🌞 Tomorrow

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	contacts AS Contacts,
	dateformat(due, "DD") AS Due,
	dateformat(scheduled, "DD") AS Scheduled
WHERE 
	contains(file.tags, "#task") 
AND actionable
AND date != null 
AND !done
AND due = (date(today) + dur(1 days))
SORT scheduled asc
```

## 🎧 Next 7 Days

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	contacts AS Contacts,
	dateformat(due, "DD") AS Due,
	dateformat(scheduled, "DD") AS Scheduled
WHERE 
	contains(file.tags, "#task") 
AND actionable
AND date != null 
AND !done
AND (due > (date(today) + dur(1 days)) AND due < (date(today) + dur(7 days)))
SORT due asc
```

# 🚀 Active Projects

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	status AS Status,
	dateformat(due, "DD") AS Due
WHERE contains(file.tags, "#project")
AND !done
AND !archived
AND !contains(file.path, "99. Hidden")
```

## 🧩 Live Areas

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	rootArea AS RootArea
WHERE !archived
AND contains(file.tags, "#area")
AND !contains(file.path, "99. Hidden")
```

## 🏆 Goals & Milestones

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	tags AS Category,
	project AS Project
WHERE 
	(
		contains(file.tags, "#goal") 
		OR 
		contains(file.tags, "#milestone")
	)
AND !contains(file.path, "99. Hidden")
```

# 💡 Creativity
## 📖 Processing Notes
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	tags AS Status,
	nextReview
WHERE 
	(
	contains(file.tags, "#note/🌱") 
	OR 
	contains(file.tags, "#note/🌿")
	)
AND !contains(file.path, "99. Hidden")
```

## 💤 Waiting Consume
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	area AS Area,
	resource AS Resource,
	status AS Status
WHERE contains(file.tags, "#clipping")
AND !contains(file.path, "99. Hidden")
```

## 🌏 Miscellaneous


# 🏆 Goals & 💎 Milestones

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	relatedGoal AS RelatedGoal,
	dateformat(scheduled, "DD") AS Scheduled,
	project AS RelatedProject
WHERE (contains(file.tags, "#goal") OR contains(file.tags, "#milestone"))
AND !contains(file.path, "99. Hidden")
```

# ♻️ Tasks Done Today

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	dateformat(date, "DD") AS Date,
	startTime as Start,
	endTime as End
WHERE contains(file.tags, "#task")
AND done
AND !archived
AND !contains(file.path, "99. Hidden")
AND date = date(today)
SORT startTime asc
```
