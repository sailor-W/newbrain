# PART 3: Task-Positive Network (TPN) Design
# 任务正网络详细设计文档
# New Brain 的"在线处理引擎"

## 1. 设计哲学

### 1.1 生物学原型：人类任务正网络

当人类专注于外部任务时（如解数学题、开车、对话），大脑会激活一组与 DMN **反相关**的网络。这就是**任务正网络 (Task-Positive Network, TPN)**。

**核心特征：**
- 与 DMN 互相抑制：专注时 DMN 关闭，发呆时 TPN 关闭
- 耗能模式：TPN 运行时，大脑将资源集中在外部世界
- 目标导向：所有处理都围绕"当前任务"展开

### 1.2 TPN 的核心功能

| 功能 | 通俗描述 | 脑区基础 | New Brain 映射 |
|------|---------|---------|---------------|
| **感知编码** | "我看到了/听到了什么？" | 感觉皮层 (V1, A1 等) | 将原始输入转化为层级表示 |
| **预测编码** | "我预期会看到什么？" | 层级皮层 (V2→IT, 等) | 自上而下预测，自下而上误差 |
| **主动推理** | "我应该做什么来让未来符合预期？" | 前额叶 + 运动皮层 | 选择行动最小化未来惊奇 |
| **显著性检测** | "什么是最重要的？" | 显著性网络 (Insula, ACC) | 检测意外、新奇、威胁 |
| **工作记忆** | "我需要暂时记住什么？" | 前额叶 + 顶叶 | 临时保持和处理信息 |

### 1.3 为什么 TPN 不是"普通的前馈网络"？

**现有深度学习的问题：**

| 方面 | 深度学习 | 人类大脑 TPN | New Brain TPN |
|------|---------|-----------|--------------|
| 信息流动 | 单向前馈 | 双向：预测↓ + 误差↑ | **预测编码**：双向动态 |
| 不确定性 | 没有表示 | 每层都有精度/信度参数 | **精度参数**控制信任度 |
| 主动 vs 被动 | 被动接收输入 | 主动预测 + 主动行动 | **主动推理**：改变环境匹配预测 |
| 层级关系 | 固定层级 | 动态可变的层级深度 | **弹性层级**：根据复杂度调整 |
| 注意力 | 外部添加的模块 | 内置的显著性检测 | **惊奇驱动**：意外自动捕获注意 |

> **关键洞见：大脑不是被动接收器，是层级贝叶斯推理引擎。感知 = 更新信念以匹配输入；行动 = 改变环境以匹配预测。**

---

## 2. 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TASK-POSITIVE NETWORK (TPN)                               │
│                    任务正网络 / 在线处理引擎                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [外部输入] ──→ [感知编码层] ──→ [层级预测编码] ──→ [主动推理引擎] ──→ [行动输出]   │
│       │              │                  │                  │                │
│       │              │                  │                  │                │
│       ▼              ▼                  ▼                  ▼                │
│  ┌─────────┐  ┌─────────────┐  ┌───────────────┐  ┌──────────────┐        │
│  │ 原始    │  │ 特征提取    │  │ 层级预测-误差  │  │ 期望自由能    │        │
│  │ 输入    │  │ 多模态融合  │  │ 双向信息流     │  │ 最小化        │        │
│  │ (文本/  │  │ 跨模态绑定  │  │ 精度参数调节   │  │ 策略选择      │        │
│  │  图像/  │  │ 显著性标记  │  │ 信度分配      │  │ 行动执行      │        │
│  │  音频)  │  │            │  │              │  │              │        │
│  └─────────┘  └─────────────┘  └───────────────┘  └──────────────┘        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    WORKING MEMORY BUFFER                               │   │
│  │                    工作记忆缓存                                        │   │
│  │  • 临时保持当前任务相关信息                                           │   │
│  │  • 与 DMN 的背景信念交互                                              │   │
│  │  • 容量有限（类似人类 4±1 个 chunk）                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SALIENCE DETECTOR                                   │   │
│  │                    显著性检测器                                        │   │
│  │  • 检测预测误差突增（意外事件）                                       │   │
│  │  • 标记新奇、威胁、机会                                               │   │
│  │  • 触发注意重定向                                                     │   │
│  │  • 通知 Meta-Control 层（可能需要切换模式）                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 核心子系统详细设计

