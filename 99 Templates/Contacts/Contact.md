---
type: contact
name: "<% tp.file.title.replace('👤 ', '') %>"
role: 
org: 
department: 
email: 
phone: 
wechat: 
tags: [contact]
createdAt: <% tp.date.now("YYYY-MM-DD") %>
archived: false
---

# <% tp.file.title.replace('👤 ', '') %>

> [!info] 基本信息
> **职位** `= this.role`
> **单位** `= this.org`
> **部门** `= this.department`
> **邮箱** `= this.email`
> **电话** `= this.phone`
> **微信** `= this.wechat`

## 关联

**参会记录：**
```dataview
TABLE date, time
FROM "05 Notes/Meetings"
WHERE contains(attendees, this.name) OR contains(attendees, this.file.name)
SORT date DESC
```

## 备注
