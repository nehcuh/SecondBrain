---
createdAt: 2024-01-12 17:06
startDate: 2024-01-12
endDate: 
project: 
area: 
resource: 
cssclasses:
  - banner-image
---
>![banner-image] ![[图书馆.jpeg]]
>

# ⚡️Actions

```button
name 📖 New Readwise Note
type command
action QuickAdd: 📖 Create A Readwise Note
```
```button
name 💡 New Handbook
type command
action QuickAdd: 💡 Create A Handbook
```
```button
name 📒 New Common Note
type command
action QuickAdd: 📒 Create A Common Note
```

# ♻️ Quick Summary

# 💡 Handbooks

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

# 📖 Readwise Notes

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

# 📒 Common Notes

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) as Title,
	tags AS Status
FROM [[]]
WHERE !archived 
AND contains(file.tags, "#common")
AND !contains(file.path, "99. Hidden") 
```