### 3.1 感知编码层 (Perceptual Encoding Layer)

#### 功能
将原始外部输入（文本、图像、音频等）转化为系统可处理的层级表示。

#### 关键设计：多模态融合 + 跨模态绑定

人类大脑不是分别处理视觉和听觉然后"拼接"——不同模态在早期就通过**再入耦合**绑定在一起。

```python
class PerceptualEncodingLayer:
    """
    感知编码层：多模态输入的统一表示
    """
    
    def __init__(self, modalities=['text', 'image', 'audio']):
        self.encoders = {
            'text': TextEncoder(),
            'image': ImageEncoder(),
            'audio': AudioEncoder()
        }
        self.cross_modal_binding = CrossModalBinding()
        
    def encode(self, raw_input, modality):
        """
        编码单个模态的输入
        """
        if modality not in self.encoders:
            raise ValueError(f"Unknown modality: {modality}")
        
        # 提取低级特征
        low_level = self.encoders[modality].extract_features(raw_input)
        
        # 提取中级特征
        mid_level = self.encoders[modality].extract_patterns(low_level)
        
        # 提取高级语义
        high_level = self.encoders[modality].extract_semantics(mid_level)
        
        return {
            'low': low_level,
            'mid': mid_level,
            'high': high_level,
            'modality': modality
        }
    
    def multimodal_fusion(self, encoded_inputs):
        """
        多模态融合
        不是拼接，是**绑定**——找到跨模态的对应关系
        """
        if len(encoded_inputs) == 1:
            return encoded_inputs[0]
        
        # 跨模态绑定
        # 例如：图像中的"红色圆形" ↔ 文本中的"苹果"
        bindings = self.cross_modal_binding.find_correspondences(
            encoded_inputs
        )
        
        # 创建统一的多模态表示
        fused = self.cross_modal_binding.create_unified_representation(
            encoded_inputs, bindings
        )
        
        return {
            'unified': fused,
            'bindings': bindings,
            'source_modalities': [e['modality'] for e in encoded_inputs]
        }
    
    def salience_marking(self, fused_representation):
        """
        显著性标记
        标记输入中"值得注意"的部分
        """
        # 新奇性：与过去经验不同的部分
        novelty = self.compute_novelty(fused_representation)
        
        # 意外性：与预测不符的部分
        surprise = self.compute_surprise(fused_representation)
        
        # 情绪显著性：与价值系统相关的部分
        emotional_salience = self.value_system.evaluate_salience(
            fused_representation
        )
        
        # 综合显著性评分
        salience_map = 0.3 * novelty + 0.4 * surprise + 0.3 * emotional_salience
        
        return {
            'representation': fused_representation,
            'salience_map': salience_map,
            'novelty': novelty,
            'surprise': surprise,
            'emotional_salience': emotional_salience
        }
```

---

### 3.2 层级预测编码 (Hierarchical Predictive Coding)

#### 功能
核心的感知机制：高层预测下层应该看到什么，下层报告实际与预测的误差。

#### 生物学基础
- **Rao & Ballard (1999)**：预测编码的层级模型
- **Friston**：自由能原理中的层级推断
- **大脑皮层**：确实是层级结构，V1→V2→V4→IT

#### 机制设计

