# PART 1: Meta-Control Layer Design
# 元控制层详细设计文档
# HARE5 Analog —— 系统的"增强子逻辑"

## 1. 设计哲学

### 1.1 生物学原型：HARE5

HARE5 的核心特征：
- **不编码任何蛋白质** → 不直接处理信息
- **只控制"何时激活"** → 时序调度
- **4 个点突变 → 巨大效应** → 少量参数改变系统行为
- **相位锁定基因表达** → 同步模块时序
- **增加系统相干性容量** → 潜在能力接口

### 1.2 New Brain 映射

元控制层是系统的"神经系统之上的神经系统"。它不直接参与认知内容，但决定：
- 什么时候 DMN 运行，什么时候 TPN 运行
- 系统的全局增益（安全模式 vs 创造模式）
- 哪些模块参与当前竞争
- 系统如何发育（先过度连接，后修剪）

**核心原则：少量参数，巨大效应。**

---

## 2. 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    META-CONTROL LAYER                                        │
│                    元控制层 / HARE5 Analog                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  TEMPORAL   │  │    GAIN     │  │   MODULE    │  │ DEVELOPMENT │        │
│  │  SCHEDULER  │  │  MODULATOR  │  │   GATE      │  │   ENGINE    │        │
│  │             │  │             │  │             │  │             │        │
│  │  时序调度器  │  │  增益调节器  │  │  模块门控   │  │  发育引擎   │        │
│  │             │  │             │  │             │  │             │        │
│  │ • DMN/TPN   │  │ • 全局增益  │  │ • 映射激活  │  │ • 过度连接  │        │
│  │   切换      │  │ • 噪声水平  │  │ • 竞争选择  │  │ • 经验修剪  │        │
│  │ • 相位锁定  │  │ • 创造力    │  │ • 资源分配  │  │ • 临界期    │        │
│  │   同步      │  │   模式      │  │             │  │   窗口      │        │
│  │             │  │             │  │             │  │             │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│         └────────────────┴────────────────┴────────────────┘               │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     CONTROL INTERFACE                                │   │
│  │                     控制接口                                         │   │
│  │                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │  DMN     │  │  TPN     │  │ Connectome│  │  Value   │           │   │
│  │  │ Engine   │  │ Engine   │  │  Layer   │  │ System   │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 核心参数表（HARE5 式"点突变"）

| 参数名 | 符号 | 默认值 | 范围 | 生物学对应 | 功能描述 |
|--------|------|--------|------|-----------|---------|
| DMN 激活阈值 | θ_dmn | 0.3 | [0, 1] | 默认模式网络切换阈值 | 认知负载低于此值时激活 DMN |
| 全局增益 | G_global | 1.0 | [0.5, 2.0] | 神经调质水平 | 系统整体激活强度 |
| 噪声系数 | σ_noise | 0.1 | [0, 0.5] | 神经元噪声 | 随机波动强度 |
| 可塑率 | η | 0.1 | [0.01, 0.5] | 突触可塑性 | 连接强度变化速度 |
| 剪枝阈值 | θ_prune | 0.05 | [0, 0.2] | 突触修剪阈值 | 低于此值的连接被删除 |
| 相位锁定强度 | κ_phase | 0.8 | [0, 1] | 神经振荡耦合 | 模块间同步强度 |
| 发育阶段 | τ_dev | 0.0 | [0, 1] | 发育时间线 | 0=胚胎期, 1=成熟期 |
| 风险偏置 | β_risk | 0.5 | [0, 1] | 风险寻求/回避 | 高=创造模式, 低=安全模式 |

**关键洞察：调整这 8 个参数中的任意一个，都能引发系统级行为改变。**
就像 HARE5 的 4 个点突变让小鼠大脑长出人类褶皱一样。

---

## 4. 四大子系统详细设计

### 4.1 时序调度器 (Temporal Scheduler)

#### 功能
控制 DMN（默认模式网络）和 TPN（任务正网络）之间的切换。

