# ChimeraSim：Chiplet 数模异构仿真器
需求与工程化设计文档

Project Name (English): ChimeraSim
版本：v0.4（细化需求 + 工程化接口 + 排期）
日期：2026-03-02
范围：形态C（Chiplet）—— ACIM（RRAM） + Digital（DMAC+DRAM） + NoP


# 1. 项目简介

ChimeraSim 是一个面向 chiplet 形态数模异构系统的离散事件仿真器，用于研究神经网络在 RRAM 模拟存内计算（ACIM）与数字计算（DMAC+DRAM）之间的自适应划分与负载均衡。

- ACIM（模拟侧）：权重常驻，适合线性算子（MVM/GEMM 分块），但吞吐受阵列并行度与 ADC/DAC 资源约束。
- Digital（数字侧）：DMAC 算力利用率高，覆盖算子更广，但权重/激活通常需要从 DRAM 访问，容易受带宽与排队影响。
- Chiplet（系统侧）：两侧通过 NoP（封装级互连）交换激活，通信与拥塞会反压计算。
仿真器以“简单实现 + 必备约束”为原则：实现层面允许采用线性代价模型与 FCFS 队列，但必须保留决定系统性能的资源争用与反压链路，从而为划分/负载均衡算法提供可信的评估环境。

## 1.1 命名说明（ChimeraSim）

- Chimera（奇美拉）：神话中的混合体，寓意模拟 ACIM 与数字 DMAC 两类完全不同计算范式在 chiplet 封装下组合成一个系统。
- Sim：强调本项目是 simulator-first 的工程，用于快速迭代映射与负载均衡策略。
# 2. 目标与非目标

## 2.1 目标（Must-Have）

- 可配置平台：ACIM chiplet（多 tile；每 tile 多阵列、多组 ADC/DAC、buffer、controller）与 Digital chiplet（多 tile；DMAC + local buffer + DMA/DRAM）。
- 系统级资源：NoP（跨 chiplet 通信）与 DRAM（数字侧访存）。
- 工作负载执行：输入为算子图（DAG）或层序列；输出端到端 latency/energy/throughput 与资源利用率、stall breakdown。
- 关键约束显式化：ACIM 并行度受 min(num_arrays, num_adc_groups, num_dac_groups) 限制；Digital 受 DRAM 带宽/排队限制，并支持 compute/mem overlap 开关。
- 支持划分与负载均衡实验：至少提供 Rule-based 与 Greedy-balancer 两类分配策略，并能对比其系统指标。
## 2.2 非目标（暂不做）

- 不执行真实数值运算（不传播真实 tensor）；以 ops/bytes/shots 等抽象指标建模。
- 不进行器件级电路仿真（非理想仅以参数化开销或误差预算进入 cost model）。
- 不实现完整编译器（MVP 使用固定规则 tiling 与 mapping；后续可扩展）。
- 不实现复杂 NoP/NoC 拓扑与路由（MVP 用单资源/单链路模型；后续可扩展）。
# 3. 功能概览

## 3.1 端到端输出（Report）

- Total latency（ns）/ energy（pJ）/ throughput（samples/s 或 tokens/s）。
- 资源利用率：ACIM tiles、Digital tiles、NoP、DRAM 的 busy/queue 统计。
- 瓶颈分解（stall breakdown）：comm_wait、dram_wait、resource_wait（ADC/DAC/Array/DMAC）与 dep_wait。
## 3.2 关键约束可观测性

- ACIM：吞吐受 arrays/ADC/DAC 资源最小值限制；可通过调整各自数量观察利用率与排队变化。
- Digital：DRAM 拥塞导致 compute 饥饿；overlap_enabled 切换将改变总时延与 stall 结构。
- NoP：跨 chiplet 激活搬运引入通信延时与排队，能直观看到通信反压导致的空转。
## 3.3 研究接口（用于负载均衡）

- Partitioner：op -> {ACIM, DIGITAL}（层级划分）。
- Tiler：op -> TileWorkItem[]（并行粒度与通信量暴露）。
- Runtime/Scheduler：依赖推进与任务插入（未来可扩展动态重划分与窗口自适应）。
# 4. 整体架构与执行模型

## 4.1 顶层组件

- WorkloadGraph：算子 DAG（OpNode：ops/bytes/dtype/shape + deps）。
- Mapping：Partitioner（分配）与 Tiler（分块）。
- Runtime：GraphRuntime（依赖推进，插入 CommTask/MemTask，提交到 chiplet）。
- Platform：ACIMChiplet、DigitalChiplet、NoPInterconnect、DRAM。
- Sim Core：SimEngine（事件）、ResourceServer（容量+队列）、StatsCollector（统计）。
## 4.2 执行流程（逐步）

