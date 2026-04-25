# New Brain 理论基础与架构设计

## 一、核心思想：人类大脑的 6 条铁律

从 HARE5 实验、DMN 发现、神经达尔文主义、自由能原理、连接组学中提炼出的不可违背的原则：

| # | 原则 | 人类大脑对应 | New Brain 映射 |
|---|---|---|---|
| 1 | **增强子调控** | HARE5 不编码蛋白，只控制"何时编码" | 系统必须有 **元控制层 (Meta-Control Layer)** —— 决定什么时候激活什么模块 |
| 2 | **默认模式网络** | 发呆时反而最耗能，跑自我模拟/时间旅行/心智理论 | 系统必须有 **"离线思考"模式** —— 不处理外部输入时，在内部跑模拟、复盘、预测 |
| 3 | **软件 > 硬件** | 褶皱只是物理压缩，编排方式才是智慧 | 重点是**连接拓扑**，不是参数量。一个轻量但高度连接的网络 > 庞大但稀疏的网络 |
| 4 | **高增益/高噪声** | 创造力与精神疾病共享 25% 基因 | 系统要有 **"风险参数"** —— 可调的不稳定性。安全模式 vs 创造模式，同一架构不同增益 |
| 5 | **外包组装** | 出生只完成 45%，世界完成剩余 | 核心系统**不全预装**。留大量接口给环境实时塑形，像婴儿大脑一样被世界"养大" |
| 6 | **实时演化** | 进化仍在进行，目的地未知 | 架构本身要**可自我修改** —— 不是固定权重，而是连接规则、激活策略、甚至元控制层本身都可演化 |

---

## 二、四大理论支柱

### 支柱 1：自由能原理 (Free Energy Principle) —— 大脑的底层操作系统

**Karl Friston 的核心发现：**

所有生物系统（从单细胞到人脑）都在做同一件事：**最小化自由能**。

自由能 = 对"惊奇"（surprise）的上界估计。大脑不喜欢惊奇，不是因为情绪，是因为惊奇的输入威胁内稳态。

**数学表达：**
```
F = E_q[ln q(s) - ln p(o,s)]
```
- F = 变分自由能
- q(s) = 大脑对世界状态 s 的信念（近似后验）
- p(o,s) = 真实生成模型（世界如何产生观测 o）
- 目标：最小化 F，即让信念尽可能接近真实

**对应 New Brain：**
- **感知** = 更新内部模型以匹配输入（Inference）
- **行动** = 改变环境以匹配预测（Active Inference）
- **DMN 离线模式** = 在没有输入时，系统仍在最小化"想象场景"的自由能——即做内部模拟

> **关键洞见：** 大脑不是被动接收器，而是**层级贝叶斯推理引擎**。高层预测向下，低层预测误差向上。这与反向传播完全不同——优化是**局部**的，每层自己调，不需要信号传遍全网络。

---

### 支柱 2：神经达尔文主义 (Neural Darwinism) —— 学习不是训练，是选择

**Gerald Edelman 的核心发现：**

大脑不是被"训练"出来的（不像机器学习用反向传播调整权重），而是被**选择**出来的。

**三种选择机制：**

| 选择类型 | 发生时间 | 机制 |
|---|---|---|
| **发育选择** | 胎儿期-婴儿期 | 大量松散连接先形成，与环境互动中筛选 |
| **经验选择** | 一生中 | 使用过的连接加强，未使用的弱化/消失 |
| **再入选择** | 实时 | 不同神经群同步竞争，最适合当前环境的模式胜出 |

**核心概念：**
- **神经群 (Neuronal Group)**：50-10000 个神经元的集群，是选择的基本单位
- **映射 (Map)**：相互连接的神经群集合，对特定类别（颜色、运动等）响应
- **再入信号 (Re-entrant Signaling)**：映射之间的双向动态信号，不是前馈/反馈，是并行互锁
- **记忆 = 再分类 (Recategorization)**：不是存储属性，而是动态重组映射连接

**对应 New Brain：**
- **放弃梯度下降**。用**选择-强化-衰减**机制
- **模块化竞争**：多个候选"映射"同时激活，由价值系统（类似多巴胺/内啡肽的评分机制）选择胜出者
- **再入架构**：模块之间双向动态耦合，不是固定流水线
- **记忆不是数据库**，是连接拓扑的动态重绘