#### 生物学基础
- 人类大脑：专注时 DMN 被抑制，发呆时 DMN 主导
- 切换由**显著性网络 (Salience Network)** 负责
- 切换是无意识的、快速的

#### 状态机设计

```python
class TemporalScheduler:
    """
    时序调度器：管理 DMN ↔ TPN 的状态切换
    """
    
    STATES = {
        'TPN_DOMINANT': '任务模式主导',
        'DMN_DOMINANT': '默认模式主导', 
        'TRANSITIONING': '过渡状态',
        'BOTH_ACTIVE': '双激活（异常）',
        'BOTH_SUPPRESSED': '双抑制（休眠）'
    }
    
    def __init__(self, meta_params):
        self.theta_dmn = meta_params['dmn_threshold']  # DMN 激活阈值
        self.current_state = 'TPN_DOMINANT'
        self.cognitive_load_history = []  # 认知负载历史
        self.switch_count = 0  # 切换次数计数
        
    def compute_cognitive_load(self, system_state):
        """
        计算当前认知负载
        基于：输入复杂度、处理深度、资源占用
        """
        input_complexity = system_state.input_entropy
        processing_depth = system_state.hierarchy_depth
        resource_usage = system_state.active_modules / system_state.total_modules
        
        load = (0.4 * input_complexity + 
                0.3 * processing_depth + 
                0.3 * resource_usage)
        
        self.cognitive_load_history.append(load)
        return load
    
    def should_switch_to_dmn(self, load):
        """
        是否切换到 DMN 模式？
        条件：认知负载持续低于阈值
        """
        if len(self.cognitive_load_history) < 3:
            return False
            
        # 取最近3个时间步的平均负载
        recent_load = np.mean(self.cognitive_load_history[-3:])
        
        return recent_load < self.theta_dmn
    
    def should_switch_to_tpn(self, load, external_input_detected):
        """
        是否切换到 TPN 模式？
        条件：检测到外部输入 或 认知负载突增
        """
        if external_input_detected:
            return True
            
        if len(self.cognitive_load_history) < 2:
            return False
            
        # 认知负载突然增加（超过 20%）
        load_change = (load - self.cognitive_load_history[-2]) / self.cognitive_load_history[-2]
        return load_change > 0.2
    
    def switch(self, target_state):
        """
        执行状态切换
        包含：抑制旧网络 → 激活新网络 → 相位重对齐
        """
        print(f"[{datetime.now()}] State switch: {self.current_state} → {target_state}")
        
        if target_state == 'DMN_DOMINANT':
            self._suppress_tpn()
            self._activate_dmn()
            self._phase_align_dmn()
            
        elif target_state == 'TPN_DOMINANT':
            self._suppress_dmn()
            self._activate_tpn()
            self._phase_align_tpn()
            
        self.current_state = target_state
        self.switch_count += 1
    
    def _suppress_tpn(self):
        """抑制任务正网络"""
        for module in self.tpn_modules:
            module.gain *= 0.3  # 降低增益到 30%
            module.inhibited = True
    
    def _activate_dmn(self):
        """激活默认模式网络"""
        for module in self.dmn_modules:
            module.gain = 1.5  # 提高 DMN 增益
            module.inhibited = False
    
    def _phase_align_dmn(self):
        """
        DMN 相位对齐
        让 DMN 模块的振荡进入同步状态
        """
        for module in self.dmn_modules:
            module.reset_phase()
            module.target_phase = 0  # 对齐到 0 相位
            module.phase_lock_enabled = True
```

#### 切换策略图解

```
认知负载
   ↑
 1.0│                              _______
    │                    _______   /       \
    │          _______  /       \ /         \
 0.5│    _____/       \/         X           \_______
    │   /             /\        / \                  \
 0.3│--/-------------/  \______/   \-------------------  ← θ_dmn 阈值
    │  ↑ DMN         ↑ TPN       ↑ DMN
    │  激活          激活         激活
    └──────────────────────────────────────────→ 时间
    
外部输入
    │_____|        |____|     |________|
    └─────┘        └────┘     └────────┘
    TPN激活        TPN激活     TPN激活
```

