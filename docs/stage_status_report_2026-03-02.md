# 阶段性工作汇报

## 1. 项目总体状态
- 当前仓库处于**MVP 早期阶段（约 30%~40%）**：顶层目录存在可运行的最小链路，但大量设计目标尚未落地。
- 架构层面存在双轨代码：
  - 可运行链路：顶层 `sim/ + runtime/ + mapping/ + platform/ + workload/ + reporting/`
  - 包化骨架：`chiplet_hetero_sim/*`（多数为占位实现）
- 该双轨状态导致“文档目标、目录设计、实际执行入口”三者不一致。

## 2. 本阶段已完成的核心工作
- 完成 workload 基础建模（`OpNode`, `WorkloadGraph`, topo + cycle 检查）。
- 完成 Rule-based 映射与 Block Tiler 基础切分。
- 完成 runtime 依赖推进和跨 chiplet 通信任务插入。
- 完成 NoP/DRAM/ACIM/Digital 的基础时延模型（但尚未主流程全量接入）。
- 已具备基础报表输出（总时延、task 类型统计、op 起止时间）。

## 3. 当前主要未完成项
- 统一事件驱动主流程（`SimEngine/ResourceServer` 与 runtime 尚未打通）。
- 平台配置与 tile 模块接口断裂（缺失 `ACIMTileConfig`/`DigitalTileConfig`/`DRAMConfig` 等）。
- Greedy 负载均衡策略缺失，仅有 Rule-based。
- 报告字段不足（能耗、吞吐、利用率、stall breakdown 缺失）。
- 自动化测试体系缺失。
- 包内实现 (`chiplet_hetero_sim`) 与顶层实现未同步。

## 4. 当前存在的关键问题
1. **文档与代码不一致**：设计文档以 `chiplet_hetero_sim/*` 为主，但 `run_sim.py` 使用顶层目录。
2. **接口断裂风险高**：`platform/__init__.py` 导入不存在配置类，说明平台模块当前不可稳定复用。
3. **模块重复维护风险**：同名模块双份实现，未来改动易出现行为漂移。
4. **验证闭环不足**：缺少测试使关键约束（min(arrays,adc,dac)、DRAM拥塞、overlap）无法持续保障。

## 5. 各 Agent 后续工作重点
### 架构与运行时调度 Agent
- 统一采用事件驱动调度模型，接入 ResourceServer。
- 增加 runtime 输入校验与错误处理。

### 平台与硬件资源建模 Agent
- 修复配置类型体系与包导出。
- 将 NoP/DRAM/Tile 资源对象接入 Platform 聚合层。

### 工作负载与映射策略 Agent
- 实现 GreedyBalancerPartitioner。
- 加强 workload schema 校验与 tiler 粒度控制。

### 报告统计与质量保障 Agent
- 扩展报告关键字段并落地 trace 导出。
- 建立最小单测 + 集成回归集合。

### 包结构治理与集成 Agent
- 明确单一源码路径并执行迁移计划。
- 改造入口脚本导入路径，清理双轨分叉。

## 6. 建议的下一阶段推进顺序
1. **先修平台配置与导入断裂（P0）**：否则 runtime 与 tile 集成会反复返工。
2. **再统一 runtime 事件驱动主链路（P0）**：形成稳定执行内核。
3. **并行推进 Greedy 映射与报告扩展（P1）**：确保能做策略对比实验。
4. **补测试与回归（P1）**：固化关键行为，降低后续重构风险。
5. **最后处理包结构迁移（P1/P2）**：在核心行为稳定后统一源码路径。

## 7. 风险与注意事项
- 若继续双轨开发，后续每个功能都需改两套代码，维护成本会指数上升。
- 目前 YAML 读取依赖 PyYAML，环境缺包时只能走 JSON；需在文档中明确。
- 建议所有 Agent 在下一阶段提交中同步更新本次新增的 `docs/agents/*.md` 与本汇报文档，保持“代码状态—任务状态”一致。
