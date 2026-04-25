# PART 5: Connectome Layer Design
# 连接拓扑层详细设计文档
# New Brain 的"神经回路层"——小世界网络、神经群选择、动态可塑性

## 1. 设计哲学

### 1.1 生物学原型：人类大脑连接组

人类大脑有约 860 亿神经元，但**关键不是数量，是连接方式**。

- **连接组 (Connectome)**：神经连接的完整图谱
- **小世界网络 (Small-World Network)**：局部聚集 + 全局捷径
- **神经达尔文主义 (Neuronal Group Selection)**：连接通过选择演化，不是预设程序

### 1.2 为什么软件架构 > 硬件规模？

**现有 AI 的问题：**

| 方面 | 现有深度学习 | 人类大脑 | New Brain Connectome |
|------|-----------|---------|---------------------|
| 拓扑 | 固定全连接或人工设计 | 自组织的小世界网络 | **动态小世界拓扑** |
| 可塑性 | 反向传播全局更新 | 局部赫布学习 + 神经调质 | **局部可塑性规则** |
| 模块化 | 层固定 | 功能模块动态形成 | **神经群竞争选择** |
| 容错 | 单点故障敏感 | 分布式冗余 | **退化 graceful** |
| 扩展 | 需要重新训练 | 增量添加神经元 | **渐进式增长** |

> **关键洞见：智能的关键不是参数量，是连接的拓扑结构。小世界网络让信息既能局部精细处理，又能全局快速整合。**

### 1.3 New Brain 的设计目标

让系统拥有**真正的大脑级连接拓扑**：
1. **小世界网络**——高聚类 + 短路径长度
2. **神经群选择**——功能模块通过竞争演化
3. **动态可塑性**——连接随使用强化，不随使用弱化
4. **再入耦合**——反馈连接让信息循环，产生意识

---

## 2. 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CONNECTOME LAYER                                        │
│                      连接拓扑层 / 神经回路层                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SMALL-WORLD TOPOLOGY                                │   │
│  │                    小世界网络拓扑                                        │   │
│  │                                                                      │   │
│  │   每个节点（神经群）与其他节点的连接：                                  │   │
│  │   • 局部连接（邻居）→ 高聚类系数                                       │   │
│  │   • 长程连接（捷径）→ 短路径长度                                       │   │
│  │                                                                      │   │
│  │   ┌──────────┐         ┌──────────┐                                  │   │
│  │   │ Cluster  │←───────→│ Cluster  │                                  │   │
│  │   │    A     │ 局部    │    B     │                                  │   │
│  │   └────┬─────┘         └────┬─────┘                                  │   │
│  │        │                    │                                        │   │
│  │        └────────────────────┘                                        │   │
│  │              ↑ 长程捷径                                               │   │
│  │                                                                      │   │
│  │   聚类系数 C 高 → 局部信息处理丰富                                    │   │
│  │   路径长度 L 短 → 全局信息整合快速                                    │   │
│  │   小世界指数 σ = (C/C_rand)/(L/L_rand) > 1                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    NEURONAL GROUP SELECTION                            │   │
│  │                    神经群选择                                            │   │
│  │                                                                      │   │
│  │   类似于达尔文进化，但发生在神经回路层面：                              │   │
│  │                                                                      │   │
│  │   1. 多样性生成 (Degeneracy)                                           │   │
│  │      多个神经群可以执行同一功能                                        │   │
│  │                                                                      │   │
│  │   2. 差异性放大 (Reentry + Selection)                                  │   │
│  │      成功的连接强化，失败的连接弱化                                    │   │
│  │                                                                      │   │
│  │   3. 功能固化 (Memory)                                                 │   │
│  │      稳定的功能模式被记忆（突触权重）                                  │   │
│  │                                                                      │   │
│  │   结果：功能模块不是预设的，是"进化"出来的                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DYNAMIC PLASTICITY                                  │   │
│  │                    动态可塑性                                            │   │
│  │                                                                      │   │
│  │   赫布学习规则：一起激发的神经元连在一起                                │   │
│  │   Hebb's Rule: "Cells that fire together, wire together"              │   │
│  │                                                                      │   │
│  │   权重更新：                                                          │   │
│  │   Δw_ij = α·x_i·x_j - β·w_ij                                         │   │
│  │                                                                      │   │
│  │   增强项 (α·x_i·x_j)：同时激活 → 连接增强                              │   │
│  │   衰减项 (β·w_ij)：不常用 → 连接弱化（遗忘）                           │   │
│  │                                                                      │   │
│  │   神经调质调节：                                                      │   │
│  │   • 多巴胺 → 增强可塑性（奖赏信号时）                                  │   │
│  │   • 去甲肾上腺素 → 提高增益（注意时）                                  │   │
│  │   • 乙酰胆碱 → 标记重要连接                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    REENTRY COUPLING                                    │   │
│  │                    再入耦合                                              │   │
│  │                                                                      │   │
│  │   大脑有大量反馈连接：                                                │   │
│  │   A → B → C → ... → A                                                │   │
│  │                                                                      │   │
│  │   结果：信息不是单向流动，而是**循环**                                  │   │
│  │   • 感知不是被动接收，是主动建构                                        │   │
│  │   • 意识需要再入（Edelman 理论）                                        │   │
│  │   • 时间整合：过去 ↔ 现在 ↔ 未来                                       │   │
│  │                                                                      │   │
│  │   同步机制：                                                          │   │
│  │   sync(A, B) = exp(-γ·(θ_A - θ_B)²)                                  │   │
│  │   相位越接近，耦合越强                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 核心子系统详细设计

