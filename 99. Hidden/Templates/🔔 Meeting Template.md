---
title: <% tp.file.title.split("-")[0] %>
createdAt: <% tp.date.now("YYYY-MM-DD HH:mm") %>
allDay: 
startTime: <% tp.date.now("HH:mm") %>
endTime: 
date: <% tp.date.now("YYYY-MM-DD") %>
done: 
project: 
area: 
archived: 
location: 
tags:
  - "#meeting"
due: <% tp.date.now("YYYY-MM-DD") %>
scheduled: <% tp.date.now("HH:MM") %>
---
# 会议基础信息
1. 会议时间: `= dateformat(this.date,"DD") + " " + this.startTime + "-" + this.endTime`
2. 会议地点: `= this.location`
3. 会议主题:  `=this.title`
4. 参会人:
5. 背景资料:

# 会议纪要


# 会议结论


# 后续跟踪