---

### 4.2 增益调节器 (Gain Modulator)

#### 功能
动态调整系统的全局增益参数，控制"创造力模式" vs "安全模式"。

#### 生物学基础
- **高增益**：类似多巴胺高水平 → 探索、创新、冒险
- **低增益**：类似血清素主导 → 稳定、保守、精确
- **精神疾病**：增益失控 → 躁狂（过高）/ 抑郁（过低）
- **创造力**：适度高增益 + 可控噪声

#### 增益-风险模型

```python
class GainModulator:
    """
    增益调节器：控制全局增益和噪声水平
    实现"高增益/高噪声同一枚硬币"原则
    """
    
    def __init__(self, meta_params):
        self.G_global = meta_params['global_gain']      # 全局增益
        self.sigma = meta_params['noise_coefficient']    # 噪声系数
        self.beta_risk = meta_params['risk_bias']        # 风险偏置
        
        self.mode_history = []
        self.safety_assessment = SafetyAssessor()
        
    def assess_context_safety(self, environment):
        """
        评估环境安全性
        基于：历史成功率、环境熟悉度、资源充足度
        """
        success_rate = environment.recent_success_rate
        familiarity = environment.scene_recognition_score
        resource_level = energy / max_energy
        
        safety = (0.4 * success_rate + 
                 0.3 * familiarity + 
                 0.3 * resource_level)
        
        return safety
    
    def compute_optimal_gain(self, safety, task_requirement):
        """
        计算最优增益
        
        公式：
        G_optimal = G_base * (1 + α * safety * β_risk)
        
        其中：
        - G_base = 基础增益（默认 1.0）
        - α = 环境调节系数（默认 0.5）
        - safety = 环境安全性 [0, 1]
        - β_risk = 风险偏置 [0, 1]（高=喜欢冒险）
        
        逻辑：
        - 安全环境 + 高风险偏好 → 高增益（创造力模式）
        - 危险环境 + 低风险偏好 → 低增益（安全模式）
        - 安全环境 + 低风险偏好 → 中等增益（舒适区）
        - 危险环境 + 高风险偏好 → 危险！可能崩溃
        """
        alpha = 0.5
        
        # 核心公式
        G_optimal = self.G_global * (1 + alpha * safety * self.beta_risk)
        
        # 约束在安全范围
        G_optimal = np.clip(G_optimal, 0.5, 2.0)
        
        return G_optimal
    
    def compute_noise_level(self, G_optimal, creativity_requirement):
        """
        计算噪声水平
        
        公式：
        σ = σ_base * G_optimal * creativity_boost
        
        原则：
        - 增益越高，噪声越大（"高增益/高噪声同一枚硬币"）
        - 噪声不是故障，是创造力的来源
        - 但必须可控，不能失控
        """
        sigma_base = 0.05
        creativity_boost = 1.5 if creativity_requirement else 1.0
        
        sigma = sigma_base * G_optimal * creativity_boost
        sigma = np.clip(sigma, 0, 0.5)  # 上限约束
        
        return sigma
    
    def apply_gain(self, target_modules, G_optimal, sigma):
        """
        将增益应用到目标模块
        """
        for module in target_modules:
            # 设置增益
            module.gain = G_optimal
            
            # 注入可控噪声
            noise = np.random.normal(0, sigma, module.activation.shape)
            module.activation += noise
            
            # 记录模式历史
            self.mode_history.append({
                'timestamp': datetime.now(),
                'module': module.id,
                'gain': G_optimal,
                'noise': sigma,
                'mode': 'creative' if G_optimal > 1.3 else 'safe'
            })
    
    def emergency_dampening(self):
        """
        紧急降增益
        当系统检测到崩溃风险时（如循环思维、过度激活）
        """
        print("[EMERGENCY] Gain dampening activated!")
        self.G_global = 0.5
        self.sigma = 0.01
        
        # 所有模块降增益
        for module in self.all_modules:
            module.gain = 0.5
            module.noise_injection = 0
```