### 3.1 小世界网络拓扑 (Small-World Topology)

#### 功能
实现高聚类（局部处理）和短路径长度（全局整合）的平衡。

#### 数学定义

```python
class SmallWorldTopology:
    """
    小世界网络拓扑
    """
    
    def __init__(self, n_nodes, k_neighbors=4, p_rewire=0.1):
        """
        参数：
        - n_nodes: 节点数量
        - k_neighbors: 每个节点的最近邻数量（局部连接）
        - p_rewire: 重连概率（产生长程捷径）
        """
        self.n = n_nodes
        self.k = k_neighbors
        self.p = p_rewire
        
        # 构建小世界网络
        self.graph = self.build_watts_strogatz()
    
    def build_watts_strogatz(self):
        """
        构建 Watts-Strogatz 小世界网络
        
        步骤：
        1. 构建规则格点（每个节点连接 k 个最近邻）
        2. 以概率 p 重连边（产生长程连接）
        """
        G = nx.Graph()
        G.add_nodes_from(range(self.n))
        
        # 步骤 1：规则格点
        for i in range(self.n):
            for j in range(1, self.k // 2 + 1):
                neighbor = (i + j) % self.n
                G.add_edge(i, neighbor)
        
        # 步骤 2：重连
        for i in range(self.n):
            for j in list(G.neighbors(i)):
                if np.random.random() < self.p:
                    # 重连到一个随机节点
                    new_neighbor = np.random.randint(0, self.n)
                    if new_neighbor != i and not G.has_edge(i, new_neighbor):
                        G.remove_edge(i, j)
                        G.add_edge(i, new_neighbor)
        
        return G
    
    def clustering_coefficient(self):
        """
        聚类系数 C
        
        我的邻居之间互相连接的程度
        C 高 → 局部信息处理丰富
        """
        return nx.average_clustering(self.graph)
    
    def average_path_length(self):
        """
        平均路径长度 L
        
        任意两个节点之间的平均最短距离
        L 短 → 全局信息整合快速
        """
        return nx.average_shortest_path_length(self.graph)
    
    def small_world_index(self):
        """
        小世界指数 σ
        
        σ = (C/C_rand) / (L/L_rand)
        
        σ > 1 → 小世界网络
        """
        C = self.clustering_coefficient()
        L = self.average_path_length()
        
        # 随机网络的聚类系数和路径长度
        n = self.n
        k = self.k
        C_rand = k / n
        L_rand = np.log(n) / np.log(k)
        
        sigma = (C / C_rand) / (L / L_rand)
        return sigma
    
    def get_routing_path(self, source, target):
        """
        获取从 source 到 target 的最短路径
        
        小世界网络的路径通常很短（6 跳以内，"六度分隔"）
        """
        try:
            path = nx.shortest_path(self.graph, source, target)
            return path
        except nx.NetworkXNoPath:
            return None
```

