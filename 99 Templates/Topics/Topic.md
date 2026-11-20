---
type: topic
title: "<% tp.file.title %>"
status: active
area: ""
goal: 
progress: 0
tags: [topic]
createdAt: <% tp.date.now("YYYY-MM-DD") %>
updatedAt: <% tp.date.now("YYYY-MM-DD") %>
archived: false
---

# 📓 Topic

> 🎯 学习目标：学完这个主题要能做什么？

## 📖 章节

```dataview
TABLE WITHOUT ID file.link as "章节", dateformat(file.ctime, "MM-dd") as "创建"
FROM "05 Notes/Learning"
WHERE contains(file.outlinks, this.file.link) AND !archived
SORT file.ctime ASC
```

## ✅ 待办

```dataview
TABLE priority, status, due
FROM "06 Tasks"
WHERE contains(file.outlinks, this.file.link) AND !archived AND status != "done"
SORT priority ASC
```

## 📝 学习笔记

```dataview
TABLE subtype, updatedAt
FROM "05 Notes"
WHERE contains(file.outlinks, this.file.link) AND !archived
SORT updatedAt DESC
```

## 📚 资料库

| 类型 | 存放路径 | 说明 |
|------|----------|------|
| 📄 文献 | `_assets/资料/` | 论文、电子书、网页存档 |
| 💻 脚本 | `_assets/脚本/` | 练习代码、实验脚本 |
| 📎 附件 | `_assets/附件/` | 截图、数据、课后题 |

> 资料直接拖进主题文件夹，学完一起归档
