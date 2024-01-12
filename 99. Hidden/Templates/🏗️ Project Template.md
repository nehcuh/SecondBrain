---
createdAt: <% tp.date.now("YYYY-MM-DD HH:mm") %>
tags:
  - "#project"
status: waiting
due: <% tp.date.now("YYYY-MM-DD") %>
scheduled: <% tp.date.now("YYYY-MM-DD") %>
rootProject: 
area: 
goals:
---
# ✅ Tasks
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	dateformat(due, "DD") AS Due,
	dateformat(scheduled, "DD") AS Scheduled,
	dateformat(date, "DD") AS Start
FROM [[]]
WHERE 
	!contains(file.path, "99. Hidden")
AND contains(file.tags, "#task")
AND !archived AND !done
```

# 🔔 Meetings
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	dateformat(due, "DD") AS Due,
	dateformat(scheduled, "DD") AS Scheduled,
	dateformat(date, "DD") AS Start
FROM [[]]
WHERE 
	!contains(file.path, "99. Hidden")
AND contains(file.tags, "#meeting")
AND !archived AND !done
```

# 💦 Efforts
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	dateformat(due, "DD") AS Due,
	dateformat(scheduled, "DD") AS Scheduled,
	dateformat(date, "DD") AS Start
FROM [[]]
WHERE 
	!contains(file.path, "99. Hidden")
AND (contains(file.tags, "#meeting") OR contains(file.tags, "#task"))
AND !archived AND done
```
