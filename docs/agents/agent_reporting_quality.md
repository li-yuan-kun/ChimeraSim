# Agent: 报告统计与质量保障 Agent

## 1. 负责模块
- `reporting/report.py`
- `chiplet_hetero_sim/reporting/*`（骨架）
- 质量相关文档与测试目录（当前缺失）

## 2. 模块目标
- 输出可比较、可追踪的仿真报告；提供验证手段确保关键约束和指标正确。

## 3. 当前已完成内容
- `build_report` 已产出总时延、任务类型分布、每个 op 的起止时间。
- 基础任务轨迹（`runtime_result['tasks']`）已具备，可做二次分析。

## 4. 当前未完成内容
- 缺失总能耗、吞吐、资源利用率、stall breakdown 等文档要求指标。
- 缺少 trace 文件输出能力（仅有内存结构，无序列化接口）。
- 仓库缺少自动化测试（单元/集成/回归）。
- 缺少“文档-实现一致性”检查机制。

## 5. 发现的问题
- 文档定义 `reporting/trace.py` 作为事件追踪能力，但顶层 `reporting/` 中无 trace 实现。
- 设计文档的 MVP 验收项（ACIM并行约束、DRAM/NoP拥塞、overlap 开关影响）均无测试覆盖。
- `chiplet_hetero_sim/reporting/report.py` 与顶层 `reporting/report.py` 功能不一致（前者仅返回 title）。

## 6. 下一阶段任务清单
- [ ] 扩展 `reporting/report.py` 输出：`total_energy_pj`、`throughput`、资源利用率、stall breakdown。
- [ ] 新建 `reporting/trace.py`（顶层）并支持将任务事件导出 JSONL。
- [ ] 建立 `tests/`：至少覆盖 runtime 主链路、平台关键约束、report 字段完整性。
- [ ] 增加文档一致性检查清单：每次阶段巡检对照需求文档关键条目打勾。
- [ ] 将 `chiplet_hetero_sim/reporting/*` 标记为“未来迁移目录”或完成与顶层实现同步。

## 7. 优先级建议
- P0: 报告字段扩展 + 最小测试集落地
- P1: trace 导出
- P2: 文档一致性自动检查

## 8. 依赖与协作关系
- 依赖 Agent-架构调度和 Agent-平台建模提供更细粒度统计源数据。
- 输出交付给所有 Agent 作为性能归因与回归基线。

## 9. 备注
- 当前“质量保障”结论基于静态检查与目录状态推断（仓库未见测试文件）。
