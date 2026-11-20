---
generated: 2026-11-20 15:51
generator: scripts/gen_atlas.py
---

# 🗺️ Atlas — 全局拓扑

> ⚠️ 生成文件，勿手改。运行 `uv run scripts/gen_atlas.py` 或触发 AI 分诊（/sb-triage）时重建。
> 数据流：🎯 目标 → 📂 领域 → 🚀 项目 → ✅ 任务簇（聚合计数）。红色 = 含逾期任务的簇 / 活跃项目下游 / 待分诊积压。

## 拓扑

```mermaid
graph TD
    n1["🎯 长期目标-终身学习"]:::goal
    n2["🎯 2026 年度目标-健康第一"]:::goal
    n3["🎯 2026Q4 目标-养成晨跑习惯"]:::goal
    n4["📂 技术"]:::area
    n5["📂 健康"]:::area
    n6["📂 工作"]:::area
    n7["📂 个人成长"]:::area
    n8["🚀 搭建个人知识库"]:::proj
    n9["🚀 备战半程马拉松"]:::proj
    n3 --- n2
    n7 --> n8
    n5 --> n9
    tc1["✅ 任务×2"]:::task
    n7 --> tc1
    tc2["✅ 任务×2 ⚠️逾期"]:::hot
    n5 --> tc2
    tc3["✅ 任务×1"]:::task
    n6 --> tc3
    INBOX["📥 待分诊 ×1"]:::hot
    classDef goal fill:#2f6f4f,color:#fff;
    classDef area fill:#3b5b8f,color:#fff;
    classDef proj fill:#8f5b3b,color:#fff;
    classDef task fill:#4a4a5a,color:#ccc;
    classDef hot fill:#a03030,color:#fff;
```

## 体检摘要 · 2026-11-20 15:51

| 指标 | 值 |
|------|-----|
| 活跃目标 | 3 |
| 领域（含子领域） | 4 |
| 活跃项目 | 2 |
| 开放任务 | 7（逾期 1） |
| 待分诊（无领域/项目） | 1 |

