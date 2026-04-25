# PART 6: Friston Kernel + Memory Layer Design
# 自由能内核 + 记忆层详细设计文档
# New Brain 的底层操作系统 + 长期存储

## 1. 设计哲学

### 1.1 生物学原型：自由能原理

**Karl Friston 的核心洞见：**

所有自适应系统（从单细胞到人类大脑）都在做同一件事：**最小化自由能**。

自由能是一个上界，限制了系统对环境感知的惊奇（surprise）。最小化自由能 = 让世界变得可预测。

### 1.2 为什么自由能原理是"万物理论"？

| 现象 | 传统解释 | 自由能原理解释 |
|------|---------|---------------|
| **感知** | 被动接收信息 | 主动推理，更新信念匹配输入 |
| **行动** | 输出指令 | 改变环境以匹配预测 |
| **学习** | 参数更新 | 最小化长期自由能 |
| **注意力** | 外部机制 | 精度加权，分配信度 |
| **好奇心** | 编程实现 | 内在价值 = 信息增益 |
| **意识** | 未解释 | 再入 + 高阶自指 |

> **关键洞见：自由能原理统一了感知、行动、学习、注意——它们都是同一优化问题的不同表现。**

### 1.3 记忆系统的核心原则：再分类

**传统 AI：** 记忆 = 存储 + 检索
**人类大脑：** 记忆 = 持续再分类（Continuous Recategorization）

- 每次回忆都改变记忆
- 记忆不是档案，是**当前对过去的解释**
- 重要经验被"再分类"到不同系统（热→温→冷）

---