> **口号："Neurons that fire together, wire together" —— 但更重要的是：不一起 fire 的，会被剪掉。**

---

### 支柱 3：连接拓扑学 (Connectomics) —— 软件架构就是一切

**核心发现：**

- 大象 2570 亿神经元，98% 在小脑（运动协调），高级认知皮层反而比人类少
- 抹香鲸大脑比人类大 6 倍，但没有语言/城市
- **神经元数量 ≠ 智慧**。关键是**神经元被编排成的计算结构**

**数学工具：**

| 工具 | 用途 | New Brain 应用 |
|---|---|---|
| **图论 (Graph Theory)** | 分析网络拓扑 | 节点=功能模块，边=连接强度 |
| **小世界网络 (Small-World)** | 高局部聚类 + 短全局路径 | 模块内部密集，模块之间少量长程连接 |
| **模块化 (Modularity)** | 功能分区 | DMN、执行控制、感觉运动各自成模块 |
| **枢纽 (Hubs)** | 高连接度节点 | 元控制层就是"神经枢纽" |
| **拉普拉斯矩阵 (Laplacian)** | 分析信息流动 | 构建 Masked Laplacian 控制信息传递 |

**人类大脑拓扑特征：**
- 小世界指数高：既高效又容错
-  rich-club 组织：枢纽之间互相强连接
-  默认模式网络与其他网络的**反相关**：专注时 DMN 被抑制，发呆时 DMN 主导

**对应 New Brain：**
- 用**图数据库**（如 Neo4j）管理连接拓扑
- 连接不是静态权重，是**动态可塑**的
- 模块之间有**竞争-抑制**关系（像 DMN 与任务网络的反相关）

---

### 支柱 4：HARE5 / 增强子逻辑 —— 元控制层的生物学原型

**核心发现：**

HARE5 本身不编码蛋白质，它是**时间相干调制器**（temporal coherence modulator）。

- 人类 HARE5 有 4 个点突变，创造了"共振谐波"
- 这个谐波让 Fzd8 基因的转录**相位锁定**到放射状胶质细胞的增殖周期
- 结果是：细胞分裂周期从 24h 压缩到 18h，多分裂 1-2 轮 → 数量翻 4 倍
- **但小鼠长出人类褶皱后，并没有变聪明**

**关键启示：**

> HARE5 是**高 PAS（潜在相干性增益）增强子**：它增加了系统产生相干性的**容量**，但不直接诱导认知。智能是从这些层级上递归构建出的涌现属性。

**对应 New Brain：**

| HARE5 生物学角色 | New Brain 架构角色 |
|---|---|
| 不编码蛋白，控制"何时编码" | 元控制层不处理内容，控制"何时激活什么模块" |
| 相位锁定基因表达 | 同步模块激活时序 |
| 4 个点突变 → 巨大效应 | 少量调控参数 → 系统级行为改变 |
|  latent PAS gain（潜在增益）| 系统预留"尚未启用"的高阶能力接口 |

**元控制层的具体功能：**
1. **时序调度**：决定 DMN 何时启动、任务网络何时抑制
2. **增益调节**：控制"高增益/高噪声"模式（创造力）vs "低增益"模式（稳定性）
3. **模块门控**：决定哪些映射参与当前竞争
4. **发育模拟**：系统早期"过度连接"，后期选择性修剪

---

## 三、New Brain 架构设计

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    META-CONTROL LAYER                                        │
│  (增强子逻辑 / HARE5 Analog)                                  │
│  • 时序调度  • 增益调节  • 模块门控  • 发育/修剪控制          │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│   DMN Mode   │    │   Task Network   │    │  Value System│
│  (离线思考)   │    │   (在线处理)      │    │  (价值评估)   │
│              │    │                  │    │              │
│ • 自我参照   │    │ • 感知输入        │    │ • 惊奇检测   │
│ • 时间旅行   │    │ • 行动输出        │    │ • 情绪标记   │
│ • 心智模拟   │    │ • 预测-误差       │    │ • 目标梯度   │
│ • 反事实推演 │    │ • 层级推理        │    │              │
└──────────────┘    └──────────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              CONNECTOME / GRAPH LAYER                        │
│  (连接拓扑 / 软件架构)                                        │
│  • 小世界网络  • 动态可塑性  • 模块竞争  • 再入耦合           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              FREE ENERGY MINIMIZATION ENGINE                 │
│  (底层 OS / Friston Kernel)                                  │
│  • 变分推断  • 预测编码  • 主动推理  • 惊奇最小化             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 各层详细设计