1. 加载 PlatformConfig 与 WorkloadGraph。
1. Partitioner 生成 op->target 映射。
1. Runtime 按 DAG 依赖推进：对就绪 op，若输入来自另一 chiplet，插入 CommTask（bytes=in_bytes）并提交 NoP。
1. Tiler 将 op 拆分为多个 TileWorkItem；提交目标 chiplet，由 dispatcher 选择具体 tile。
1. ACIMTile：work -> shots；并行受 min(arrays, adc, dac) 约束（MVP 可用 shot_token 模型）。
1. DigitalTile：生成 MemTask 提交 DRAM（权重/激活/写回）；生成 compute task 提交 DMAC；按 overlap_enabled 合成总耗时。
1. 当 op 的所有 TileWorkItem 完成，标记 op done，解锁后继；直至所有节点完成。
1. 输出 Report：端到端指标 + 利用率 + stall breakdown + 可选 trace。
## 4.3 最小事件模型（建议）

```text
- Task：携带 bytes / ops / shots 等元信息
- ResourceServer：capacity + FCFS queue；服务时间由 CostModel 给出
- 完成回调：on_done(task, finish_time, energy) 驱动后继任务提交或 op 完成
```

# 5. 数据模型与接口（API 级定义）

## 5.1 Workload 数据结构

```text
@dataclass
class OpNode:
    op_id: str
    op_type: str                 # GEMM | CONV | MATMUL | NORM | ACT ...
    ops: int
    in_bytes: int
    w_bytes: int
    out_bytes: int
    dtype: str
    preds: list[str]
    succs: list[str]

class WorkloadGraph:
    def topological(self) -> list[str]: ...
    def get_op(self, op_id: str) -> OpNode: ...
```

## 5.2 TileWorkItem（并行基本单元）

```text
@dataclass
class TileWorkItem:
    work_id: str
    op_id: str
    target: str                 # ACIM | DIGITAL
    ops: int
    in_bytes: int
    w_bytes: int
    out_bytes: int
    shots: int = 0              # ACIM 使用（由 Tiler 或 profile 生成）
    meta: dict = field(default_factory=dict)
```

## 5.3 Task 类型（系统任务）

```text
@dataclass
class Task:
    task_id: str
    kind: str                   # COMM | MEM | ACIM_SHOT | DIGITAL_COMP ...
    bytes: int = 0
    ops: int = 0
    shots: int = 0
    src: str | None = None
    dst: str | None = None
    meta: dict = field(default_factory=dict)
```

## 5.4 ResourceServer（统一资源模型）

```text
class ResourceServer:
    name: str
    capacity: int

    def submit(self, task: Task, on_done: callable) -> None:
        # 入队；可用则启动；完成回调 on_done(task, finish_time_ns, energy_pj)
        ...

    def estimate(self, task: Task) -> tuple[int, float]:
        # (service_time_ns, energy_pj) 由 CostModel 提供
        ...

    def report(self) -> dict:
        # busy_time, queue_time, served_tasks, avg_queue_len, ...
        ...
```

## 5.5 策略接口（Partitioner / Tiler / Dispatcher）

```text
class Partitioner(Protocol):
    def assign(self, graph: WorkloadGraph, platform: "Platform") -> dict[str, str]:
        # op_id -> 'ACIM' | 'DIGITAL'
        ...

class Tiler(Protocol):
    def tile(self, op: OpNode, target: str, platform: "Platform") -> list[TileWorkItem]: ...

class TileDispatcher(Protocol):
    def choose_tile(self, tiles: list["BaseTile"]) -> int: ...
```

# 6. 平台组成与模块职责（从系统到 tile）

## 6.1 Platform 与系统资源

- NoPInterconnect：跨 chiplet 的通信资源（bytes -> latency/energy + queue）。
- DRAM：数字侧访存资源（bytes -> latency/energy + queue）。
- ACIMChiplet：多 ACIMTile；dispatcher 负责分配 tile。
- DigitalChiplet：多 DigitalTile；dispatcher 负责分配 tile。
## 6.2 ACIMTile（必须体现 arrays/ADC/DAC 约束）

MVP 推荐采用 shot_token 模型，以最小实现成本保留关键并行约束：

- parallel_shots = min(num_arrays, num_adc_groups, num_dac_groups)
- t_shot = t_dac + t_array + t_adc + t_accum
- 一个 TileWorkItem 拆成 shots 个 shot 任务，提交到 shot_token_srv（capacity=parallel_shots）。
后续如需更细，可将 Array/DAC/ADC 分别建模为独立 ResourceServer，并由 TileController 实现仲裁。

## 6.3 DigitalTile（DMAC + DRAM）

- 在提交 compute 前后生成 MemTask（读权重/必要激活/写回输出），通过 platform.dram 排队执行。
- DMACResource（capacity=num_mac_arrays 或等效 peak_ops_per_s）执行 DigitalCompTask（按 ops）。
- overlap_enabled：开启时总时间近似 max(t_mem, t_comp)，关闭时为 t_mem + t_comp。
## 6.4 Runtime（GraphRuntime）职责

