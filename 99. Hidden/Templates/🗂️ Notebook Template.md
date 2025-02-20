---
createdAt: <% tp.date.now("YYYY-MM-DD HH:mm") %>
startDate: <% tp.date.now("YYYY-MM-DD") %>
endDate: 
status: "#iteration"
project: 
area: 
resource: 
cssclasses:
  - kanban
archived: 
tags:
  - "#notebook"
---
## ♻️ Quick Summary

## 💡 Handbooks

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	project AS Project,
	area AS Area,
	resource AS Resource
FROM [[]]
WHERE contains(file.tags, "#handbook")
AND !contains(file.path, "99. Hidden")
```

## 📖 Readwise Notes

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) as Title,
	tags AS Status,
	nextReview AS NextReview
FROM [[]]
WHERE !archived 
AND contains(file.tags, "#readwise")
AND !contains(file.path, "99. Hidden") 
```

## 📒 Common Notes

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) as Title,
	tags AS Status
FROM [[]]
WHERE !archived 
AND contains(file.tags, "#common")
AND !contains(file.path, "99. Hidden") 
```
## 🖇️ References