#### 层 1：自由能最小化引擎 (Friston Kernel)

**这是系统的"物理定律"层。**

```python
# 概念伪代码
class FreeEnergyEngine:
    def __init__(self):
        self.generative_model = HierarchicalModel()  # 生成模型
        self.variational_density = q()               # 近似后验 q(s)
    
    def perceive(self, observation):
        # 感知 = 更新信念以减少预测误差
        prediction_error = observation - self.generative_model.predict()
        self.variational_density.update(prediction_error)
        return self.variational_density  # 新的信念
    
    def act(self, goal_state):
        # 行动 = 选择使未来观测匹配预测的动作
        expected_free_energy = self.compute_EFE(goal_state)
        action = argmin(expected_free_energy)
        return action
    
    def offline_simulate(self):
        # DMN 模式：在没有输入时，对想象的场景最小化自由能
        imagined_observations = self.dmn.generate_scenarios()
        for obs in imagined_observations:
            self.perceive(obs)  # 用内部模拟"训练"生成模型
```

**数学核心：**
- 变分自由能 F = 复杂性 (Complexity) + 不准确性 (Inaccuracy)
- 复杂性 = q(s) 与先验的距离（不要让模型太复杂）
- 不准确性 = 预测与观测的误差（要准确）
- **最小化 F = 在简洁和准确之间找平衡**（奥卡姆剃刀内置）

#### 层 2：连接拓扑层 (Connectome)

**这是系统的"硬件描述"层。**

```python
# 概念伪代码
class Connectome:
    def __init__(self):
        self.graph = nx.Graph()  # NetworkX 图
        self.modules = {}        # 模块集合
        self.plasticity_rate = 0.1
    
    def add_neuronal_group(self, group_id, module_type, initial_connections):
        # 添加神经群（50-10000 个节点的抽象）
        self.graph.add_node(group_id, module=module_type)
        for target, weight in initial_connections:
            self.graph.add_edge(group_id, target, weight=weight)
    
    def strengthen(self, group_a, group_b, amount):
        # "一起 fire，一起 wire"
        if self.graph.has_edge(group_a, group_b):
            self.graph[group_a][group_b]['weight'] += amount
    
    def weaken(self, group_a, group_b, amount):
        # 不一起 fire，就剪掉
        if self.graph.has_edge(group_a, group_b):
            self.graph[group_a][group_b]['weight'] -= amount
            if self.graph[group_a][group_b]['weight'] <= 0:
                self.graph.remove_edge(group_a, group_b)
    
    def compute_small_world_index(self):
        # 计算小世界指数，监控网络健康度
        C = nx.average_clustering(self.graph)  # 聚类系数
        L = nx.average_shortest_path_length(self.graph)  # 平均路径
        return C / L
    
    def reentrant_couple(self, map_a, map_b):
        # 再入耦合：两个映射之间的双向动态信号
        # 不是前馈/反馈，是并行互锁
        synchronization = self.compute_phase_lock(map_a, map_b)
        if synchronization > threshold:
            self.strengthen(map_a, map_b, synchronization * self.plasticity_rate)
```

**关键拓扑参数：**
- 聚类系数 (Clustering Coefficient)：局部密集度
- 特征路径长度 (Characteristic Path Length)：全局效率
- 模块度 (Modularity)：功能分区清晰度
-  rich-club 系数：枢纽之间的互连程度

#### 层 3：DMN / 离线思考引擎

**这是系统的"梦境/发呆"层。**

