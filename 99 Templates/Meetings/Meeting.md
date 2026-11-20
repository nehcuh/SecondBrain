---
type: meeting
title: "<% tp.file.title.replace('🤝 ', '').slice(0, -11) %>"
status: scheduled
date: <% tp.date.now("YYYY-MM-DD") %>
time: 
attendees: []
area: ""
project: 
tags: [meeting]
createdAt: <% tp.date.now("YYYY-MM-DD") %>
archived: false
---

# <% tp.file.title.replace('🤝 ', '').slice(0, -11) %>

## 议题


## 讨论记录


## 决议


## 行动项

> 每个行动项 → Cmd+P `📥 快速捕获` 建任务，双向链接

- [ ] 

## 跟踪

```dataview
TABLE status, due, priority
FROM "06 Tasks"
WHERE contains(file.outlinks, this.file.link) AND !archived
SORT status ASC
```