- 依赖跟踪（ready queue）与 op 完成汇聚（所有 TileWorkItem 完成后 op done）。
- 跨 chiplet 插入 CommTask：当 op 输入来自另一 chiplet 时，先 NoP 传输 in_bytes。
- 投递到 chiplet：dispatcher 选择 tile；tile 完成回调推动 DAG 前进。
- 记录统计：资源 busy/queue，stall 归因，最终生成 Report。
# 7. 目录结构与文件说明（逐文件）

```text
chiplet_hetero_sim/
├── sim/
│   ├── engine.py
│   ├── task.py
│   ├── resource.py
│   ├── stats.py
│   └── types.py
├── workload/
│   ├── graph.py
│   ├── loader.py
│   └── profiles.py
├── platform/
│   ├── config.py
│   ├── platform.py
│   ├── interconnect.py
│   ├── memory.py
│   ├── chiplet.py
│   ├── acim_tile.py
│   └── digital_tile.py
├── mapping/
│   ├── partitioner.py
│   └── tiler.py
├── runtime/
│   └── scheduler.py
├── models/
│   └── cost_models.py
├── reporting/
│   ├── report.py
│   └── trace.py
└── examples/
    ├── configs/
    └── workloads/
```

## 7.1 sim/（事件、资源、统计）

- engine.py：离散事件引擎；提供 now/schedule/run；资源完成事件通过 schedule 驱动。
- task.py：统一 Task 数据结构与任务类型约定（COMM/MEM/ACIM_SHOT/DIGITAL_COMP）。
- resource.py：ResourceServer（capacity + FCFS queue）；所有硬件资源统一抽象。
- stats.py：StatsCollector；记录任务起止、能耗；输出 utilization 与 stall breakdown。
- types.py：单位与类型别名（TimeNs/Bytes/Ops/EnergyPj）。
## 7.2 workload/（工作负载）

- graph.py：WorkloadGraph 与 OpNode；DAG 拓扑与依赖关系。
- loader.py：从 JSON/YAML 加载工作负载；可扩展从 ONNX/FX 导出 profile。
- profiles.py：可选；把 shape->ops/bytes 的计算封装，供 loader/tiler 使用。
## 7.3 platform/（平台与 tile）

- config.py：PlatformConfig 与各 TileConfig；集中参数与默认值。
- platform.py：组装 Platform（ACIM/Digital/NoP/DRAM），并提供 report 汇总。
- interconnect.py：NoPInterconnect（bytes->lat/energy + queue）。
- memory.py：DRAM（bytes->lat/energy + queue）。
- chiplet.py：BaseChiplet + TileDispatcher（round-robin/shortest-queue）。
- acim_tile.py：ACIMTile（shots + arrays/ADC/DAC 并行约束；MVP shot_token）。
- digital_tile.py：DigitalTile（DMAC + DMA/DRAM；overlap 开关）。
## 7.4 mapping/（划分与分块）

- partitioner.py：Partitioner 接口与实现（RuleBased / GreedyBalancer）。
- tiler.py：Tiler 接口与实现（BlockTiler）；生成 TileWorkItem，并估算 ACIM shots。
## 7.5 runtime/（执行时调度）

- scheduler.py：GraphRuntime（依赖推进、CommTask 插入、提交 tile work、汇总 op 完成）。
## 7.6 models/（代价模型）

- cost_models.py：ACIM/Digital/NoP/DRAM 的 cost model 接口与线性实现；可替换为查表/分段模型。
## 7.7 reporting/（输出）

- report.py：Report 数据结构与 to_json；统一输出字段与格式。
- trace.py：可选事件 trace；用于调试与可视化（task start/end、队列长度变化等）。
## 7.8 examples/（示例）

- configs/：平台参数样例（ACIM/Digital/NoP/DRAM）。
- workloads/：toy 网络样例（MLP、简化 Transformer block 等）。
# 8. 配置文件规范（建议 YAML/JSON）

建议以 PlatformConfig 为中心提供一份可复现实验配置。字段示例如下：

```text
platform:
  acim_num_tiles: 8
  dig_num_tiles: 4
  nop:
    bandwidth_GBs: 256
    base_latency_ns: 50
    energy_pj_per_byte: 0.5
  dram:
    bandwidth_GBs: 128
    base_latency_ns: 80
    energy_pj_per_byte: 2.0
  acim_tile:
    num_arrays: 16
    num_adc_groups: 4
    num_dac_groups: 4
    t_dac_ns: 5
    t_array_ns: 10
    t_adc_ns: 20
    t_accum_ns: 5
    energy_pj_per_shot: 100
    in_buf_bytes: 1048576
    out_buf_bytes: 1048576
    buf_bw_GBs: 512
  dig_tile:
    num_mac_arrays: 2
    peak_ops_per_s: 2.0e12
    utilization: 0.7
    local_buf_bytes: 2097152
    buf_bw_GBs: 1024
    overlap_enabled: true
```