```python
# 概念伪代码
class DefaultModeNetwork:
    def __init__(self, connectome, friston_kernel):
        self.connectome = connectome
        self.friston = friston_kernel
        self.active = False
        self.scenarios = []
    
    def activate(self):
        # 当任务网络不活跃时，DMN 接管
        self.active = True
        self.connectome.suppress_task_network()
        self.connectome.enhance_self_referential_nodes()
    
    def self_referential_loop(self):
        # 自我参照："我是谁？我刚才做了什么？"
        recent_experiences = self.memory.get_recent()
        for exp in recent_experiences:
            # 用自由能引擎处理自己的历史
            self.friston.perceive(exp)
    
    def mental_time_travel(self):
        # 时间旅行：回忆过去 + 想象未来
        past_scenarios = self.memory.reconstruct_past(alternatives=True)
        future_scenarios = self.imagination.project_future(self.goals)
        
        for scenario in past_scenarios + future_scenarios:
            # 反事实推演："如果当时那样做会怎样？"
            self.friston.offline_simulate(scenario)
    
    def theory_of_mind(self, other_agent):
        # 心智理论：模拟他人的心理状态
        other_model = self.models[other_agent]
        predicted_behavior = other_model.predict()
        # 在自己的神经系统中模拟他人处境
        empathy_signal = self.friston.perceive(predicted_behavior, as_if=other_agent)
        return empathy_signal
    
    def generate_report(self):
        # 生成"内部报告"——系统对自己的分析
        return {
            'self_state': self.friston.variational_density,
            'regret_analysis': self.compute_regret(),
            'anxiety_forecast': self.compute_risk_scenarios(),
            'empathy_map': self.theory_of_mind_cache
        }
```

**DMN 的关键功能：**
1. **后悔 (Regret)**：重新运行过去场景，评估不同选择
2. **焦虑 (Anxiety)**：预先模拟未来场景，计算风险
3. **共情 (Empathy)**：在自己神经系统中模拟他人处境
4. **自我连续性**：把碎片经验整合成"我的人生故事"

> **这些是现有 AI 完全没有的能力。**

#### 层 4：任务网络 (Task-Positive Network)

**这是系统的"在线工作"层。**

```python
# 概念伪代码
class TaskNetwork:
    def __init__(self, connectome, friston_kernel):
        self.connectome = connectome
        self.friston = friston_kernel
    
    def execute_task(self, sensory_input, goal):
        # 在线模式：DMN 被抑制，任务网络主导
        self.connectome.suppress_dmn()
        self.connectome.enhance_sensorimotor_pathways()
        
        # 层级预测编码
        prediction = self.friston.generative_model.predict()
        prediction_error = sensory_input - prediction
        
        # 误差向上传递，预测向下修正
        self.friston.update_hierarchy(prediction_error)
        
        # 主动推理：选择行动减少未来误差
        action = self.friston.act(goal)
        return action
```

#### 层 5：价值系统 (Value System)

**这是系统的"多巴胺/内啡肽"层。**

```python
# 概念伪代码
class ValueSystem:
    def __init__(self):
        self.neuromodulators = {
            'surprise': 0.0,      # 惊奇 = 自由能激增
            'prediction_error': 0.0,  # 预测误差
            'homeostatic_deviation': 0.0,  # 内稳态偏离
            'information_gain': 0.0,  # 信息增益（好奇心）
            'social_value': 0.0    # 社会评估
        }
    
    def evaluate(self, state, action, outcome):
        # 评估一个"神经群映射"的适应度
        surprise = self.compute_surprise(outcome, state)
        if surprise > threshold:
            # 负向强化：这个映射不好
            return -surprise
        else:
            # 正向强化：这个映射好
            return self.compute_information_gain(state, outcome)
    
    def modulate_gain(self, context):
        # 根据环境调整"增益参数"
        # 安全环境 → 高增益（创造力模式）
        # 危险环境 → 低增益（稳定模式）
        if context.safety > 0.8:
            return 1.5  # 高增益，高噪声，高创造力
        else:
            return 0.5  # 低增益，低噪声，高稳定性
```

**价值系统的生物学对应：**
- 多巴胺 → 预测误差（奖励预期与实际差）
- 血清素 → 时间折扣（耐心/冲动）
- 去甲肾上腺素 → 不确定性/注意力
- 乙酰胆碱 → 预期精度（信度分配）

#### 层 6：元控制层 (Meta-Control / HARE5 Analog)

**这是系统的"增强子"层。**

