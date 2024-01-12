---
createdAt: 2024-01-12 17:07
area: 
cssclasses:
  - banner-image
---
>![banner-image] ![[资源.jpeg]]

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
name 🏞️ New Resource
type command
action QuickAdd: 🏞️ Create Resource
```
````
## ✅ Tasks
```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	createdAt AS "Created Time",
	dateformat(date, "DD") AS Date
FROM [[]]
WHERE !archived
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
