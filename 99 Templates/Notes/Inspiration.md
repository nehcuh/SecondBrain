---
type: note
subtype: inspiration
title: "<% tp.file.title %>"
status: spark
area: ""
project: 
tags: [inspiration]
createdAt: <% tp.date.now("YYYY-MM-DD") %>
updatedAt: <% tp.date.now("YYYY-MM-DD") %>
archived: false
---

# 💡 Inspiration

> 一句话说清这个点子

## 为什么重要


## 怎么做

- [ ] 

## 关联项目

```dataview
TABLE WITHOUT ID file.link as "项目", status
FROM "03 Projects"  
WHERE contains(file.outlinks, this.file.link)
```

## 备注