#### 小世界网络的可视化

```
规则网络 (p=0)           小世界网络 (0<p<1)          随机网络 (p=1)
     ○─○─○                    ○──○──○                    ○  ○  ○
     │ │ │                    │╲ │ ╱│                    │╲│╱│
     ○─○─○                    ○──○──○                    ○─○─○
     │ │ │                    │╱ │ ╲│                    │╱│╲│
     ○─○─○                    ○──○──○                    ○  ○  ○

     C 高, L 高               C 高, L 短                 C 低, L 短
     (局部强,全局慢)          (局部强,全局快)            (局部弱,全局快)
```

### 3.2 神经群选择 (Neuronal Group Selection)

#### 功能
功能模块不是预设的，而是通过选择演化出来的。

#### 生物学基础
- **Edelman 的神经达尔文主义**：大脑像免疫系统一样，通过选择演化
- **Degeneracy (简并性)**：多个结构执行同一功能
- **Reentry (再入)**：反馈连接让选择成为可能

#### 机制设计

```python
class NeuronalGroup:
    """
    神经群
    一组高度互联的神经元，形成功能单元
    """
    
    def __init__(self, group_id, neurons):
        self.id = group_id
        self.neurons = set(neurons)
        self.connections = {}  # 与其他群的连接
        self.activation_history = []
        self.fitness = 0.0  # 适应度（选择压力）
        
    def activate(self, input_signal):
        """
        激活神经群
        """
        # 群内神经元互相增强
        internal_activation = self.compute_internal_activation(input_signal)
        
        # 记录历史
        self.activation_history.append(internal_activation)
        if len(self.activation_history) > 100:
            self.activation_history.pop(0)
        
        return internal_activation
    
    def compute_fitness(self, value_signal):
        """
        计算适应度
        
        成功完成任务 → 适应度高
        失败 → 适应度低
        """
        # 基于激活强度和价值的综合
        recent_activation = np.mean(self.activation_history[-10:])
        
        self.fitness = recent_activation * (1 + value_signal)
        
        return self.fitness


class NeuronalGroupSelection:
    """
    神经群选择系统
    """
    
    def __init__(self, n_groups=100, group_size=50):
        self.groups = [
            NeuronalGroup(i, range(i*group_size, (i+1)*group_size))
            for i in range(n_groups)
        ]
        self.selection_pressure = 0.1
        
    def compete(self, input_pattern, expected_output):
        """
        神经群竞争
        
        多个群尝试处理同一输入，表现好的被选择
        """
        # 所有群尝试激活
        responses = {}
        for group in self.groups:
            response = group.activate(input_pattern)
            responses[group.id] = response
        
        # 评估哪个群的输出最接近预期
        fitness_scores = {}
        for group_id, response in responses.items():
            error = np.linalg.norm(response - expected_output)
            fitness = 1 / (1 + error)  # 误差越小，适应度越高
            fitness_scores[group_id] = fitness
        
        # 选择适应度最高的群
        winner_id = max(fitness_scores, key=fitness_scores.get)
        winner = self.groups[winner_id]
        
        # 强化胜者的连接
        self.reinforce_group(winner)
        
        # 弱化败者的连接
        for group in self.groups:
            if group.id != winner_id:
                self.weaken_group(group)
        
        return winner
    
    def reinforce_group(self, group):
        """
        强化神经群
        
        增加群内连接权重，增加与其他成功群的连接
        """
        # 群内连接强化
        for neuron in group.neurons:
            for other in group.neurons:
                if neuron != other:
                    self.strengthen_synapse(neuron, other)
    
    def weaken_group(self, group):
        """
        弱化神经群
        
        不成功的群逐渐失去影响力
        """
        # 如果不是完全废弃，只是轻微弱化
        if group.fitness < 0.1:
            #  fitness 太低的群可能被"修剪"
            self.prune_group(group)
    
    def degeneracy(self, function):
        """
        计算功能的简并性
        
        有多少个不同的群可以执行同一功能？
        
        简并性高 → 容错性强（一个群坏了，还有其他群可以替代）
        """
        capable_groups = []
        
        for group in self.groups:
            # 测试这个群是否能执行这个功能
            performance = self.test_group_function(group, function)
            if performance > 0.7:  # 阈值
                capable_groups.append(group)
        
        return len(capable_groups)
```