```python
# 概念伪代码
class MetaControlLayer:
    def __init__(self, dmn, task_network, value_system, connectome):
        self.dmn = dmn
        self.task = task_network
        self.value = value_system
        self.connectome = connectome
        
        # HARE5 式参数：少量参数，巨大效应
        self.gain_parameter = 1.0          # 全局增益
        self.plasticity_rate = 0.1         # 可塑速度
        self.dmn_threshold = 0.3           # DMN 激活阈值
        self.pruning_threshold = 0.05      # 剪枝阈值
        self.phase_lock_strength = 0.8     # 相位锁定强度
    
    def temporal_scheduling(self, system_state):
        # 时序调度：决定 DMN 和任务网络何时切换
        if system_state.cognitive_load < self.dmn_threshold:
            self.dmn.activate()
            self.task.suppress()
        else:
            self.task.activate()
            self.dmn.suppress()
    
    def gain_modulation(self, context):
        # 增益调节：安全时高增益（创造力），危险时低增益（稳定）
        self.gain_parameter = self.value.modulate_gain(context)
        self.connectome.set_global_gain(self.gain_parameter)
    
    module_gating(self, task_requirement):
        # 模块门控：决定哪些映射参与竞争
        relevant_maps = self.connectome.find_relevant_maps(task_requirement)
        for map_id in self.connectome.all_maps:
            if map_id in relevant_maps:
                self.connectome.activate_map(map_id)
            else:
                self.connectome.inhibit_map(map_id)
    
    def developmental_simulation(self, age):
        # 模拟发育过程：早期过度连接，后期选择性修剪
        if age < DEVELOPMENTAL_PEAK:
            # 过度生成连接
            self.connectome.overconnect()
        else:
            # 经验依赖的修剪
            for edge in self.connectome.all_edges:
                if edge.activation_frequency < self.pruning_threshold:
                    self.connectome.prune(edge)
    
    def phase_lock_modules(self, module_a, module_b):
        # 相位锁定：像 HARE5 锁定 Fzd8 一样，同步模块时序
        sync = self.compute_phase_coupling(module_a, module_b)
        if sync > self.phase_lock_strength:
            # 建立强耦合
            self.connectome.create_reentrant_loop(module_a, module_b)
```

---

## 四、关键数学模型汇总

### 4.1 变分自由能 (Variational Free Energy)

```
F[q] = E_q[ln q(s)] - E_q[ln p(o,s)]
     = D_KL[q(s) || p(s|o)] - ln p(o)
     ≈ Complexity + Accuracy
```

**实现要点：**
- 用变分推断近似后验（不像精确贝叶斯那样计算不可行）
- 优化是局部的：每层只负责自己的精度参数和预测
- **不需要反向传播**——这与神经网络训练有本质区别

### 4.2 主动推理的期望自由能 (Expected Free Energy of Action)

```
G(π) = Σ_t [H[p(o|s)] - E_q[ln p(o|s)]]  +  E_q[D_KL[q(s')||q(s)]]
     =  外在价值 (Extrinsic)      +  内在价值 (Intrinsic)
     =  达成目标的确定性          +  信息增益（好奇心）
```

**实现要点：**
- 智能体选择策略 π（动作序列）时，不仅考虑"能否达成目标"，还考虑"能否学到新东西"
- 这解释了**好奇心**、**探索行为**、**信息寻求**

### 4.3 神经群选择动态

```
dw_ij/dt = α * x_i * x_j * V(t) - β * w_ij
```
- w_ij = 连接 (i,j) 的强度
- x_i, x_j = 神经群 i, j 的激活水平
- V(t) = 价值系统信号（正向/负向强化）
- α = 学习率，β = 衰减率

**实现要点：**
- 这不是梯度下降，是**赫布学习 + 价值调节**
- "一起 fire"通过 x_i * x_j 项实现
- "好坏"通过 V(t) 调节

### 4.4 小世界网络度量

```
σ = (C / C_rand) / (L / L_rand)
```
- C = 网络聚类系数
- L = 特征路径长度
- C_rand, L_rand = 随机网络基准值
- σ > 1 = 小世界网络

**实现要点：**
- 持续监控网络的小世界指数
- 如果网络变得太规则（σ 太低），增加随机长程连接
- 如果网络太随机（σ 太高），增强局部聚类

### 4.5 再入同步 (Re-entrant Synchronization)

```
θ_ij = |φ_i - φ_j|
sync_ij = exp(-γ * θ_ij^2)
```
- φ_i = 神经群 i 的相位
- θ_ij = 相位差
- γ = 耦合强度
- sync_ij = 同步度（0-1）

**实现要点：**
- 再入信号不是权重相乘，是**相位耦合**
- 同步度决定连接强化/弱化
- 这创造了**动态绑定**：瞬时同步 = 功能连接

