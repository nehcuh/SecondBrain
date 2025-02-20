---
createdAt: <% tp.date.now("YYYY-MM-DD HH:mm") %>
cssclasses:
  - kanban
tags:
  - "#resource"
---
## ✅ Tasks
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	createdAt AS "Created Time",
	dateformat(date, "DD") AS Date
FROM [[]]
WHERE !archived
AND contains(file.tags, "#task")
```

## 📒 Notes
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	createdAt AS "Created Time",
	tags AS Status
FROM [[]]
WHERE contains(tags, "#note") AND !archived
```

## ✂️ Clippings

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	createdAt AS "Created Time",
	status AS Status
FROM [[]]
WHERE contains(tags, "#clipping") AND !archived
```