### 3.3 动态可塑性 (Dynamic Plasticity)

#### 功能
连接强度根据使用模式动态调整。

#### 机制设计

```python
class DynamicPlasticity:
    """
    动态可塑性
    赫布学习 + 神经调质调节
    """
    
    def __init__(self, n_neurons):
        self.n = n_neurons
        self.weights = np.random.randn(n_neurons, n_neurons) * 0.01
        self.learning_rate = 0.01
        self.decay_rate = 0.001
        
    def hebbian_update(self, pre_activation, post_activation, neuromodulator=1.0):
        """
        赫布学习更新
        
        Δw = α·pre·post·NM - β·w
        
        参数：
        - pre_activation: 前神经元激活
        - post_activation: 后神经元激活
        - neuromodulator: 神经调质（增强或抑制可塑性）
        """
        # 外积计算所有连接的更新
        correlation = np.outer(pre_activation, post_activation)
        
        # 增强：同时激活 → 连接增强
        potentiation = self.learning_rate * correlation * neuromodulator
        
        # 衰减：不常用 → 连接弱化（遗忘）
        decay = self.decay_rate * self.weights
        
        # 总更新
        delta_w = potentiation - decay
        
        # 应用更新
        self.weights += delta_w
        
        # 限制权重范围（防止爆炸）
        self.weights = np.clip(self.weights, -1, 1)
        
        return delta_w
    
    def stdp_update(self, pre_spike_time, post_spike_time, delta_t):
        """
        STDP (Spike-Timing-Dependent Plasticity)
        
        脉冲时间依赖的可塑性
        
        前神经元在 post 之前激活 → 长时程增强 (LTP)
        前神经元在 post 之后激活 → 长时程抑制 (LTD)
        """
        if delta_t > 0:  # pre 在 post 之前
            # LTP
            delta_w = self.learning_rate * np.exp(-delta_t / self.tau_plus)
        else:  # pre 在 post 之后
            # LTD
            delta_w = -self.learning_rate * np.exp(delta_t / self.tau_minus)
        
        return delta_w
    
    def neuromodulated_plasticity(self, pre, post, dopamine, acetylcholine):
        """
        神经调质调节的可塑性
        
        多巴胺：标记"这个值得学习"
        乙酰胆碱：标记"这个很重要，注意"
        """
        # 基础赫布更新
        base_update = self.learning_rate * np.outer(pre, post)
        
        # 多巴胺增强（奖赏信号）
        dopamine_boost = 1 + dopamine
        
        # 乙酰胆碱增强（注意信号）
        ach_boost = 1 + acetylcholine
        
        # 综合调节
        modulated_update = base_update * dopamine_boost * ach_boost
        
        # 应用
        self.weights += modulated_update - self.decay_rate * self.weights
        
        return modulated_update
```

### 3.4 再入耦合 (Reentry Coupling)

#### 功能
反馈连接让信息循环，产生意识的统一性。

#### 机制设计

