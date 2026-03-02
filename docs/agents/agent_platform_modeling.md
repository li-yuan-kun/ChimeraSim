# Agent: 平台与硬件资源建模 Agent

## 1. 负责模块
- `platform/config.py`, `platform/platform.py`
- `platform/interconnect.py`, `platform/memory.py`
- `platform/acim_tile.py`, `platform/digital_tile.py`

## 2. 模块目标
- 提供可配置的 ACIM/Digital/NoP/DRAM 资源模型，支持队列、并发、时延、能耗统计。

## 3. 当前已完成内容
- `NoPInterconnect` 与 `DRAM` 具备 FCFS 单资源排队、基础延迟 + 带宽模型、能耗累计。
- `ACIMTile` 已实现 `parallel_shots = min(arrays, adc, dac)` 的关键约束和 shot-token 排程。
- `DigitalTile` 支持 `overlap_enabled` 开关（`max(mem, comp)` vs 顺序串行）。
- 各资源均提供 `report()` 输出基础利用率统计。

## 4. 当前未完成内容
- `PlatformConfig` 仅包含 `acim/digital/nop`，缺失 DRAM 与 ACIM/Digital 详细配置字段（与 tile 模块期望类型不匹配）。
- `Platform` 未真正组装 NoP/DRAM/tile 实例，目前仅暴露 tile 数属性。
- `ACIMTile` / `DigitalTile` 尚未被 `GraphRuntime` 主流程调用。
- 缺少 chiplet 级 dispatcher（round-robin/shortest-queue）与多 chiplet 抽象。

## 5. 发现的问题
- 严重接口断裂：`platform/acim_tile.py` 引用 `ACIMTileConfig`，`platform/digital_tile.py` 引用 `DigitalTileConfig`/`DRAMConfig`，但 `platform/config.py` 未定义这些类型。
- `platform/__init__.py` 导出了不存在的配置类，导入该包会触发 ImportError。
- 文档定义的 `bandwidth_GBs` 与当前 `PlatformConfig` 使用的 `bandwidth_bytes_per_ns` 单位不统一，且未提供转换层。

## 6. 下一阶段任务清单
- [ ] 重构 `platform/config.py`：补齐 `ACIMTileConfig/DigitalTileConfig/NoPConfig/DRAMConfig/PlatformConfig`，统一单位并做反序列化校验。
- [ ] 修复 `platform/__init__.py` 导出项，确保 `from platform import ...` 可用。
- [ ] 在 `platform/platform.py` 构造真实资源对象（`NoPInterconnect`, `DRAM`, tile 池）并提供统一 `report()`。
- [ ] 在 `runtime/scheduler.py` 接入 tile 与 DRAM/NoP 提交接口，打通端到端资源统计。
- [ ] 增加模型一致性测试：配置解析、单位换算、`overlap_enabled` 和 `parallel_shots` 行为断言。

## 7. 优先级建议
- P0: 配置类型修复 + package 导入修复
- P1: 平台对象组装与 runtime 集成
- P2: 模型参数校准与精细化

## 8. 依赖与协作关系
- 依赖 Agent-架构调度定义 runtime 调用契约。
- 依赖 Agent-测试验证补齐单元和集成用例。
- 输出交付给 Agent-报告统计用于资源利用率与能耗呈现。

## 9. 备注
- 多处不一致基于当前源码静态检查；未执行运行验证。
