---
createdAt: 2024-09-01 18:02
startDate: 2024-09-01
endDate: 
status: "#processing"
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
- [陈天 · Rust 编程第一课\_Rust\_rust\_语言\_陈天\_ct\_编程\_第一课\_get hands dirty\_编程语言\_Java\_C\_C++\_Python\_用户体验\_所有权\_生命周期\_性能\_内存安全\_内存管理\_思维转换\_类型系统-极客时间](https://time.geekbang.org/column/intro/100085301?tab=catalog)