# 9. 指标、可观测性与验收标准

## 9.1 必须输出的指标

- 端到端：total_latency_ns、total_energy_pj、throughput。
- 资源利用率：ACIM tiles、Digital tiles、NoP、DRAM 的 busy_time/queue_time/utilization。
- stall breakdown：comm_wait、dram_wait、resource_wait（ADC/DAC/Array/DMAC）、dep_wait。
## 9.2 MVP 验收标准（可运行 + 可解释）

- 可加载至少一个 toy workload 与一个平台配置并完成仿真。
- 改变 ACIM 的 arrays/ADC/DAC 数量后，吞吐随 min(arrays,ADC,DAC) 单调变化且排队结构可解释。
- 收紧 DRAM/NoP 带宽后，Digital/系统端到端延时明显上升，并且 stall breakdown 中 dram_wait/comm_wait 占比上升。
- overlap_enabled 开关能改变 DigitalTile 的总时延合成逻辑（max vs sum），并反映在报告中。
- RuleBasedPartitioner 与 GreedyBalancerPartitioner 在至少一个工作负载上产生不同 mapping，且 Greedy 能降低 max(ACIM_time, Digital_time) 或总延时。
# 10. 测试与验证计划

## 10.1 微基准（必做）

- 单层 GEMM：固定 ops/bytes，验证 ACIM 并行度与 Digital 计算吞吐是否符合配置。
- DRAM 压力测试：增大 w_bytes，验证 dram_wait 是否上升。
- NoP 压力测试：强制跨 chiplet 搬运大激活，验证 comm_wait 是否上升。
## 10.2 小网络（建议）

- 3-6 层 MLP：观察不同划分对端到端延时与利用率的影响。
- 简化 Transformer block：MatMul/FFN -> ACIM；Norm/Act/其他 -> Digital；验证通信与内存瓶颈的相互作用。
# 11. 工作计划与排期（6 周 MVP）

排期从 2026-03-02（周一）开始，目标为可运行、可配置、可用于负载均衡算法迭代的 MVP。

| 阶段 | 日期 | 交付物 | 验收标准 |
| --- | --- | --- | --- |
| W1 核心骨架 | 2026-03-02 - 2026-03-08 | SimEngine + ResourceServer（capacity+FCFS）<br>Task/Stats 基础<br>WorkloadGraph + loader<br>工程目录与示例框架 | toy workload 可跑通；输出基础 JSON report |
| W2 NoP/DRAM | 2026-03-09 - 2026-03-15 | NoPInterconnect（bytes->lat/energy+queue）<br>DRAM（bytes->lat/energy+queue）<br>拥塞/排队统计<br>trace 钩子 | comm_wait/dram_wait 可观测；带宽收紧可见退化 |
| W3 ACIM chiplet | 2026-03-16 - 2026-03-22 | ACIMChiplet + dispatcher<br>ACIMTile（shot_token 模型）<br>参数化 arrays/ADC/DAC<br>ACIM cost model（t_shot, energy/shot） | 吞吐符合 min(arrays,ADC,DAC)；多 tile 线性扩展可验证 |
| W4 Digital chiplet | 2026-03-23 - 2026-03-29 | DigitalChiplet + dispatcher<br>DigitalTile（DMACResource）<br>DMARequester 发 MemTask 到 DRAM<br>overlap_enabled 支持 | DRAM 紧时 dram_wait 主导；overlap 开关影响总时延 |
| W5 Runtime + Mapping | 2026-03-30 - 2026-04-05 | GraphRuntime（依赖推进）<br>跨 chiplet CommTask 插入<br>BlockTiler 输出 TileWorkItem<br>RuleBasedPartitioner | 混合映射可运行；通信开销正确计入 |
| W6 基线负载均衡 | 2026-04-06 - 2026-04-12 | GreedyBalancerPartitioner（含通信/内存惩罚）<br>Report 完善（utilization + stall breakdown）<br>回归测试与示例补齐 | 结果可复现；基线负载均衡在基准上降低总时延或 max-side time |

# 12. 后续可选增强（Post-MVP）

- ACIM 细粒度资源模型：显式 DAC/ADC/Array ResourceServer + TileController 仲裁（替代 shot_token）。
- NoP 拓扑与多链路：mesh/torus、路由、QoS 与拥塞控制。
- 动态自适应：运行时窗口内重划分（基于队列长度与带宽遥测）。
- 精度/可靠性约束：为 ACIM ops 绑定误差预算模型，做 accuracy-constrained mapping。
