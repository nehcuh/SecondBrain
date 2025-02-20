---
createdAt: 2025-02-20 14:41
tags:
  - "#area"
cssclasses:
  - kanban
rootArea: 
goals:
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
	WHERE !contains(file.path, "99. Hidden") 
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
	- [ ] 资料汇总 🔁 every day 
	- [ ] 复习资料 🔁 every day 

## 🖇️ References

# 📚 Knowledge Base
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	createdAt as CreatedTime,
	tags as Category
FROM [[]]
WHERE (contains(file.tags, "#clipping") or contains(file.tags, "#reference") or contains(file.tags, "#notebook")) or contains(file.tags, "#inspiration")
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
