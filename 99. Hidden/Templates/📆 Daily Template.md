---
tags:
  - "#periodic/daily"
created_at: <% tp.date.now("YYYY-MM-DD HH:mm") %>
mood: 🙂
cssclasses:
  - kanban
---
<< [[03. Notes/Periodic/Daily/<% moment(tp.file.title,'YYYY-MM-DD').add(-1,'days').format("YYYY-MM-DD_ddd")%>|<% moment(tp.file.title,'YYYY-MM-DD').add(-1,'days').format("YYYY-MM-DD_ddd") %>]] | [[03. Notes/Periodic/Daily/<% moment(tp.file.title,'YYYY-MM-DD').format("YYYY-MM-DD_ddd") %>|<% moment(tp.file.title,'YYYY-MM-DD').format("YYYY-MM-DD_ddd") %>]] | [[03. Notes/Periodic/Daily/<% moment(tp.file.title,'YYYY-MM-DD').add(1,'days').format("YYYY-MM-DD_ddd") %>|<% moment(tp.file.title,'YYYY-MM-DD').add(1,'days').format("YYYY-MM-DD_ddd") %>]] >> 

## 💡 Reminders

> [!DANGER] Today's Highlight
> %% What am I most looking forward to today? %%

## 👀 Bird View
- ✅ Tasks
  ```dataview
	TABLE WITHOUT ID 
		(link(file.path, title)) as Title, 
		dateformat(due, "DD") AS Due, 
		startTime AS Start, 
		endTime AS End, 
		contacts AS Contacts
	FROM #task
	WHERE 
	(
			date(due) = date(<% tp.date.now("YYYY-MM-DD") %>) 
		OR 
			date(date) = date(<% tp.date.now("YYYY-MM-DD") %>)
		OR	
			date(scheduled) = date(<% tp.date.now("YYYY-MM-DD") %>)
	)
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
	FROM #meeting
	WHERE 
	(
		date(due) = date(<% tp.date.now("YYYY-MM-DD") %>)
		or
		date(scheduled) = date(<% tp.date.now("YYYY-MM-DD") %>)
		OR
		date(date) = date(<% tp.date.now("YYYY-MM-DD") %>)
	)
	AND !contains(file.path, "99. Hidden") 
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
	FROM #note
	WHERE 
		(
			date(due) = date(<% tp.date.now("YYYY-MM-DD") %>)
		OR
			date(scheduled) = date(<% tp.date.now("YYYY-MM-DD") %>)
		OR 
			date(date) = date(<% tp.date.now("YYYY-MM-DD") %>)
		)
	AND 
		!contains(file.path, "99. Hidden") 
	AND 
		status != "#canceled" AND status != "#done"
	AND 
		!archived 
	SORT createdAt asc
   ```
- 🙌 Habit Tracker
	- [ ] 有氧锻炼 30 分钟 🔁 every day 
	- [ ] 器械锻炼 5 组 🔁 every day 
	- [ ] 视频学习 30 分钟  🔁 every day 
	- [ ] 有效阅读 15 分钟 🔁 every day 

## 💦 Efforts

```dataview
TABLE WITHOUT ID 
	(link(file.path, title)) as Title, 
	dateformat(due, "DD") AS Due, 
	startTime AS Start, 
	endTime AS End
FROM ""
WHERE 
	(
		date(due) = date(<% tp.date.now("YYYY-MM-DD") %>) 
	OR 
		date(date) = date(<% tp.date.now("YYYY-MM-DD") %>)
	OR
		date(scheduled) = date(<% tp.date.now("YYYY-MM-DD") %>)
	)
AND 
	!contains(file.path, "99. Hidden") 
AND (contains(file.tags, "#task") OR contains(file.tags, "#meeting") OR contains(file.tags, "#note"))
AND !archived 
AND status = "#done"
SORT startTime asc
```

## 📦 Archived
```dataview
TABLE WITHOUT ID 
	(link(file.path, title)) as Title,
	scheduled as Scheduled,
	due AS Due, 
	startTime AS Start, 
	endTime AS End
FROM ""
WHERE 
	(contains(tags, "#task") or contains(tags, "#meeting") or contains(tags, "#note")) 
AND 
	(
		date(due) = date(<% tp.date.now("YYYY-MM-DD") %>) 
	OR 
		date(date) = date(<% tp.date.now("YYYY-MM-DD") %>)
	OR
		date(scheduled) = date(<% tp.date.now("YYYY-MM-DD") %>)
	)
AND archived 
AND !contains(file.path, "99. Hidden")
SORT createdAt asc
```