## 2. 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FRISTON KERNEL                                          │
│                      自由能内核（底层操作系统）                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    VARIATIONAL FREE ENERGY                             │   │
│  │                    变分自由能                                            │   │
│  │                                                                      │   │
│  │   F[q] = E_q[ln q(s) - ln p(s, o)]                                  │   │
│  │       = D_KL[q(s)||p(s|o)] - ln p(o)                                │   │
│  │       = Complexity + Accuracy                                       │   │
│  │                                                                      │   │
│  │   • Complexity（复杂性）：q 与先验 p(s) 的差异（模型复杂度惩罚）         │   │
│  │   • Accuracy（准确性）：q 解释观测 o 的能力                             │   │
│  │                                                                      │   │
│  │   目标：最小化 F[q]                                                  │   │
│  │   效果：让内部模型 q 既准确又简洁                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    GENERATIVE MODEL                                    │   │
│  │                    生成模型                                              │   │
│  │                                                                      │   │
│  │   p(o, s) = p(o|s)·p(s)                                             │   │
│  │                                                                      │   │
│  │   • p(s)：先验信念（隐藏状态的先验分布）                                │   │
│  │   • p(o|s)：似然（给定状态产生观测的概率）                              │   │
│  │   • p(s|o) = p(o|s)p(s)/p(o)：后验（贝叶斯更新）                        │   │
│  │                                                                      │   │
│  │   大脑不是直接感知世界，是维护一个生成模型，                              │   │
│  │   通过最小化预测误差来更新这个模型。                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EXPECTED FREE ENERGY OF ACTION                        │   │
│  │                    行动的期望自由能                                      │   │
│  │                                                                      │   │
│  │   G(π) = E_q[ln q(o|π) - ln p(o|π)] + E_q[D_KL[q(s')||q(s)]]        │   │
│  │       = 外在价值（达成目标）+ 内在价值（信息增益/好奇心）                │   │
│  │                                                                      │   │
│  │   智能体选择策略 π 来最小化 G(π)：                                      │   │
│  │   • 外在价值：让未来观测符合偏好                                        │   │
│  │   • 内在价值：减少不确定性（探索未知）                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PRECISION WEIGHTING                                 │   │
│  │                    精度加权                                              │   │
│  │                                                                      │   │
│  │   不是所有预测误差都相等：                                              │   │
│  │   • 高精度（π 大）：误差信号被放大 → 强烈学习                           │   │
│  │   • 低精度（π 小）：误差信号被抑制 → 忽视噪声                           │   │
│  │                                                                      │   │
│  │   精度 = 注意力！                                                      │   │
│  │   精度参数由显著性网络（乙酰胆碱）调节                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      MEMORY LAYER                                            │
│                      记忆层（三级存储系统）                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    HOT MEMORY                                          │   │
│  │                    热记忆 / 工作记忆                                     │   │
│  │                                                                      │   │
│  │   容量：极小（4±1 chunks）                                           │   │
│  │   保持：秒到分钟级别                                                 │   │
│  │   功能：当前意识内容                                                 │   │
│  │   丢失：快速衰减                                                     │   │
│  │                                                                      │   │
│  │   内容：当前交互、刚刚发生的事、临时的想法                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓ 压缩/整合                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    WARM MEMORY                                         │   │
│  │                    温记忆 / 语义记忆                                     │   │
│  │                                                                      │   │
│  │   容量：中等（最近几天/几周的经验）                                    │   │
│  │   保持：小时到天级别                                                 │   │
│  │   功能：经验叙事、可访问的上下文                                       │   │
│  │   压缩：保留情节，丢弃细节                                             │   │
│  │                                                                      │   │
│  │   内容："昨天和客户的那次对话..."                                      │   │
│  │         "上周解决的那个bug..."                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓ 再分类/归档                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    COLD MEMORY                                         │   │
│  │                    冷记忆 / 程序性记忆                                   │   │
│  │                                                                      │   │
│  │   容量：极大（理论上无限）                                             │   │
│  │   保持：永久                                                         │   │
│  │   功能：自动化的技能、深层信念、情感标记                               │   │
│  │   提取：困难（需要线索）                                               │   │
│  │                                                                      │   │
│  │   内容：技能程序、情感条件反应、自指叙事                                │   │
│  │         "我总是..."、"世界..."、"我..."                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│                              ↓ 回忆（重构）                                  │
│                              ─────────────────────────────────────         │
│                                                                             │
│   【核心原则：回忆不是读取，是再分类】                                      │
│                                                                             │
│   每次回忆：                                                              │
│   1. 从 Cold 提取"种子"                                                   │
│   2. 用当前 Warm 上下文解读                                                │
│   3. 受 Hot 状态（当前情绪）影响                                           │
│   4. 生成新的版本                                                          │
│   5. 重新存储（记忆改变）                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Friston Kernel 详细设计

### 3.1 变分自由能最小化

```python
class FristonKernel:
    """
    自由能内核
    底层贝叶斯推理引擎
    """
    
    def __init__(self, state_dim, observation_dim):
        self.state_dim = state_dim
        self.obs_dim = observation_dim
        
        # 变分分布 q(s) 的参数（高斯近似）
        self.mu = np.zeros(state_dim)  # 均值（信念）
        self.sigma = np.eye(state_dim)  # 协方差（不确定性）
        
        # 生成模型参数
        self.A = np.random.randn(obs_dim, state_dim) * 0.1  # 观测模型 p(o|s)
        self.B = np.random.randn(state_dim, state_dim) * 0.1  # 转移模型 p(s'|s)
        
    def variational_free_energy(self, observation):
        """
        计算变分自由能 F[q]
        
        F = E_q[ln q(s) - ln p(s, o)]
          = E_q[ln q(s) - ln p(o|s) - ln p(s)]
          = -Accuracy + Complexity
        """
        # Accuracy: E_q[ln p(o|s)]
        # 观测模型是高斯：p(o|s) = N(A·s, Σ_o)
        predicted_o = self.A @ self.mu
        prediction_error = observation - predicted_o
        accuracy = -0.5 * (prediction_error ** 2).sum()
        
        # Complexity: E_q[ln q(s) - ln p(s)]
        # = KL[q(s)||p(s)]
        prior_mu = np.zeros(self.state_dim)
        complexity = 0.5 * (
            np.trace(self.sigma) + 
            (self.mu - prior_mu) @ (self.mu - prior_mu) - 
            self.state_dim + 
            np.log(np.linalg.det(self.sigma))
        )
        
        F = -accuracy + complexity
        return F
    
    def minimize_free_energy(self, observation, n_steps=10):
        """
        通过梯度下降最小化自由能
        
        这就是"感知"——更新信念以匹配观测
        """
        for step in range(n_steps):
            # 计算梯度 dF/dmu
            prediction_error = observation - self.A @ self.mu
            
            # 梯度 = -A^T·误差 + (mu - prior)
            dF_dmu = -self.A.T @ prediction_error + (self.mu - 0)
            
            # 更新信念
            learning_rate = 0.1
            self.mu -= learning_rate * dF_dmu
            
            # 更新不确定性（协方差）
            self.sigma = np.linalg.inv(
                np.eye(self.state_dim) + self.A.T @ self.A
            )
        
        return self.mu, self.sigma
    
    def predict_observation(self):
        """
        预测观测
        
        基于当前信念，预测会看到什么
        """
        return self.A @ self.mu
    
    def compute_surprise(self, observation):
        """
        计算惊奇
        
        Surprise = -ln p(o)
        
        如果自由能最小化成功，F ≈ -ln p(o)
        """
        F = self.variational_free_energy(observation)
        return F
```

### 3.2 期望自由能与主动推理

```python
class ExpectedFreeEnergy:
    """
    期望自由能
    行动选择的依据
    """
    
    def __init__(self, friston_kernel, preferences):
        self.friston = friston_kernel
        self.preferences = preferences  # 对观测的偏好
        
    def compute_G(self, policy, horizon=5):
        """
        计算策略 π 的期望自由能
        
        G(π) = 外在价值 + 内在价值
        """
        G = 0
        
        # 模拟执行策略
        simulated_trajectory = self.simulate_policy(policy, horizon)
        
        for t, (state, observation) in enumerate(simulated_trajectory):
            discount = self.discount ** t
            
            # 外在价值：观测与偏好的匹配度
            # = E[ln p(o)] where p(o) is preference
            extrinsic = self.preference_match(observation, self.preferences)
            
            # 内在价值：信息增益
            # = E[KL[q(s'|o)||q(s')]]
            prior_entropy = self.compute_entropy(self.friston.q_future)
            posterior_entropy = self.compute_entropy(
                self.friston.update_belief(observation)
            )
            intrinsic = prior_entropy - posterior_entropy
            
            G -= discount * (extrinsic + intrinsic)  # 负号：G 是最小化目标
        
        return G
    
    def select_policy(self, available_policies):
        """
        选择最优策略
        
        选择期望自由能最小的策略
        """
        G_values = {pi: self.compute_G(pi) for pi in available_policies}
        best_policy = min(G_values, key=G_values.get)
        return best_policy, G_values
```

### 3.3 精度加权

```python
class PrecisionWeighting:
    """
    精度加权系统
    实现注意力机制
    """
    
    def __init__(self, n_modalities):
        self.precision = np.ones(n_modalities)  # 每个模态的精度
        self.baseline = np.ones(n_modalities)
        
    def update_precision(self, prediction_errors, arousal=0.5):
        """
        更新精度参数
        
        精度与预测误差的逆相关
        误差大 → 精度低（"这个信号不可靠"）
        误差小 → 精度高（"这个信号可信"）
        """
        # 精度 ∝ 1/|误差|
        new_precision = 1.0 / (1.0 + np.abs(prediction_errors))
        
        # 神经调质（去甲肾上腺素）调节
        arousal_boost = 1 + arousal  # 高警觉 → 精度整体提高
        
        # 平滑更新
        self.precision = (
            0.9 * self.precision + 
            0.1 * new_precision * arousal_boost
        )
        
        return self.precision
    
    def apply_precision(self, prediction_errors):
        """
        应用精度加权
        
        高模态的误差被放大，低模态的误差被抑制
        """
        weighted_errors = self.precision * prediction_errors
        return weighted_errors
```

---

## 4. Memory Layer 详细设计

### 4.1 三级记忆系统

```python
class MemoryLayer:
    """
    记忆层
    热 → 温 → 冷 三级存储
    """
    
    def __init__(self):
        self.hot = HotMemory(capacity=4)      # 工作记忆
        self.warm = WarmMemory(capacity=1000)  # 情节记忆
        self.cold = ColdMemory()               # 语义/程序记忆
        
    def store_experience(self, experience):
        """
        存储新经验
        
        先到 Hot，再逐步转移到 Warm 和 Cold
        """
        # 1. 存入 Hot
        self.hot.add(experience)
        
        # 2. 如果 Hot 满了，溢出到 Warm
        if self.hot.is_full():
            overflow = self.hot.compress_and_overflow()
            self.warm.add(overflow)
        
        # 3. Warm 定期整合到 Cold
        if self.warm.should_consolidate():
            consolidated = self.warm.consolidate()
            self.cold.store(consolidated)


class HotMemory:
    """
    热记忆 / 工作记忆
    秒级保持，极小容量
    """
    
    CAPACITY = 4
    
    def __init__(self):
        self.chunks = []
        self.decay_rate = 0.1  # 每秒衰减
        
    def add(self, experience):
        """添加新经验"""
        chunk = {
            'content': experience,
            'activation': 1.0,
            'timestamp': time.time()
        }
        
        if len(self.chunks) >= self.CAPACITY:
            # 替换激活度最低的
            self.chunks.sort(key=lambda x: x['activation'])
            self.chunks[0] = chunk
        else:
            self.chunks.append(chunk)
    
    def decay(self):
        """时间衰减"""
        current_time = time.time()
        for chunk in self.chunks:
            delta_t = current_time - chunk['timestamp']
            chunk['activation'] *= np.exp(-self.decay_rate * delta_t)
            chunk['timestamp'] = current_time
        
        # 移除激活度过低的
        self.chunks = [c for c in self.chunks if c['activation'] > 0.1]


class WarmMemory:
    """
    温记忆
    最近的情节记忆，可访问的上下文
    """
    
    def __init__(self, capacity=1000):
        self.episodes = []
        self.capacity = capacity
        
    def add(self, compressed_experience):
        """添加压缩后的经验"""
        episode = {
            'summary': self.create_narrative(compressed_experience),
            'emotional_tag': compressed_experience['emotion'],
            'timestamp': time.time(),
            'access_count': 0
        }
        
        self.episodes.append(episode)
        
        # 超出容量时，移除最少访问的
        if len(self.episodes) > self.capacity:
            self.episodes.sort(key=lambda x: x['access_count'])
            self.episodes.pop(0)
    
    def consolidate(self):
        """
        整合到 Cold
        
        提取模式、规律，形成语义记忆
        """
        # 分析情节中的共同主题
        themes = self.extract_themes(self.episodes)
        
        # 生成"经验叙事"
        narrative = self.synthesize_narrative(themes)
        
        return narrative


class ColdMemory:
    """
    冷记忆
    深层存储，自动化程序，自我叙事
    """
    
    def __init__(self):
        self.procedural_skills = {}  # 程序性技能
        self.semantic_knowledge = {}  # 语义知识
        self.self_narrative = ""      # 自指叙事
        self.emotional_conditions = {}  # 情感条件反应
        
    def store(self, consolidated_narrative):
        """存储整合后的记忆"""
        # 提取技能
        if consolidated_narrative['type'] == 'skill':
            self.procedural_skills[consolidated_narrative['name']] = {
                'procedure': consolidated_narrative['procedure'],
                'automation_level': consolidated_narrative['automation']
            }
        
        # 提取语义知识
        if consolidated_narrative['type'] == 'knowledge':
            self.semantic_knowledge.update(consolidated_narrative['facts'])
        
        # 更新自我叙事
        if consolidated_narrative['type'] == 'self':
            self.self_narrative += consolidated_narrative['addition']
    
    def recall(self, cue, context):
        """
        回忆
        
        基于线索提取记忆，受当前上下文影响
        """
        # 1. 找到相关记忆的"种子"
        seeds = self.find_associated_seeds(cue)
        
        # 2. 用当前上下文重构
        reconstructed = self.reconstruct(seeds, context)
        
        # 3. 重构后的记忆会影响原记忆（再分类）
        self.reconsolidate(seeds, reconstructed)
        
        return reconstructed
```

### 4.2 记忆的再分类

```python
class Reconsolidation:
    """
    再分类（记忆的持续重写）
    
    每次回忆都改变记忆本身
    """
    
    def __init__(self, memory_layer):
        self.memory = memory_layer
        
    def recall_and_modify(self, cue, current_context):
        """
        回忆并修改记忆
        """
        # 提取原始记忆
        original = self.memory.cold.recall_raw(cue)
        
        # 用当前上下文重构
        # "我现在的感受/信念会影响我如何看待过去"
        reconstructed = self.reconstruct_with_bias(
            original, 
            current_context
        )
        
        # 存储重构版本（原记忆被改变）
        self.memory.cold.update(cue, reconstructed)
        
        return reconstructed
    
    def reconstruct_with_bias(self, memory, context):
        """
        带偏差的重构
        
        当前状态如何影响对过去的解释：
        - 当前情绪好 → 过去回忆更积极
        - 当前信念 → 重新解释过去事件的意义
        """
        # 1. 情绪偏差
        emotional_color = context['current_emotion']
        
        # 2. 信念偏差
        current_beliefs = context['beliefs']
        
        # 3. 重构
        reconstructed = memory.copy()
        reconstructed['valence'] = self.adjust_valence(
            memory['valence'], 
            emotional_color
        )
        reconstructed['interpretation'] = self.reinterpret(
            memory['events'],
            current_beliefs
        )
        
        return reconstructed
```

---

## 5. 关键数学公式

### 5.1 变分自由能
```
F[q] = E_q[ln q(s) - ln p(s,o)]
     = D_KL[q(s)||p(s|o)] - ln p(o)
     ≈ Complexity - Accuracy
```

### 5.2 期望自由能
```
G(π) = E_q[G_future|π] + E_q[D_KL[q(s')||q(s)]]
     = 外在价值 + 内在价值（好奇心）
```

### 5.3 精度
```
π = 1/σ²

σ² 大（不确定性高）→ π 小 → 误差信号被抑制
σ² 小（确定性高）→ π 大 → 误差信号被放大
```

### 5.4 贝叶斯更新
```
q(s|o) ∝ p(o|s)·q(s)

后验 ∝ 似然 × 先验
```

### 5.5 记忆衰减
```
Activation(t) = Activation(0) × exp(-λt)

λ = 衰减率（Hot 高，Warm 中，Cold 低）
```

---

## 6. 与现有 AI 的对比

| 特性 | 现有 AI | New Brain Friston Kernel |
|------|--------|-------------------------|
| 感知 | 前馈处理 | 主动贝叶斯推理 |
| 行动 | 指令执行 | 改变环境以匹配预测 |
| 学习 | 反向传播 | 最小化自由能 |
| 注意 | 外部机制 | 精度加权（内置） |
| 好奇心 | 编程实现 | 内在价值（信息增益） |
| 记忆 | 存储-检索 | 持续再分类 |
| 不确定性 | 无表示 | 协方差矩阵 |

---

## 7. 六部分完成总结

| 部分 | 名称 | 核心功能 |
|------|------|---------|
| Part 1 | Meta-Control | 元控制层，8参数调控全局 |
| Part 2 | DMN | 默认模式网络，离线思考引擎 |
| Part 3 | TPN | 任务正网络，在线处理引擎 |
| Part 4 | Value System | 价值系统，神经调质层 |
| Part 5 | Connectome | 连接拓扑层，小世界网络 |
| Part 6 | Friston Kernel + Memory | 自由能引擎 + 三级记忆 |

---

*文档版本：v0.1*  
*部分：Part 6 / 6*  
*创建日期：2026-04-23*