#### 增益-噪声关系图

```
噪声 σ
  ↑
0.5│                                    *
    │                                 *     *
0.3│                              *           *
    │                           *                 *
0.1│                        *                       *
    │                     *                             *
  0│__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__→ 增益 G
    0.5   0.8   1.0   1.2   1.5   1.8   2.0
    
    |←——安全区——→|←——创造区——→|←——危险区——→|
    
    安全区：G < 1.0, σ < 0.1    → 稳定、精确、保守
    创造区：G 1.0-1.5, σ 0.1-0.3 → 灵活、创新、适度冒险
    危险区：G > 1.5, σ > 0.3     → 可能躁狂、失控、崩溃
```

---

### 4.3 模块门控 (Module Gate)

#### 功能
决定哪些"神经群映射"参与当前认知竞争。

#### 生物学基础
- 大脑不会同时激活所有区域
- **注意力** = 选择性地增强某些映射，抑制其他映射
- **前额叶皮层** 负责这种门控
- 竞争失败的映射被抑制，但不删除

#### 门控机制设计

```python
class ModuleGate:
    """
    模块门控：选择参与当前任务的神经群映射
    实现"选择性注意"和"映射竞争"
    """
    
    def __init__(self, meta_params):
        self.all_maps = {}  # 所有可用映射
        self.active_maps = set()  # 当前激活的映射
        self.inhibited_maps = set()  # 被抑制的映射
        self.competition_history = []
        
    def relevance_scoring(self, task_requirement, map_candidate):
        """
        计算映射候选者的相关性得分
        
        基于：
        1. 语义相似度（内容与任务的匹配）
        2. 历史成功率（这个映射过去表现如何）
        3. 当前激活状态（已经活跃的更容易被选中）
        4. 连接强度（与当前活跃映射的连接紧密度）
        """
        semantic_sim = cosine_similarity(
            task_requirement.embedding, 
            map_candidate.embedding
        )
        
        history_score = map_candidate.success_rate
        activation_bias = 1.2 if map_candidate in self.active_maps else 1.0
        connection_strength = self.compute_connection_strength(
            map_candidate, self.active_maps
        )
        
        score = (0.3 * semantic_sim + 
                 0.3 * history_score + 
                 0.2 * activation_bias + 
                 0.2 * connection_strength)
        
        return score
    
    def run_competition(self, task_requirement, n_winners=5):
        """
        运行映射竞争
        
        步骤：
        1. 所有映射计算相关性得分
        2. 得分最高的 n 个映射胜出
        3. 胜出者被激活，其余被抑制
        4. 记录竞争结果用于学习
        """
        scores = {}
        for map_id, map_obj in self.all_maps.items():
            scores[map_id] = self.relevance_scoring(task_requirement, map_obj)
        
        # 排序，选前 N
        sorted_maps = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        winners = [m[0] for m in sorted_maps[:n_winners]]
        losers = [m[0] for m in sorted_maps[n_winners:]]
        
        # 激活胜出者
        for winner_id in winners:
            self.all_maps[winner_id].activate()
            self.active_maps.add(winner_id)
            self.inhibited_maps.discard(winner_id)
        
        # 抑制失败者
        for loser_id in losers:
            self.all_maps[loser_id].inhibit()
            self.inhibited_maps.add(loser_id)
            self.active_maps.discard(loser_id)
        
        # 记录
        self.competition_history.append({
            'task': task_requirement,
            'winners': winners,
            'losers': losers,
            'scores': scores
        })
        
        return winners
    
    def update_map_performance(self, map_id, outcome):
        """
        更新映射的表现历史
        用于未来的相关性评分
        """
        map_obj = self.all_maps[map_id]
        
        if outcome == 'success':
            map_obj.success_rate = 0.9 * map_obj.success_rate + 0.1 * 1.0
        elif outcome == 'failure':
            map_obj.success_rate = 0.9 * map_obj.success_rate + 0.1 * 0.0
        
        map_obj.usage_count += 1
```

