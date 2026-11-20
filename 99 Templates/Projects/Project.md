---
type: project
name: "<% tp.file.title.replace('🚀 ', '') %>"
status: planning
deadline: 
area: ""
goal: 
progress: 0
priority: medium
parent: 
tags: [project]
createdAt: <% tp.date.now("YYYY-MM-DD") %>
updatedAt: <% tp.date.now("YYYY-MM-DD") %>
archived: false
---

# 🚀 <% tp.file.title.replace('🚀 ', '') %>

> 🎯 项目目标：要交付什么？为什么重要？

## ✅ 成功标准

- [ ] 
- [ ] 
- [ ] 

## 📦 交付物

| 交付物 | 形式 | 状态 |
|--------|------|------|
| | 文档/代码/产品 | ⏳ |

## 🗺️ 里程碑

| 节点 | 截止 | 状态 |
|------|------|------|
| M1 | | ⏳ |
| M2 | | ⏳ |
| M3 | | ⏳ |

## 🎯 关联目标

```dataview
TABLE level, status, progress
FROM "01 Goals"
WHERE contains(file.outlinks, this.file.link) AND !archived
SORT level ASC
```

## ✅ 待办

```dataview
TABLE priority, status, due
FROM "06 Tasks"
WHERE contains(file.outlinks, this.file.link) AND !archived AND status != "done"
SORT priority ASC
```

## 🤝 相关会议

```dataview
TABLE date, time
FROM "05 Notes/Meetings"
WHERE contains(file.outlinks, this.file.link) AND !archived
SORT date DESC
```

## 📝 相关笔记

```dataview
TABLE subtype, updatedAt
FROM "05 Notes"
WHERE contains(file.outlinks, this.file.link) AND !archived
SORT updatedAt DESC
```

## 🌿 子项目

```dataviewjs
const children = dv.pages('"03 Projects"').where(p => p.type === "project" && p.parent === dv.current().name && !p.archived);

if (children.length === 0) {
  dv.el("p", "暂无子项目");
} else {
  const grid = dv.el("div", "", {cls: "sb-subarea-grid"});
  for (const c of children) {
    const card = grid.createEl("div", {cls: "sb-subarea-card"});
    card.style.cursor = "pointer";
    card.onclick = () => app.workspace.openLinkText(c.file.path, c.file.path, false);
    card.createEl("span", {text: "🚀", cls: "sb-subarea-icon"});
    card.createEl("span", {text: c.name, cls: "sb-subarea-name"});
    card.createEl("span", {text: (c.progress || 0) + "%", cls: "sb-subarea-desc"});
  }
}
```

## 📚 项目资料

| 类型 | 存放路径 | 说明 |
|------|----------|------|
| 📄 文档 | `_assets/文档/` | 需求、设计、评审材料 |
| 📎 附件 | `_assets/附件/` | 截图、数据、外部文件 |
| 🎬 记录 | `_assets/记录/` | 录屏、录音、会议纪要 |

> 资料直接拖进项目文件夹，`[[链接]]` 引用，项目结束一起归档

## 📝 备注