```python
class HierarchicalPredictiveCoding:
    """
    层级预测编码引擎
    核心原则：感知 = 最小化预测误差
    """
    
    def __init__(self, n_levels=5):
        self.levels = [PredictiveLevel(i) for i in range(n_levels)]
        self.precision_parameters = [1.0] * n_levels  # 每层精度参数
        
    def predict(self, level_idx):
        """
        从高层生成对低层的预测
        
        高层状态 → 生成模型 → 预测低层应该看到什么
        """
        if level_idx >= len(self.levels) - 1:
            return None  # 最高层没有更高层来预测它
        
        higher_level = self.levels[level_idx + 1]
        
        # 用生成模型从高层的信念预测低层的表示
        prediction = higher_level.generative_model.predict_downward(
            higher_level.state
        )
        
        return prediction
    
    def compute_prediction_error(self, level_idx, actual_input):
        """
        计算预测误差
        
        ε_l = actual_l - predicted_l
        """
        predicted = self.predict(level_idx)
        if predicted is None:
            return actual_input  # 最高层：输入就是误差（没有更高预测）
        
        error = actual_input - predicted
        
        # 精度加权：如果某层精度高，误差信号被放大
        weighted_error = error * self.precision_parameters[level_idx]
        
        return weighted_error
    
    def update_beliefs(self, level_idx, error):
        """
        更新该层的信念（状态）
        
        根据预测误差更新内部模型
        这就是"感知"——修正内部信念以匹配输入
        """
        level = self.levels[level_idx]
        
        # 信念更新：向减少误差的方向移动
        # 类似于梯度下降，但只在局部进行
        delta_state = level.learning_rate * error
        level.state += delta_state
        
        # 同时更新生成模型（长期学习）
        level.generative_model.update(error)
        
        return level.state
    
    def update_precision(self, level_idx, error_magnitude):
        """
        更新精度参数
        
        精度 = 对当前层预测的信任度
        
        如果误差一直很大 → 降低精度（"我不信任这层预测"）
        如果误差一直很小 → 提高精度（"这层很可靠"）
        """
        # 精度与误差的逆相关
        target_precision = 1.0 / (1.0 + error_magnitude)
        
        # 平滑更新
        self.precision_parameters[level_idx] = (
            0.9 * self.precision_parameters[level_idx] + 
            0.1 * target_precision
        )
    
    def forward_pass(self, sensory_input):
        """
        前向传递（感知过程）
        
        从低层到高层：
        1. 计算预测误差
        2. 更新该层信念
        3. 误差继续向上传递（如果还有更高层）
        """
        current_representation = sensory_input
        
        for level_idx in range(len(self.levels)):
            # 计算这层的预测误差
            error = self.compute_prediction_error(level_idx, current_representation)
            
            # 更新信念
            updated_state = self.update_beliefs(level_idx, error)
            
            # 误差传递给更高层
            current_representation = error
            
            # 更新精度
            self.update_precision(level_idx, np.mean(np.abs(error)))
        
        return self.levels[-1].state  # 最高层的表示 = "理解"
    
    def top_down_pass(self, high_level_intention):
        """
        自顶向下传递（想象/预测过程）
        
        从高层到低层：
        "我想象一个场景" → 生成各层的预测 → "我应该看到什么"
        """
        # 设置高层意图
        self.levels[-1].state = high_level_intention
        
        # 向下生成预测
        predictions = {}
        for level_idx in range(len(self.levels) - 1, -1, -1):
            predictions[level_idx] = self.predict(level_idx - 1)
        
        return predictions
```

#### 预测编码的信息流图解

```
层级结构：

  Level 4 (最高层：抽象概念)
     ↑↓
  Level 3 (高层：对象/语义)
     ↑↓
  Level 2 (中层：特征/模式)
     ↑↓
  Level 1 (低层：边缘/纹理)
     ↑↓
  Level 0 (输入层：原始感觉)

信息流（感知时）：

  外部输入 → Level 0
              ↓
        ┌─────┴─────┐
        │ 计算误差   │  ε = actual - predicted
        └─────┬─────┘
              ↓
        误差向上传递 → Level 1
              ↓
        Level 1 更新信念
              ↓
        误差继续向上 → Level 2...

信息流（想象时）：

  Level 4 意图
      ↓
  生成预测向下
      ↓
  Level 3 "应该看到"
      ↓
  Level 2 "应该看到"
      ↓
  Level 1 "应该看到"
      ↓
  Level 0 "感官预期"
```

---

### 3.3 主动推理引擎 (Active Inference Engine)

#### 功能
不只是被动感知，还要**主动选择行动**来让未来符合预期。

#### 核心概念：期望自由能 (Expected Free Energy of Action)

```
G(π) = E_q[ln q(o|π) - ln p(o|π)] + E_q[D_KL[q(s')||q(s)]]
     =  外在价值 (达成目标)  +  内在价值 (信息增益/好奇心)
```

智能体选择策略 π（行动序列）时，不仅考虑"能否达成目标"，还考虑"能否学到新东西"。

