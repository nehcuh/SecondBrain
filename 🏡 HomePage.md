---
cssclasses:
  - dashboard
  - dashboard-ReadLineLength
---
# 🛠️ Quick Actions

- ✅ Task Actions
	```button
	name ✅ Capture Task
	type command
	action QuickAdd: ✅ Create Task
	```
	```button
	name 🔔 Create Meeting
	type command
	action QuickAdd: 🔔 Create Meeting
	```

- 📝 Note Actions
	```button
	name 📝 Create Note
	type command
	action QuickAdd: 📝 Create Note
	```

- 🏗️ Project Actions
	```button
	name 🏗️ Create Project
	type command
	action QuickAdd: 🏗️ Create Project
	```

- ⛰️ Area & Resource Actions
	```button
	name 🏔️ Create Area/Resource
	type command
	action QuickAdd: ⛰️ Create Area/Resource
	```
# 🤺 Tasks
- 💦 Today
	```dataview
	TABLE WITHOUT ID (link(file.path, title)) as Title, tags as Tags, Area/Resource, Project, due as Due
	WHERE (contains(tags, "#task") OR contains(tags, "#meeting")) AND date(due) = date(today) AND !done AND !contains(file.path, "99. Hidden") AND !Archived SORT due asc
	```

- 📅 Within A Week
	%% tasks due within a week from today (not included) %%
	```dataview
	TABLE WITHOUT ID (link(file.path, title)) as Title, tags AS Tags, Area/Resource, Project, due AS Due FROM "" 
	WHERE (contains(tags, "#task") OR contains(tags, "#meeting")) AND date(due) > date(today) AND (date(due) <= date(today) + dur(7 days)) AND !done AND !Archived AND !contains(file.path, "99. Hidden") SORT due asc
	```
- ❗Dued Tasks
	```dataview
	TABLE WITHOUT ID (link(file.path, title)) as Title, tags as Tags, Area/Resource, Project, due as Due
	WHERE actionable AND (contains(tags, "#task") OR contains(tags, "#meeting")) AND date(due) < date(today) AND !done AND !contains(file.path, "99. Hidden") AND !Archived SORT due asc
	```
- ❓Someday
  ```dataview
	 TABLE WITHOUT ID (link(file.path, title)) as Title, created_at AS Created, tags AS Tags, scheduled AS Scheduled FROM "" WHERE !actionable AND contains(tags, "#task") AND contains(tags, "#task/someday") SORT scheduled asc
	```
- 📥 Tasks Inbox
	```dataview
	 TABLE WITHOUT ID (link(file.path, title)) as Title, created_at AS Created, tags AS Tags FROM "" WHERE !actionable AND contains(tags, "#task") AND !contains(tags, "#task/someday") AND !contains(tags, "#task/delegate") AND Project = null AND Area/Resource = null AND delegate = null AND !Archived AND !contains(file.path, "99. Hidden") SORT due asc
	```

# 🎯 Goals
- 🎉 Yearly Goals
  ```tasks
	not done
	due this year
	tags include #goal
	filter by function task.file.folder.includes("05. Areas & Resources")
    ```
- 📅 Monthly Goals
	```tasks
	not done
	due in this month
	tags include #goal
	filter by function task.file.folder.includes("05. Areas & Resources")
	```
- 🏗️ Project Goals
	```tasks
	not done
	tags include #goal
	filter by function task.file.folder.includes("04. Projects")
	```

# 🎛️Projects
## 🏗️ Processing

```dataview
Table Deadline, Area/Resource, Progress
FROM #project
WHERE !contains(file.path, "99. Hidden") AND status = "#🟩"
SORT Deadline asc
```

## 🧱 Waiting

```dataview
table Deadline, Area/Resource
FROM #project WHERE status = "#⬜️" AND !contains(file.path, "99 Hidden")
SORT Deadline asc
```

# 🧐 Creativity
## 📝 Notes

```dataview
Table  WITHOUT ID (link(file.path, title)) AS Title, created_at AS Created, tags AS Status, next_review AS Review
from ""
WHERE (contains(tags, "#note/🌱") OR  contains(tags, "#note/🌿"))
AND !contains(file.path, "99. Hidden")
sort created_at desc
```

## 💼References
```dataview
Table  WITHOUT ID (link(file.path, title)) AS Title, created_at AS Created, tags AS Status
from ""
WHERE contains(tags, "#note/💼")
AND !contains(file.path, "99. Hidden")
sort created_at desc
```
# 🛜 Quick Links
- 📁 PARA Method
	- 🚧 Projects
	- ⛰️ Areas/Resources
	- 🗑️ Archives
- 📈 Productivity
	- 📌 Kanbans
	- ♻️ Habits
	- 💭 Inspirations
	- 💬 Meetings
- 📅 Calendar
	- Daily Notes
	- Weekly Notes
	- Monthly Notes
	- Quarterly Notes
	- Yearly Notes
- 🕹️ Miscellaneous
	- Social Circle
	- Tasks delegate
