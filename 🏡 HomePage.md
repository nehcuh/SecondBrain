---
cssclasses:
  - kanban
---
## 🎛️ 操作导航栏
- ⚡️ Quick-Todo
    - `button-task`
	- `button-meeting`
	- `button-clipping`
	- `button-inspiration`
- 📚 Quick-Notes
	- `button-notebook`
	- `button-handbook`
	- `button-readwise`
	- `button-common`
- 📦 Para
	- `button-project`
	- `button-area`
	- `button-resource`
- 🎯 OKR
	- `button-goal`
	- `button-milestone`

## 📥 Inbox
```dataview
TABLE WITHOUT ID 
	(link(file.path, title)) as Title, 
	dateformat(due, "DD") AS Due, 
	startTime AS Start, 
	endTime AS End
FROM #task OR #note
WHERE !project AND !area AND !resource
	AND !contains(file.path, "99. Hidden") 
	AND status != "#canceled" AND status != "#done"
	AND !archived 
	SORT createdAt asc
```
## 🧱 待办追踪
 - ✅ 今日事今日毕
	 ```dataview
	 TABLE WITHOUT ID 
		(link(file.path, title)) as Title, 
		dateformat(due, "DD") AS Due, 
		startTime AS Start, 
		endTime AS End, 
		contacts AS Contacts
	FROM #task
	WHERE (date(due) = date(today) OR date(scheduled) = date(today))
	AND !contains(file.path, "99. Hidden") 
	AND contains(file.tags, "#task")
	AND status != "#canceled" AND status != "#done"
	AND !archived 
	SORT createdAt asc
	 ```
- 🌂 未雨绸缪
  ```dataview
	 TABLE WITHOUT ID 
		(link(file.path, title)) as Title, 
		dateformat(due, "DD") AS Due, 
		startTime AS Start, 
		endTime AS End, 
		contacts AS Contacts
	FROM #task
	WHERE (date(due) > date(today) AND date(due) <= (date(today) + dur(7days)))
	AND !contains(file.path, "99. Hidden") 
	AND contains(file.tags, "#task")
	AND status != "#canceled" AND status != "#done"
	AND !archived 
	SORT createdAt asc
	```
- 📂 文档追踪 
   ```dataview
	TABLE WITHOUT ID 
		(link(file.path, title)) AS Title, 
		status AS Status,
		notebook AS Notebook,
		dateformat(due, "DD") AS Due
	FROM #note
	WHERE !contains(file.path, "99. Hidden") 
	AND contains(file.tags, "#note")
	AND status != "#canceled" AND status != "#done"
	AND !archived 
	SORT createdAt asc
	```
- 📅 会议追踪
  ```dataview
	TABLE WITHOUT ID 
		(link(file.path, title)) AS Title, 
		dateformat(due, "DD") AS Due
	FROM #meeting
	WHERE !contains(file.path, "99. Hidden")
	AND date(due) = date(today) 
	AND status != "#canceled" AND status != "#done"
	AND !archived 
	SORT createdAt asc
	```
## 🎈 温故知新
```dataview
	 TABLE WITHOUT ID 
		(link(file.path, title)) as Title,
		project AS Project,
		status AS Status
	FROM #notebook
	WHERE !contains(file.path, "99. Hidden") 
	AND status != "#canceled"
	AND !archived 
	SORT createdAt asc
```
## 🎲 PARA
- 🏗️ Project
  ```dataview
	 TABLE WITHOUT ID 
		(link(file.path, title)) as Title,
		dateformat(startDate, "DD") AS Start,
		dateformat(due, "DD") AS Due,
		status AS Status
	FROM #project
	WHERE !contains(file.path, "99. Hidden") 
	AND status = "#processing" OR status = "#waiting"
	AND !archived
	SORT createdAt asc
  ```
- 🏕️ Area
  ```dataview
	 TABLE WITHOUT ID 
		(link(file.path, title)) AS Title,
		rootArea AS RootArea
	FROM #area
	WHERE !contains(file.path, "99. Hidden")
	AND !archived
	SORT createdAt asc
  ```
- 🏞️ Resource
  ```dataview
   	 TABLE WITHOUT ID 
		(link(file.path, title)) AS Title
	FROM #resource
	WHERE !contains(file.path, "99. Hidden")
	AND !archived
	SORT createdAt asc
   ```
   

---