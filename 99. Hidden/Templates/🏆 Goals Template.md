---
year: 
project: 
area: 
tags:
  - "#goal"
scheduled:
---
# 🚏 Milestones

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	due AS Due
FROM [[]]
WHERE contains(file.tags, "#milestone")
```

# 🏗️ Related Projects

```dataview
TABLE WITHOUT ID
	(link(file.path, title)) AS Title,
	due AS Due
FROM [[]]
WHERE contains(file.tags, "#project")
```
