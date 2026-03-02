# Agent: 架构与运行时调度 Agent

## 1. 负责模块
- `run_sim.py`
- `runtime/scheduler.py`
- `sim/engine.py`, `sim/resource.py`, `sim/stats.py`, `sim/task.py`

## 2. 模块目标
- 串起 workload -> mapping -> runtime -> report 的完整仿真主流程。
- 提供可扩展的调度与资源抽象，支持后续接入 DRAM/NoP/Tile 细粒度建模。

## 3. 当前已完成内容
- `GraphRuntime` 已具备 DAG 依赖推进、ready 队列、op 完成回填逻辑。
- 已有跨 chiplet 场景的 `COMM` 任务插入（基于前驱映射与 NoP 参数）。
- `BlockTiler` + runtime 能产出 tile 级任务时间戳并汇总为 `runtime_result`。
- `SimEngine`/`ResourceServer` 实现了独立的离散事件与 FCFS 容量模型（可复用）。

## 4. 当前未完成内容
- 当前 `GraphRuntime` 未使用 `sim/engine.py` 与 `sim/resource.py`，而是手写时间推进（模块能力未集成）。
- 运行时没有统一的任务状态机（`TaskState` 未在主流程消费）。
- 缺少事件 trace 钩子与调度策略可插拔接口。
- 无异常场景处理（非法 mapping、缺失 op、负载图空洞）与运行时校验。

## 5. 发现的问题
- 文档与代码不一致：设计文档定义的 `GraphRuntime + ResourceServer` 统一事件驱动架构尚未落地，当前是简化版串行调度。
- 存在双轨实现：`chiplet_hetero_sim/sim/*` 是骨架，`sim/*` 是可运行实现；职责重叠、边界不清。
- `run_sim.py` 依赖顶层包（`runtime/*`, `mapping/*`），与文档宣称的 `chiplet_hetero_sim/*` 主路径不一致。

## 6. 下一阶段任务清单
- [ ] 将 `runtime/scheduler.py` 改造成事件驱动：通过 `SimEngine.schedule()` + `ResourceServer.submit()` 驱动任务完成回调。
- [ ] 为 `GraphRuntime` 增加输入校验：检查 `mapping` 覆盖率、graph 拓扑合法性、目标枚举合法性。
- [ ] 在 `runtime_result` 中补齐 `stall_breakdown`（`dep_wait`/`comm_wait`/`resource_wait`）并统一命名。
- [ ] 抽象 runtime 的 `TaskFactory`（COMM/MEM/ACIM_SHOT/DIGITAL_COMP），避免 `_execute_op` 内部硬编码。
- [ ] 建立单测：覆盖拓扑推进、跨 chiplet 通信插入、并行 tile 完成汇聚。

## 7. 优先级建议
- P0: runtime 事件驱动统一（避免后续模块重复造轮子）
- P1: 校验与错误处理
- P2: trace 与可观测性扩展

## 8. 依赖与协作关系
- 依赖 Agent-平台建模提供 NoP/DRAM/Tile 提交接口。
- 依赖 Agent-映射策略提供稳定 `mapping` / `TileWorkItem` 结构。
- 输出交付给 Agent-报告统计用于报表与瓶颈分解。

## 9. 备注
- 双轨代码结论为根据当前实现推断：`chiplet_hetero_sim/*` 更像未来包化目录，`./runtime|sim|mapping` 才是当前入口链路。