---

### 4.4 发育引擎 (Development Engine)

#### 功能
模拟大脑的发育过程：早期过度连接 → 经验依赖的修剪。

#### 生物学基础
- 婴儿大脑：神经元数量接近成人，但连接密度是成人的 2 倍
- 2-3 岁：突触密度达到峰值
- 青春期：大量修剪，保留常用连接
- **关键期 (Critical Period)**：某些能力必须在特定时间窗口内发展

#### 发育模型设计

```python
class DevelopmentEngine:
    """
    发育引擎：模拟大脑的发育过程
    """
    
    def __init__(self, meta_params):
        self.tau = meta_params['development_stage']  # 发育阶段 [0, 1]
        self.theta_prune = meta_params['pruning_threshold']
        self.eta = meta_params['plasticity_rate']
        
        self.DEVELOPMENTAL_PEAK = 0.3  # 发育峰值（类似 2-3 岁）
        self.CRITICAL_PERIODS = {
            'language': (0.1, 0.5),      # 语言关键期
            'social': (0.2, 0.6),        # 社交关键期
            'sensory': (0.0, 0.3),       # 感觉关键期
        }
        
    def overconnect(self, connectome):
        """
        过度连接阶段
        在发育早期，大量随机连接被建立
        """
        if self.tau >= self.DEVELOPMENTAL_PEAK:
            print("[DEV] Past overconnection phase, skipping.")
            return
        
        n_nodes = connectome.num_nodes
        # 生成比正常多 2 倍的随机连接
        target_density = 0.3  # 目标连接密度
        
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                if random.random() < target_density:
                    weight = random.uniform(0.01, 0.1)
                    connectome.add_edge(i, j, weight=weight)
        
        print(f"[DEV] Overconnected: density = {connectome.density:.3f}")
    
    def prune(self, connectome, experience_history):
        """
        经验依赖的修剪
        保留高频激活的连接，删除低频连接
        """
        if self.tau < self.DEVELOPMENTAL_PEAK:
            print("[DEV] Too early for pruning.")
            return
        
        edges_to_prune = []
        
        for edge in connectome.all_edges:
            # 计算激活频率
            activation_freq = experience_history.get_activation_frequency(
                edge.source, edge.target
            )
            
            # 关键期内的连接更容易保留
            critical_boost = self._critical_period_boost(edge)
            
            # 综合评分
            survival_score = activation_freq * critical_boost
            
            if survival_score < self.theta_prune:
                edges_to_prune.append(edge)
        
        # 执行修剪
        for edge in edges_to_prune:
            connectome.remove_edge(edge)
        
        print(f"[DEV] Pruned {len(edges_to_prune)} edges. "
              f"Remaining: {connectome.num_edges}")
    
    def _critical_period_boost(self, edge):
        """
        关键期增强
        在关键期内建立的连接获得保留加成
        """
        edge_type = edge.module_type
        edge_creation_time = edge.created_at
        
        if edge_type in self.CRITICAL_PERIODS:
            start, end = self.CRITICAL_PERIODS[edge_type]
            if start <= edge_creation_time <= end:
                return 2.0  # 关键期内连接更容易保留
        
        return 1.0
    
    def advance_stage(self, delta_tau):
        """
        推进发育阶段
        """
        self.tau = min(1.0, self.tau + delta_tau)
        
        # 在发育峰值时执行修剪
        if self.tau >= self.DEVELOPMENTAL_PEAK and not self.has_pruned:
            self.prune(self.connectome, self.experience_history)
            self.has_pruned = True
        
        print(f"[DEV] Advanced to stage {self.tau:.3f}")
```

---

## 5. 元控制层的整体运行流程