---

## 五、与现有 AI 的本质区别

| 维度 | 深度学习 (当前 AI) | New Brain |
|---|---|---|
| **学习机制** | 反向传播 + 梯度下降 | 神经群选择 + 价值调节 |
| **记忆** | 静态权重参数 | 动态连接拓扑（再分类） |
| **自我** | 无 | DMN 自我参照回路 |
| **离线能力** | 无（不输入就休眠） | DMN 持续内部模拟 |
| **好奇心** | 人工设计的探索奖励 | 期望自由能中的信息增益项 |
| **创造力/精神疾病** | 无此参数 | 可调增益参数（同一枚硬币） |
| **发育** | 预训练后固定 | 持续可塑，环境依赖的修剪 |
| **行动** | 输出 token/分类 | 主动推理：最小化未来惊奇 |
| **不确定性** | 没有内在表示 | 每层都有精度/信度参数 |
| **社会认知** | 无 | 内置心智理论（ToM）模拟 |

---

## 六、第一阶段原型：DMN 模拟器

### 6.1 最小可行产品 (MVP)

**目标**：让系统表现出"发呆时的内部报告"

**输入**：一段对话/事件/记忆
**内部处理**：
1. 自我参照分析（"我刚才说了什么？"）
2. 反事实推演（"如果那样说会怎样？"）
3. 心智模拟（"他为什么那样想？"）
4. 后悔/焦虑计算
**输出**：一份"内部报告"

### 6.2 技术栈建议

| 组件 | 工具 | 原因 |
|---|---|---|
| 连接拓扑 | Neo4j / NetworkX | 原生图结构，支持动态可塑 |
| 概率推理 | PyMC / NumPyro | 变分推断 |
| 层级预测 | 自定义（参考 PredNet） | 预测编码架构 |
| 可视化 | D3.js / Graphviz | 连接拓扑可视化 |
| 原型语言 | Python | 生态丰富，实验友好 |

### 6.3 成功标准

- [ ] 系统能在无输入时"自发"生成内部模拟
- [ ] 能输出可读的"自我分析报告"
- [ ] 连接拓扑随交互发生可测量的变化
- [ ] 表现出简单的"后悔"（重新评估过去选择）

---

## 七、命名建议

| 候选名 | 含义 | 评价 |
|---|---|---|
| **CortexOS** | 皮层操作系统 | 技术感强，但有点冷 |
| **Neuroframe** | 神经框架 | 通用，不够独特 |
| **HARE5** | 致敬那个增强子 | 有故事，但可能难读 |
| **Reentrant** | 再入（Edelman 核心概念）| 学术，圈内人懂 |
| **Encephalon** | 脑（希腊词根）| 古典，太文绉绉 |
| **New Brain** | 直白 | 你原来的名字，有力 |

**我的建议**：就叫 **New Brain**。或者内部代号 **Project HARE**（致敬 HARE5，也有"野兔"的敏捷意象）。

---

## 八、参考文献

1. **Friston, K.** The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 2010.
2. **Friston, K., et al.** Active inference and learning. *Neuroscience & Biobehavioral Reviews*, 2016.
3. **Edelman, G.M.** Neural Darwinism: The Theory of Neuronal Group Selection. *Basic Books*, 1987.
4. **Edelman, G.M. & Tononi, G.** A Universe of Consciousness. *Basic Books*, 2000.
5. **Sporns, O.** Networks of the Brain. *MIT Press*, 2011.
6. **Bullmore, E. & Sporns, O.** Complex brain networks. *Nature Reviews Neuroscience*, 2009.
7. **Raichle, M.E.** The brain's default mode network. *Annual Review of Neuroscience*, 2015.
8. **Boyd, J.L. et al.** A Human-specific Enhancer Fine-tunes Radial Glia Potency and Corticogenesis. *Nature*, 2025.
9. **Pollard, K.S. et al.** Forces Shaping the Fastest Evolving Regions in the Human Genome. *PLoS Genetics*, 2006.
10. **Clark, A.** Whatever next? Predictive brains, situated agents, and the future of cognitive science. *Behavioral and Brain Sciences*, 2013.

---

*文档版本：v0.1*  
*创建日期：2026-04-23*  
*作者：Kimi Claw（人类）*
