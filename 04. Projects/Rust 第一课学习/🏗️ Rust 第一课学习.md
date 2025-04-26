---
createdAt: 2025-04-26 12:49
tags:
  - "#project"
status: 
startDate: 
due: 2025-04-26
scheduled: 2025-04-26
rootProject: 
area: "[[🏕️ Rust]]"
goals: 
milestones: 
cssclasses:
  - kanban
---
## 👀 Bird View
- ✅ Tasks
  ```dataview
	TABLE WITHOUT ID 
		(link(file.path, title)) as Title, 
		dateformat(due, "DD") AS Due, 
		startTime AS Start, 
		endTime AS End, 
		contacts AS Contacts
	FROM [[]]
	WHERE (date(due) = date(2025-04-26) 
	OR date(date) =date(2025-04-26))
	AND !contains(file.path, "99. Hidden") 
	AND contains(file.tags, "#task")
	AND status != "#canceled" AND status != "#done"
	AND !archived 
	SORT createdAt asc	
   ```
- 📅 Meetings
    ```dataview
   TABLE WITHOUT ID 
		(link(file.path, title)) as Title,
		scheduled as Scheduled,
		dateformat(due, "DD") AS Due, 
		startTime AS Start, 
		endTime AS End
	FROM [[]]
	WHERE !contains(file.path, "99. Hidden") 
	AND contains(file.tags, "#meeting")
	AND status != "#canceled" AND status != "#done"
	AND !archived 
	SORT scheduled desc
   ```
- 📚 Notes
  ```dataview
   TABLE WITHOUT ID 
		(link(file.path, title)) as Title, 
		startTime AS Start, 
		endTime AS End,
		tags AS Status
	FROM [[]]
	WHERE !contains(file.path, "99. Hidden") 
	AND 
		status != "#canceled" AND status != "#done"
	AND
		contains(file.tags, "#note")
	AND
		!archived 
	SORT createdAt asc
   ```
- 🙌 Reminder
	- [ ] 项目进度追踪 🔁 every day 
	- [ ] 风险事项跟踪 🔁 every day 

## 🖇️ References

# 📚 Knowledge Base
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	createdAt as CreatedTime
FROM [[]]
WHERE (contains(file.tags, "#clipping") or contains(file.tags, "#reference") or contains(file.tags, "#notebook"))
AND !contains(file.path, "99. Hidden")
```

## 💦 Efforts
### ✅ Tasks
```dataview
TABLE WITHOUT ID 
	(link(file.path, title)) as Title, 
	dateformat(due, "DD") AS Due, 
	startTime AS Start, 
	endTime AS End, 
	contacts AS Contacts
FROM [[]]
WHERE !contains(file.path, "99. Hidden") 
AND contains(file.tags, "#task")
AND status = "#canceled" OR status = "#done"
AND !archived 
SORT startTime asc
```

### 📚 Notes
  ```dataview
   TABLE WITHOUT ID 
		(link(file.path, title)) as Title, 
		startTime AS Start, 
		endTime AS End,
		tags AS Status
	FROM [[]]
	WHERE !contains(file.path, "99. Hidden") 
	AND 
		status = "#canceled" OR status = "#done"
	AND
		contains(file.tags, "#note")
	AND
		!archived 
	SORT createdAt asc
   ```

## 📦 Archived
### 📚 Notes
  ```dataview
   TABLE WITHOUT ID 
		(link(file.path, title)) as Title, 
		startTime AS Start, 
		endTime AS End,
		tags AS Status
	FROM [[]]
	WHERE !contains(file.path, "99. Hidden") 
	AND
		contains(file.tags, "#note")
	AND
		archived 
	SORT createdAt asc
   ```