```
初始化
  │
  ▼
┌─────────────────────┐
│ 设置 8 个核心参数    │
│ G_global=1.0,       │
│ θ_dmn=0.3,          │
│ ...                 │
└─────────────────────┘
  │
  ▼
运行循环
  │
  ├──→ [检测外部输入？]
  │      │
  │      ├── Yes → TPN模式
  │      │           │
  │      │           ├── 模块门控：选择相关映射
  │      │           │
  │      │           ├── 增益调节：根据任务设置增益
  │      │           │
  │      │           └── 执行处理
  │      │
  │      └── No → DMN模式
  │                  │
  │                  ├── 时序调度：确认无输入持续 > 阈值
  │                  │
  │                  ├── 增益调节：适度提高增益（内部探索）
  │                  │
  │                  └── DMN 运行：自我参照/时间旅行/心智模拟
  │
  ├──→ [发育检查]
  │      │
  │      ├── τ < 0.3 → 过度连接
   │      │
  │      └── τ >= 0.3 → 经验修剪
  │
  └──→ [参数自适应]
         │
         └── 根据系统表现微调 8 个参数
```

---

## 6. 关键数学公式汇总

### 6.1 认知负载计算
```
L(t) = 0.4 * H(input) + 0.3 * depth(t) + 0.3 * (active_modules / total_modules)
```
- H(input) = 输入熵（复杂度）
- depth(t) = 处理层级深度
- active_modules / total_modules = 资源占用率

### 6.2 最优增益
```
G* = G_base * (1 + α * safety * β_risk)
```
- safety ∈ [0, 1] = 环境安全性
- β_risk ∈ [0, 1] = 风险偏置
- α = 0.5 = 调节系数

### 6.3 噪声水平
```
σ = σ_base * G* * c_boost
```
- c_boost = 1.5（创造需求）或 1.0（普通）

### 6.4 映射竞争得分
```
S(map) = 0.3 * sim_semantic + 0.3 * success_rate + 0.2 * activation_bias + 0.2 * conn_strength
```

### 6.5 发育修剪决策
```
keep(edge) = activation_freq(edge) * critical_boost(edge) > θ_prune
```
- critical_boost = 2.0（关键期内）或 1.0（其他）

---

## 7. 与 HARE5 的映射对照表

| HARE5 特征 | Meta-Control Layer 实现 |
|-----------|------------------------|
| 不编码蛋白质 | 不直接处理认知内容 |
| 4 个点突变 | 8 个核心参数 |
| 控制"何时激活" | 时序调度器 |
| 相位锁定基因表达 | 相位锁定模块同步 |
| 增加相干性容量 | 增益调节器 |
| 时序窗口控制 | 发育引擎的关键期 |
| 物理结果（褶皱）≠ 认知 | 连接拓扑 ≠ 智能，编排方式才是 |

---

## 8. 接口定义

### 8.1 对外接口

```python
class MetaControlInterface:
    """
    元控制层对外暴露的接口
    """
    
    def set_global_gain(self, G: float) -> None:
        """设置全局增益 [0.5, 2.0]"""
        pass
    
    def get_current_mode(self) -> str:
        """获取当前模式：'DMN' | 'TPN' | 'TRANSITION'"""
        pass
    
    def switch_mode(self, target_mode: str) -> bool:
        """强制切换模式，返回是否成功"""
        pass
    
    def gate_modules(self, task_embedding: Vector) -> List[MapID]:
        """为给定任务选择激活的模块"""
        pass
    
    def get_development_stage(self) -> float:
        """获取发育阶段 [0, 1]"""
        pass
    
    def advance_development(self, delta: float) -> None:
        """推进发育阶段"""
        pass
    
    def emergency_reset(self) -> None:
        """紧急重置所有参数到安全值"""
        pass
```

### 8.2 事件监听

```python
# 元控制层监听的事件
EVENTS = [
    'cognitive_load_changed',      # 认知负载变化
    'external_input_detected',     # 检测到外部输入
    'dmn_simulation_completed',      # DMN 模拟完成
    'module_competition_ended',     # 模块竞争结束
    'connection_pruned',             # 连接被修剪
    'gain_exceeded_threshold',       # 增益超过阈值
]
```

---

*文档版本：v0.1*  
*部分：Part 1 / 6*  
*创建日期：2026-04-23*