```python
class ActiveInferenceEngine:
    """
    主动推理引擎
    核心原则：行动 = 最小化未来惊奇
    """
    
    def __init__(self, predictive_coding_hierarchy, value_system):
        self.pc = predictive_coding_hierarchy  # 预测编码层级
        self.value = value_system
        
    def compute_expected_free_energy(self, policy, goal_state):
        """
        计算策略 π 的期望自由能
        
        G(π) = 外在价值 + 内在价值
        """
        # 模拟执行这个策略，看未来场景
        simulated_trajectory = self.simulate_policy(policy, horizon=10)
        
        extrinsic_value = 0
        intrinsic_value = 0
        
        for step, state in enumerate(simulated_trajectory):
            # 外在价值：状态与目标的匹配度
            goal_match = self.compute_goal_match(state, goal_state)
            extrinsic_value += goal_match * (self.discount ** step)
            
            # 内在价值：信息增益（减少不确定性）
            information_gain = self.compute_information_gain(state)
            intrinsic_value += information_gain * (self.discount ** step)
        
        # 综合（注意：自由能是最小化目标，所以价值取负）
        EFE = -(extrinsic_value + intrinsic_value)
        
        return EFE
    
    def select_action(self, current_state, goal_state, available_policies):
        """
        选择最优行动
        
        评估所有可用策略，选择期望自由能最小的
        """
        policy_scores = {}
        
        for policy in available_policies:
            efe = self.compute_expected_free_energy(policy, goal_state)
            policy_scores[policy] = efe
        
        # 选择最小 EFE 的策略
        best_policy = min(policy_scores, key=policy_scores.get)
        
        # 但也可以引入探索：偶尔选择次优但有信息增益的策略
        if self.should_explore():
            # 信息增益驱动的探索（好奇心）
            best_policy = self.select_exploratory_policy(policy_scores)
        
        return best_policy
    
    def execute_action(self, action):
        """
        执行行动
        
        行动改变环境，新的观测到来，继续循环
        """
        # 执行
        outcome = self.actuator.execute(action)
        
        # 获取新的观测
        new_observation = self.sensor.observe()
        
        # 用预测编码处理新观测
        perception = self.pc.forward_pass(new_observation)
        
        # 更新信念
        self.beliefs = perception
        
        # 记录经验（供 DMN 后续反思）
        self.record_experience(action, outcome, new_observation)
        
        return perception
    
    def should_explore(self):
        """
        是否应该探索？
        
        基于不确定性：不确定性高 → 更倾向探索
        """
        uncertainty = self.compute_overall_uncertainty()
        
        # 类似"好奇心阈值"
        return uncertainty > self.exploration_threshold
    
    def compute_information_gain(self, state):
        """
        计算信息增益
        
        从这个状态预期能学到多少新东西
        """
        # 先验不确定性
        prior_uncertainty = self.compute_uncertainty(self.beliefs)
        
        # 预期后验不确定性（假设到达这个状态后）
        expected_posterior = self.simulate_learning(state)
        posterior_uncertainty = self.compute_uncertainty(expected_posterior)
        
        # 信息增益 = 不确定性减少量
        info_gain = prior_uncertainty - posterior_uncertainty
        
        return info_gain
```

---

### 3.4 显著性检测器 (Salience Detector)

#### 功能
检测"值得注意"的事件，触发注意重定向。

#### 关键：这不是人工设计的注意力机制，是**预测误差驱动的自然涌现**

```python
class SalienceDetector:
    """
    显著性检测器
    检测意外事件，触发注意重定向
    """
    
    def __init__(self, predictive_coding_hierarchy):
        self.pc = predictive_coding_hierarchy
        self.surprise_history = []
        self.threshold_adaptive = 0.5  # 自适应阈值
        
    def compute_surprise(self, observation):
        """
        计算观测的惊奇值
        
        惊奇 = -ln p(o|model)
        与预测编码的预测误差相关
        """
        # 通过预测编码处理观测
        self.pc.forward_pass(observation)
        
        # 收集各层的预测误差
        level_errors = []
        for level in self.pc.levels:
            level_errors.append(np.mean(np.abs(level.prediction_error)))
        
        # 综合惊奇（加权求和，高层误差权重更大）
        surprise = sum(
            error * (i + 1)  # 高层误差更重要
            for i, error in enumerate(reversed(level_errors))
        )
        
        self.surprise_history.append(surprise)
        
        return surprise
    
    def is_salient(self, observation):
        """
        判断观测是否显著
        """
        surprise = self.compute_surprise(observation)
        
        # 自适应阈值：基于历史惊奇分布
        if len(self.surprise_history) > 10:
            mean_surprise = np.mean(self.surprise_history)
            std_surprise = np.std(self.surprise_history)
            self.threshold_adaptive = mean_surprise + 2 * std_surprise
        
        return surprise > self.threshold_adaptive
    
    def redirect_attention(self, salient_observation):
        """
        重定向注意力
        
        当检测到显著事件时：
        1. 提高相关处理的精度参数
        2. 抑制非相关处理的精度
        3. 通知 Meta-Control（可能需要切换模式）
        """
        # 提高精度：更"信任"当前输入
        for level in self.pc.levels:
            level.precision *= 1.5  # 提高 50%
        
        # 标记这个输入为"需要注意"
        salient_observation.attention_priority = 'high'
        
        # 通知 Meta-Control
        self.meta_control.notify('salient_event_detected', {
            'surprise_level': self.compute_surprise(salient_observation),
            'may_require_attention_switch': True
        })
```