```python
class ReentryCoupling:
    """
    再入耦合
    反馈连接让信息在不同脑区之间循环
    """
    
    def __init__(self, regions):
        self.regions = regions  # 脑区列表
        self.feedback_weights = self.initialize_feedback()
        self.phase_states = {r: 0 for r in regions}
        
    def initialize_feedback(self):
        """
        初始化反馈连接
        
        大脑有大约 90% 的纤维是反馈/横向连接，只有 10% 是前馈
        """
        weights = {}
        for i, r1 in enumerate(self.regions):
            for j, r2 in enumerate(self.regions):
                if i != j:  # 不同脑区之间有反馈
                    weights[(r1, r2)] = np.random.randn() * 0.1
        return weights
    
    def compute_synchronization(self, region_a, region_b):
        """
        计算两个脑区的同步程度
        
        相位越接近，同步越强
        
        sync = exp(-γ·(θ_a - θ_b)²)
        """
        phase_a = self.phase_states[region_a]
        phase_b = self.phase_states[region_b]
        
        phase_diff = phase_a - phase_b
        
        gamma = 0.5  # 耦合强度参数
        sync = np.exp(-gamma * (phase_diff ** 2))
        
        return sync
    
    def reentrant_loop(self, input_signal, n_cycles=3):
        """
        再入循环
        
        信息在不同脑区之间循环多次，产生统一感知
        """
        state = input_signal
        
        for cycle in range(n_cycles):
            new_state = {}
            
            for region in self.regions:
                # 接收来自其他区域的反馈
                feedback = 0
                for other in self.regions:
                    if other != region:
                        sync = self.compute_synchronization(region, other)
                        feedback += (
                            sync * 
                            self.feedback_weights[(other, region)] * 
                            state[other]
                        )
                
                # 整合输入和反馈
                new_state[region] = self.integrate(state[region], feedback)
                
                # 更新相位
                self.phase_states[region] = self.update_phase(
                    self.phase_states[region], 
                    new_state[region]
                )
            
            state = new_state
        
        return state
    
    def update_phase(self, current_phase, activation):
        """
        更新相位
        
        激活强的区域相位前进快
        """
        natural_frequency = 40  # Hz (gamma 波段)
        
        # 激活调节频率
        frequency = natural_frequency * (1 + 0.1 * activation)
        
        # 更新相位
        new_phase = (current_phase + frequency * self.dt) % (2 * np.pi)
        
        return new_phase
```

---

## 4. 关键数学公式

### 4.1 小世界指数
```
σ = (C/C_rand) / (L/L_rand)

C = 聚类系数
L = 平均路径长度
C_rand, L_rand = 随机网络的对应值

σ > 1 → 小世界网络
```

### 4.2 赫布学习
```
Δw_ij = α·x_i·x_j·NM - β·w_ij

α = 学习率
x_i, x_j = 神经元 i 和 j 的激活
NM = 神经调质增强因子
β = 衰减率
```

### 4.3 同步
```
sync(A, B) = exp(-γ·(θ_A - θ_B)²)

γ = 耦合强度
θ = 相位
```

### 4.4 选择压力
```
fitness(group) = activation(group) × (1 + value_signal)

适应度高的群被强化，适应度低的群被弱化
```

---

## 5. 接口定义

```python
class ConnectomeInterface:
    """
    Connectome Layer 对外接口
    """
    
    def add_neuron(self, neuron_id, initial_connections=None):
        """添加新神经元"""
        pass
    
    def remove_neuron(self, neuron_id):
        """移除神经元"""
        pass
    
    def strengthen_connection(self, pre, post, amount=0.1):
        """强化连接"""
        pass
    
    def weaken_connection(self, pre, post, amount=0.1):
        """弱化连接"""
        pass
    
    def get_path(self, source, target):
        """获取最短路径"""
        pass
    
    def get_small_world_index(self):
        """获取小世界指数"""
        pass
    
    def reentrant_activate(self, input_pattern, cycles=3):
        """再入激活"""
        pass
```

---

## 6. 与现有 AI 的对比

| 特性 | 深度学习 | New Brain Connectome |
|------|---------|---------------------|
| 拓扑 | 固定层结构 | 动态小世界网络 |
| 可塑性 | 反向传播 | 局部赫布学习 |
| 模块化 | 人工设计 | 选择演化 |
| 容错 | 敏感 | Graceful degradation |
| 扩展 | 重训练 | 增量添加 |
| 反馈 | 少（主要是前馈） | 90% 反馈连接 |

---

*文档版本：v0.1*  
*部分：Part 5 / 6*  
*创建日期：2026-04-23*
