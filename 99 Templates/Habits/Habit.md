---
type: habit
title: "<% tp.file.title %>"
goal: 
frequency: daily
tags: [habit]
createdAt: <% tp.date.now("YYYY-MM-DD") %>
archived: false
---

# <% tp.file.title %>

## 目标关联


## 执行标准


## 打卡记录

```dataviewjs
const file = dv.current();
const checkins = Array.isArray(file.checkins) ? file.checkins : [];
const entries = checkins.map(d => {
  const ds = typeof d === "string" ? d : dv.date(d).toFormat("yyyy-MM-dd");
  return { date: ds, intensity: 1 };
});
renderHeatmapTracker(this.container, {
  year: new Date().getFullYear(),
  entries,
  colors: { color1: ["#c6e48b","#40a02b"] },
  showCurrentDayBorder: true,
});
```