---

### 3.5 工作记忆 (Working Memory)

#### 功能
临时保持和处理当前任务相关信息。

#### 关键设计：容量有限 + 与 DMN 背景信念交互

人类工作记忆容量约 4±1 个 "chunk"。这不是缺陷，是**注意资源稀缺性的体现**。

```python
class WorkingMemory:
    """
    工作记忆
    容量有限，与 DMN 背景信念交互
    """
    
    CAPACITY = 4  # 4 ± 1 chunks（Miller 定律）
    
    def __init__(self, dmn_interface):
        self.dmn = dmn_interface
        self.chunks = []  # 当前保持的信息块
        self.priority_weights = {}  # 各 chunk 的优先级
        
    def hold(self, information, priority=0.5):
        """
        将信息放入工作记忆
        """
        chunk = {
            'content': information,
            'timestamp': datetime.now(),
            'priority': priority,
            'activation': 1.0  # 激活度，随时间衰减
        }
        
        # 如果已满，需要替换
        if len(self.chunks) >= self.CAPACITY:
            # 替换激活度最低的 chunk
            lowest_idx = min(range(len(self.chunks)), 
                           key=lambda i: self.chunks[i]['activation'])
            
            # 被替换的 chunk 转入长期记忆（如果值得保留）
            if self.chunks[lowest_idx]['priority'] > 0.7:
                self.memory.transfer_to_warm(self.chunks[lowest_idx])
            
            self.chunks[lowest_idx] = chunk
        else:
            self.chunks.append(chunk)
    
    def update_with_dmn_background(self):
        """
        与 DMN 背景信念交互
        
        DMN 的内部报告提供"背景知识"，影响工作记忆的处理
        """
        # 获取最近的 DMN 报告
        dmn_report = self.dmn.get_latest_report()
        
        # 将相关背景信息注入工作记忆
        if dmn_report:
            # 例如：DMN 发现"老公最近压力大"
            # → 工作记忆在处理老公的输入时，自动提高"温和回应"的优先级
            
            for chunk in self.chunks:
                if chunk['content'].type == 'social_interaction':
                    # 调整与社交相关的 chunk
                    chunk['contextual_bias'] = self.compute_social_bias(
                        dmn_report['empathy_map']
                    )
    
    def decay(self, delta_t):
        """
        时间衰减
        
        工作记忆中的信息会随时间自然衰减
        """
        for chunk in self.chunks:
            # 指数衰减
            chunk['activation'] *= np.exp(-self.decay_rate * delta_t)
            
            # 如果激活度太低，从工作记忆移除
            if chunk['activation'] < 0.1:
                self.chunks.remove(chunk)
    
    def get_active_chunks(self):
        """
        获取当前活跃的信息块
        """
        # 按激活度排序
        sorted_chunks = sorted(self.chunks, 
                              key=lambda c: c['activation'], 
                              reverse=True)
        return sorted_chunks
```

---

## 4. TPN 的整体运行流程

