# Agent: 工作负载与映射策略 Agent

## 1. 负责模块
- `workload/graph.py`, `workload/loader.py`
- `mapping/partitioner.py`, `mapping/tiler.py`
- `examples/workloads/*`

## 2. 模块目标
- 将 workload 描述解析为 DAG，并完成 op 到目标后端（ACIM/DIGITAL）的分配和 tile 粒度切分。

## 3. 当前已完成内容
- `WorkloadGraph` 已支持拓扑排序、前驱/后继关系构建和环检测。
- `load_workload` 支持 JSON/YAML 输入，能生成 `OpNode` 列表。
- `RuleBasedPartitioner` 已按算子类型进行基础映射。
- `BlockTiler` 已按 tile 数切分 ops/bytes，并估算 ACIM shots。

## 4. 当前未完成内容
- 缺失 Greedy/负载均衡 partitioner，与设计文档目标不符。
- 缺少跨 op 的数据复用或通信感知切分策略（仅均分切块）。
- `TileWorkItem.meta` 未承载任何 profile/布局信息。
- 无 workload schema 校验（字段缺失/负值/非法 dtype）。

## 5. 发现的问题
- 文档要求支持 Rule-based + Greedy-balancer，对比实验接口，但代码只实现 Rule-based。
- `BlockTiler` 可能生成大量空工作块（当 `num_tiles > ops`），造成 runtime 任务膨胀。
- `chiplet_hetero_sim/workload/*` 与顶层 `workload/*` 重复实现，且 package 版本为骨架，存在维护分叉风险。

## 6. 下一阶段任务清单
- [ ] 实现 `GreedyBalancerPartitioner`（目标最小化 `max(acim_time, digital_time)`，并考虑通信惩罚项）。
- [ ] 为 `load_workload` 增加 schema 校验与错误信息（建议引入 dataclass 校验层或手写校验函数）。
- [ ] 优化 `BlockTiler.tile()`：跳过零工作分块，必要时按最小任务粒度重分块。
- [ ] 扩展 `TileWorkItem.meta`，填充 `dtype`、op_type、估算访存比等字段，供 runtime 和 report 消费。
- [ ] 增加映射回归用例：同一 workload 下 Rule-based 与 Greedy 输出不同 mapping 且指标可比较。

## 7. 优先级建议
- P0: Greedy partitioner + workload 校验
- P1: tiler 任务粒度优化
- P2: profile 信息扩展

## 8. 依赖与协作关系
- 依赖 Agent-平台建模提供稳定的性能估算接口。
- 依赖 Agent-架构调度返回 per-op/per-task 时延，作为 Greedy 反馈信号。
- 输出交付给 Agent-报告统计用于 mapping 对比报告。

## 9. 备注
- “空工作块”问题为根据当前 `split()` 行为推断，在小算子/大 tile 数配置下风险更高。