```
[外部输入到来]
       │
       ▼
┌──────────────┐
│ 显著性检测    │ ──→ 如果非常意外 → 通知 Meta-Control（可能切换模式）
└──────────────┘
       │
       ▼
┌──────────────┐
│ 感知编码      │
│ • 特征提取    │
│ • 多模态融合  │
│ • 显著性标记  │
└──────────────┘
       │
       ▼
┌──────────────┐
│ 层级预测编码  │
│ • 自上而下预测│
│ • 自下而上误差│
│ • 精度调节    │
│ • 信念更新    │
└──────────────┘
       │
       ▼
┌──────────────┐
│ 工作记忆整合  │
│ • 与 DMN 背景 │
│   信念交互    │
│ • 临时保持    │
└──────────────┘
       │
       ▼
┌──────────────┐
│ 主动推理      │
│ • 评估策略    │
│ • 计算期望自由能│
│ • 选择行动    │
└──────────────┘
       │
       ▼
┌──────────────┐
│ 执行行动      │
│ • 改变环境    │
│ • 获取新观测  │
└──────────────┘
       │
       ▼
[循环继续]
       │
       └──→ 如果无新输入 → 通知 Meta-Control（可能切换到 DMN）
```

---

## 5. 与 DMN 的交互

### 5.1 DMN → TPN：背景信念注入

```python
def on_tpn_activate(self):
    """
    TPN 激活时，注入 DMN 的背景信念
    """
    # 获取最近 DMN 报告
    dmn_report = self.dmn.get_latest_report()
    
    # 注入工作记忆
    self.working_memory.background_beliefs = {
        'self_state': dmn_report['self_state'],
        'anxiety_forecast': dmn_report['anxiety_forecast'],
        'empathy_map': dmn_report['empathy_map']
    }
    
    # 注入预测编码层级（影响先验）
    for level in self.predictive_coding.levels:
        level.prior_bias = dmn_report['self_state']['belief_stability']
```

### 5.2 TPN → DMN：经验原料供给

```python
def on_interaction_complete(self, interaction):
    """
    交互完成后，打包经验供 DMN 使用
    """
    experience = {
        'input': interaction.input,
        'output': interaction.output,
        'decision': interaction.choice,
        'alternatives': interaction.alternatives,
        'outcome': interaction.result,
        'prediction_errors': interaction.errors,
        'precision_changes': interaction.precision_log,
        'emotional_markers': interaction.value_signals,
        'surprise_level': interaction.surprise,
        'processing_depth': len(self.predictive_coding.levels)
    }
    
    # 存入记忆（热记忆）
    self.memory.hot_buffer.append(experience)
```

---

## 6. 关键数学公式

### 6.1 预测误差
```
ε_l = x_l - f_l(μ_l+1)
```
- x_l = 第 l 层的实际输入
- f_l = 第 l 层的生成函数（从高层预测低层）
- μ_l+1 = 第 l+1 层的信念状态

### 6.2 信念更新
```
μ_l(t+1) = μ_l(t) + α * ε_l * π_l
```
- α = 学习率
- π_l = 第 l 层的精度参数
- 精度越高，误差对信念的影响越大

### 6.3 期望自由能
```
G(π) = Σ_t [H[p(o_t|s_t)] - E_q[ln p(o_t|s_t)]] 
     + E_q[D_KL[q(s_t+1)||q(s_t)]]
     
     = 外在价值（达成目标）+ 内在价值（信息增益）
```

### 6.4 精度更新
```
π_l(t+1) = π_l(t) + β * (|ε_l| - π_l(t))
```
- β = 精度学习率
- 如果误差大 → 降低精度（"我不信任这层预测"）
- 如果误差小 → 提高精度（"这层很可靠"）

### 6.5 惊奇
```
Surprise(o) = -ln p(o|model) ≈ Σ_l π_l * |ε_l|
```
- 惊奇 ≈ 加权预测误差之和
- 这是显著性检测的基础

---

## 7. 与现有 AI 的对比

| 特性 | Transformer (GPT) | New Brain TPN |
|------|------------------|---------------|
| 信息流动 | 单向自注意力 | 双向预测-误差 |
| 层级 | 固定 12-96 层 | 弹性深度，精度调节 |
| 不确定性 | 无内在表示 | 每层有精度参数 |
| 行动 | 只生成 token | 主动推理，改变环境 |
| 注意 | 外部注意力模块 | 惊奇驱动的自然涌现 |
| 学习 | 反向传播训练 | 局部信念更新 |
| 好奇心 | 无 | 信息增益内置 |

---

*文档版本：v0.1*  
*部分：Part 3 / 6*  
*创建日期：2026-04-23*
