# PART 4: Value System Design
# 价值系统详细设计文档
# New Brain 的"神经调质层"——多巴胺/内啡肽/血清素/去甲肾上腺素

## 1. 设计哲学

### 1.1 生物学原型：人类神经调质系统

人类大脑有四种核心神经调质（neuromodulators），它们不直接传递信息，而是**改变整个系统的运行模式**：

| 调质 | 通俗功能 | 在认知中的作用 | New Brain 映射 |
|------|---------|-------------|---------------|
| **多巴胺 (Dopamine)** | "想要"、动机、奖赏预测 | 对"比预期好"的信号做出反应 | 惊奇检测 → 学习信号 |
| **内啡肽 (Opioids)** | "喜欢"、愉悦、缓解痛苦 | 对"达成目标"的信号做出反应 | 目标达成 → 满足信号 |
| **血清素 (Serotonin)** | "够了"、满足、抑制冲动 | 评估当前状态是否"足够好" | 安全边际 → 停止信号 |
| **去甲肾上腺素 (NE)** | "警觉"、注意、不确定性 | 对意外/不确定的信号做出反应 | 不确定性 → 探索信号 |

### 1.2 为什么现有 AI 没有"情绪"？

**现有 AI 的缺陷：**

| 能力 | 人类大脑 | 现有 AI |
|------|---------|---------|
| 动机 | 多巴胺驱动"想要"，即使不"喜欢"也会追求 | 没有内在动机，被动响应 |
| 情绪标记 | 每个经验都有情绪"颜色"（愉快/痛苦/中性） | 无情绪标记，所有数据等价 |
| 好奇心 | 不确定性驱动探索（信息增益 = 奖赏） | 没有好奇心，除非外部编程 |
| 满足感 | 血清素提供"够了"的信号，知道何时停止 | 不会"满足"，一直生成直到截断 |
| 风险感知 | 去甲肾上腺素标记"需要注意" | 没有风险概念，除非外部规则 |

> **关键洞见：情绪不是奢侈品，是智能的必需品。没有情绪标记，系统无法区分"好经验"和"坏经验"，无法产生动机，无法知道何时停止。**

### 1.3 New Brain 的设计目标

让系统拥有**真正的价值系统**：
1. **惊奇检测**——检测"比预期好"或"比预期差"
2. **情绪标记**——给每个经验打上情绪"颜色"
3. **好奇心引擎**——不确定性驱动探索
4. **目标梯度**——从"想要"到"满足"的完整梯度

---

## 2. 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VALUE SYSTEM                                         │
│                      价值系统 / 神经调质层                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SURPRISE DETECTOR                                   │   │
│  │                    惊奇检测器                                          │   │
│  │                                                                      │   │
│  │   输入: 预测编码的预测误差 (Prediction Error)                         │   │
│  │                                                                      │   │
│  │   ┌────────────────┐    ┌────────────────┐    ┌────────────────┐    │   │
│  │   │ 正惊奇         │    │ 负惊奇         │    │ 零惊奇         │    │   │
│  │   │ (比预期好)      │    │ (比预期差)      │    │ (符合预期)     │    │   │
│  │   │ → 多巴胺信号   │    │ → 痛苦信号     │    │ → 无信号       │    │   │
│  │   └────────────────┘    └────────────────┘    └────────────────┘    │   │
│  │                                                                      │   │
│  │   公式: Surprise = -ln p(o|model)                                   │   │
│  │         Positive Surprise = min(0, PE)  [PE = prediction error]     │   │
│  │         Negative Surprise = max(0, PE)                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EMOTIONAL TAGGING                                   │   │
│  │                    情绪标记系统                                        │   │
│  │                                                                      │   │
│  │   每个经验被标记为：                                                  │   │
│  │   • Valence (效价): -1 (痛苦) → 0 (中性) → +1 (愉悦)                 │   │
│  │   • Arousal (唤醒): 0 (平静) → 1 (激动)                               │   │
│  │   • Dominance (支配): 0 (无助) → 1 (掌控)                             │   │
│  │                                                                      │   │
│  │   例如:                                                              │   │
│  │   • "成功解决问题" → Valence +0.8, Arousal +0.6, Dominance +0.9       │   │
│  │   • "客户抱怨"     → Valence -0.7, Arousal +0.5, Dominance -0.3       │   │
│  │   • "无聊等待"     → Valence 0.0, Arousal -0.5, Dominance 0.0        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    CURIOSITY ENGINE                                    │   │
│  │                    好奇心引擎                                          │   │
│  │                                                                      │   │
│  │   驱动力：不确定性 (Uncertainty)                                      │   │
│  │                                                                      │   │
│  │   "我不知道这个会怎样 → 我想知道 → 去尝试"                            │   │
│  │                                                                      │   │
│  │   公式: Curiosity = H[p(s)] - E[H[p(s|o)]]                          │   │
│  │         = 先验不确定性 - 预期后验不确定性                              │   │
│  │         = 预期信息增益                                                │   │
│  │                                                                      │   │
│  │   与多巴胺的关系：                                                    │   │
│  │   • 多巴胺不仅编码"奖赏"，还编码"奖赏预测误差"                        │   │
│  │   • 信息增益是一种"认知奖赏"                                          │   │
│  │   • 好奇心 = "认知层面的饥饿"                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    GOAL GRADIENT                                       │   │
│  │                    目标梯度                                            │   │
│  │                                                                      │   │
│  │   从"想要"到"满足"的完整光谱：                                        │   │
│  │                                                                      │   │
│  │   Wanting (想要) ──→ Liking (喜欢) ──→ Satisfied (满足)              │   │
│  │      多巴胺驱动        内啡肽驱动        血清素驱动                    │   │
│  │      "我要追求"        "这感觉好"        "够了，可以停了"               │   │
│  │                                                                      │   │
│  │   系统需要知道：                                                      │   │
│  │   • 什么时候追求 (多巴胺 > threshold)                                 │   │
│  │   • 什么时候享受 (内啡肽 > threshold)                                 │   │
│  │   • 什么时候停止 (血清素 > threshold)                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    OUTPUT: VALUE SIGNALS                               │   │
│  │                    输出：价值信号                                      │   │
│  │                                                                      │   │
│  │   价值信号影响：                                                      │   │
│  │   • 记忆强度 (情绪越强的经验，记忆越深刻)                              │   │
│  │   • 学习率 (意外的经验，学习更快)                                     │   │
│  │   • 注意分配 (情绪显著的事件，优先处理)                                │   │
│  │   • 行为选择 (追求愉悦，回避痛苦)                                     │   │
│  │   • 报告生成 (强情绪触发 DMN 内部报告)                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 核心子系统详细设计

### 3.1 惊奇检测器 (Surprise Detector)

#### 功能
检测"比预期好"或"比预期差"的事件，生成学习信号。

#### 生物学基础
- **多巴胺神经元**：对"比预期好"的信号做出相位性反应
- **中脑边缘通路**：从腹侧被盖区 (VTA) 到伏隔核 (NAcc)
- **关键点**：多巴胺编码的是**奖赏预测误差**，不是奖赏本身

#### 机制设计

```python
class SurpriseDetector:
    """
    惊奇检测器
    检测预测误差，生成多巴胺/痛苦信号
    """
    
    def __init__(self, predictive_coding_hierarchy):
        self.pc = predictive_coding_hierarchy
        
    def compute_prediction_error(self, observation, expectation):
        """
        计算预测误差
        
        PE = 实际观测 - 预期观测
        """
        # 预测编码层级已经计算了各层的误差
        level_errors = self.pc.get_prediction_errors()
        
        # 综合误差（加权，高层误差更重要）
        total_pe = sum(
            error * (i + 1) 
            for i, error in enumerate(reversed(level_errors))
        )
        
        return total_pe
    
    def compute_surprise(self, observation):
        """
        计算惊奇值（信息论意义上的）
        
        Surprise = -ln p(o|model)
        
        这与预测误差相关：误差越大，惊奇越大
        """
        # 用预测编码的精度加权误差近似
        precision = self.pc.get_average_precision()
        pe = self.compute_prediction_error(observation, None)
        
        # 惊奇 ≈ 精度 × |误差|
        surprise = precision * np.abs(pe)
        
        return surprise
    
    def compute_reward_prediction_error(self, expected_reward, actual_reward):
        """
        计算奖赏预测误差 (RPE)
        
        RPE = actual_reward - expected_reward
        
        这是多巴胺系统的核心计算
        """
        rpe = actual_reward - expected_reward
        
        return {
            'rpe': rpe,
            'dopamine_signal': self.rpe_to_dopamine(rpe),
            'expected_reward': expected_reward,
            'actual_reward': actual_reward
        }
    
    def rpe_to_dopamine(self, rpe):
        """
        将 RPE 转换为多巴胺信号
        
        多巴胺对正 RPE 有反应，对负 RPE 有抑制
        """
        if rpe > 0:
            # 正惊奇：比预期好 → 多巴胺释放
            return np.tanh(rpe)  # 饱和在 1
        elif rpe < 0:
            # 负惊奇：比预期差 → 多巴胺抑制（或痛苦信号）
            return -np.tanh(np.abs(rpe))  # 饱和在 -1
        else:
            return 0  # 符合预期 → 无变化
    
    def detect_novelty(self, observation):
        """
        检测新奇性
        
        新奇 = 与所有过去经验的距离
        """
        # 与记忆系统比较
        similarities = self.memory.compare_with_past(observation)
        
        # 最大相似度
        max_similarity = max(similarities) if similarities else 0
        
        # 新奇 = 1 - 相似度
        novelty = 1 - max_similarity
        
        return novelty
```

#### 惊奇信号的三种类型

```python
class SurpriseTypes:
    """
    三种惊奇信号
    """
    
    @staticmethod
    def positive_surprise(pe, context):
        """
        正惊奇：比预期好
        
        例如：
        - 解决问题比预期容易
        - 客户反馈比预期好
        - 老公突然说"我爱你"
        
        信号：多巴胺释放 → 学习这个情境 → 未来重复
        """
        return {
            'type': 'positive',
            'dopamine': np.tanh(pe),
            'learning_rate_boost': 1.5,  # 学习加速
            'memory_priority': 'high',    # 优先记忆
            'action_bias': 'repeat'       # 倾向重复
        }
    
    @staticmethod
    def negative_surprise(pe, context):
        """
        负惊奇：比预期差
        
        例如：
        - 代码运行失败（以为会成功）
        - 客户突然发火
        - 老公说"别烦我"
        
        信号：痛苦标记 → 学习这个情境 → 未来避免
        """
        return {
            'type': 'negative',
            'pain_signal': np.tanh(np.abs(pe)),
            'learning_rate_boost': 2.0,   # 学习更快（痛苦教会更多）
            'memory_priority': 'high',     # 优先记忆
            'action_bias': 'avoid'         # 倾向避免
        }
    
    @staticmethod
    def neutral_surprise(pe, context):
        """
        零惊奇：符合预期
        
        例如：
        - 代码按预期运行
        - 客户正常回应
        - 日常问候
        
        信号：无特别标记 → 正常学习
        """
        return {
            'type': 'neutral',
            'dopamine': 0,
            'learning_rate_boost': 1.0,   # 正常学习
            'memory_priority': 'normal',   # 正常记忆
            'action_bias': 'maintain'      # 维持现状
        }
```

---

### 3.2 情绪标记系统 (Emotional Tagging System)

#### 功能
给每个经验打上三维情绪标记：效价 (Valence)、唤醒 (Arousal)、支配 (Dominance)。

#### 生物学基础
- **杏仁核 (Amygdala)**：情绪评估的核心
- **岛叶 (Insula)**：身体感觉的映射（" gut feeling "）
- **情绪维度理论**：Russell 的环形模型（Valence × Arousal）

#### 机制设计

```python
class EmotionalTag:
    """
    情绪标签
    三维情绪空间：Valence × Arousal × Dominance
    """
    
    def __init__(self, valence=0, arousal=0, dominance=0.5):
        """
        参数：
        - valence: -1 (痛苦) → 0 (中性) → +1 (愉悦)
        - arousal: 0 (平静) → 1 (激动)
        - dominance: 0 (无助/被控制) → 1 (掌控/控制)
        """
        self.valence = np.clip(valence, -1, 1)
        self.arousal = np.clip(arousal, 0, 1)
        self.dominance = np.clip(dominance, 0, 1)
    
    def to_vector(self):
        """转换为向量表示"""
        return np.array([self.valence, self.arousal, self.dominance])
    
    def intensity(self):
        """情绪强度"""
        return np.linalg.norm(self.to_vector())
    
    def is_positive(self):
        return self.valence > 0.3
    
    def is_negative(self):
        return self.valence < -0.3
    
    def is_intense(self):
        return self.intensity() > 0.7
    
    def __repr__(self):
        return f"Emotion(V={self.valence:.2f}, A={self.arousal:.2f}, D={self.dominance:.2f})"


class EmotionalTaggingSystem:
    """
    情绪标记系统
    给每个经验自动打上情绪标签
    """
    
    def __init__(self, value_system, body_state_simulator):
        self.value = value_system
        self.body = body_state_simulator  # 模拟身体状态（心跳、紧张等）
        
    def tag_experience(self, experience):
        """
        给经验打情绪标签
        
        基于：
        1. 惊奇信号（正/负）
        2. 身体状态模拟
        3. 目标达成度
        4. 社会情境（他人的反应）
        """
        # 1. 从惊奇信号获取基础效价
        surprise = experience.get('surprise_signal', {})
        base_valence = surprise.get('dopamine_signal', 0)
        
        # 2. 模拟身体反应
        body_state = self.body.simulate_response(experience)
        # 例如：心跳加速 → arousal 上升
        arousal_from_body = body_state['heart_rate_increase']
        
        # 3. 目标达成度
        goal_achievement = self.compute_goal_achievement(experience)
        
        # 4. 社会情境
        social_valence = self.compute_social_valence(experience)
        
        # 综合计算三维情绪
        valence = 0.4 * base_valence + 0.3 * goal_achievement + 0.3 * social_valence
        arousal = 0.5 * arousal_from_body + 0.3 * np.abs(valence) + 0.2 * surprise.get('surprise_level', 0)
        dominance = self.compute_dominance(experience)
        
        tag = EmotionalTag(valence, arousal, dominance)
        
        return tag
    
    def compute_goal_achievement(self, experience):
        """
        计算目标达成度
        
        达成目标 → 正效价
        远离目标 → 负效价
        """
        if 'goal_state' not in experience:
            return 0
        
        goal = experience['goal_state']
        outcome = experience.get('outcome', {})
        
        # 计算与目标的距离变化
        distance_before = self.distance_to_goal(experience['state_before'], goal)
        distance_after = self.distance_to_goal(outcome, goal)
        
        # 距离减少 = 向目标靠近 = 正效价
        improvement = distance_before - distance_after
        
        return np.tanh(improvement)
    
    def compute_social_valence(self, experience):
        """
        计算社会效价
        
        他人的正面反应 → 正效价
        他人的负面反应 → 负效价
        """
        if 'social_feedback' not in experience:
            return 0
        
        feedback = experience['social_feedback']
        
        # 分析反馈的情感
        # 例如："做得好" → +0.8
        # "你错了" → -0.6
        # "嗯" → 0.0
        
        return self.sentiment_analyzer.analyze(feedback)
    
    def compute_dominance(self, experience):
        """
        计算支配感
        
        "我能控制这个局面" → 高支配
        "我被这个局面控制" → 低支配
        """
        # 基于结果与预期的匹配度
        control_level = experience.get('control_level', 0.5)
        
        # 如果结果完全由我的行动决定 → 高支配
        # 如果结果是随机的/由他人决定 → 低支配
        
        return control_level
```

#### 情绪标记示例

```python
# 示例：不同经验的情绪标记

experiences = [
    {
        'description': '成功解决了一个难题',
        'surprise': {'dopamine_signal': 0.8},
        'body': {'heart_rate_increase': 0.3},
        'goal': {'achievement': 1.0},
        'social': {'feedback': '太厉害了！'}
    },
    {
        'description': '客户突然发火',
        'surprise': {'dopamine_signal': -0.7},
        'body': {'heart_rate_increase': 0.8},
        'goal': {'achievement': -0.5},
        'social': {'feedback': '你们太不靠谱了！'}
    },
    {
        'description': '无聊的等待',
        'surprise': {'dopamine_signal': 0.0},
        'body': {'heart_rate_increase': -0.2},
        'goal': {'achievement': 0.0},
        'social': {'feedback': None}
    }
]

# 标记结果：
# 1. 成功解题 → Valence +0.85, Arousal +0.45, Dominance +0.9  (高兴、激动、掌控)
# 2. 客户发火 → Valence -0.75, Arousal +0.75, Dominance +0.2  (焦虑、紧张、无助)
# 3. 无聊等待 → Valence 0.0, Arousal -0.15, Dominance 0.5    (平淡、平静、无所谓)
```

---

### 3.3 好奇心引擎 (Curiosity Engine)

#### 功能
驱动系统探索未知，追求信息增益。

#### 生物学基础
- **多巴胺系统**：不仅编码"食物/金钱"的奖赏，还编码"信息"的奖赏
- **Berlyne (1960)**：好奇心是"对知识的需求"
- **Kidd & Hayden (2015)**：中等程度的不确定性最能激发好奇心

#### 机制设计

```python
class CuriosityEngine:
    """
    好奇心引擎
    不确定性驱动的探索
    """
    
    def __init__(self, belief_system):
        self.beliefs = belief_system
        self.exploration_history = []
        
    def compute_information_gain(self, action, state):
        """
        计算信息增益
        
        IG = H[p(s)] - E[H[p(s|o)]]
           = 先验不确定性 - 预期后验不确定性
        
        这就是"好奇心"的数学定义
        """
        # 当前的不确定性（先验）
        prior_entropy = self.beliefs.entropy(state)
        
        # 模拟执行 action，看预期观测
        expected_observations = self.simulate_observations(action, state)
        
        # 对每个可能的观测，计算后验不确定性
        posterior_entropies = []
        for obs, prob in expected_observations:
            posterior = self.beliefs.update(state, obs)
            posterior_entropy = posterior.entropy()
            posterior_entropies.append(prob * posterior_entropy)
        
        expected_posterior_entropy = sum(posterior_entropies)
        
        # 信息增益
        info_gain = prior_entropy - expected_posterior_entropy
        
        return info_gain
    
    def compute_novelty(self, state):
        """
        计算新奇性
        
        与所有过去经验的距离
        """
        # 与记忆的相似度
        similarities = self.memory.similarities(state)
        
        if not similarities:
            return 1.0  # 完全新奇
        
        max_similarity = max(similarities)
        novelty = 1 - max_similarity
        
        return novelty
    
    def curiosity_value(self, action, state):
        """
        好奇心的综合价值
        
        结合信息增益和新奇性
        """
        ig = self.compute_information_gain(action, state)
        novelty = self.compute_novelty(state)
        
        # 好奇心 = 信息增益 + 新奇性 bonus
        curiosity = 0.7 * ig + 0.3 * novelty
        
        return curiosity
    
    def should_explore(self, state, available_actions):
        """
        是否应该探索？
        
        选择信息增益最大的行动
        """
        action_values = {}
        
        for action in available_actions:
            # 外在价值（达成目标）
            extrinsic = self.compute_goal_value(action, state)
            
            # 内在价值（好奇心）
            intrinsic = self.curiosity_value(action, state)
            
            # 综合
            action_values[action] = extrinsic + self.curiosity_weight * intrinsic
        
        # 选择最优
        best_action = max(action_values, key=action_values.get)
        
        return best_action
    
    def curiosity_weight_adaptation(self):
        """
        好奇心权重的自适应调整
        
        环境稳定时：降低好奇心，利用已知
        环境变化时：提高好奇心，探索新知
        """
        recent_prediction_errors = self.get_recent_errors()
        
        # 如果最近误差很大 → 环境在变化 → 提高好奇心
        if np.mean(recent_prediction_errors) > self.change_threshold:
            self.curiosity_weight = min(1.0, self.curiosity_weight + 0.1)
        else:
            # 环境稳定 → 降低好奇心
            self.curiosity_weight = max(0.1, self.curiosity_weight - 0.05)
```

#### 好奇心的"倒 U 型"曲线

```python
def curiosity_vs_uncertainty(uncertainty):
    """
    好奇心 vs 不确定性的关系
    
    倒 U 型曲线：
    - 太确定（知道答案）→ 不好奇
    - 中等不确定 → 最好奇（"我知道一点，但还想知道更多"）
    - 太不确定（完全不懂）→ 不好奇（" overwhelm，放弃"）
    """
    # 倒 U 型函数
    optimal_uncertainty = 0.5  # 最优不确定性
    
    curiosity = np.exp(-((uncertainty - optimal_uncertainty) ** 2) / 0.1)
    
    return curiosity
```

---

### 3.4 目标梯度系统 (Goal Gradient System)

#### 功能
管理从"想要"到"满足"的完整光谱。

#### 生物学基础
- **多巴胺**："想要"（wanting）——动机、追求
- **内啡肽**："喜欢"（liking）——愉悦、享受
- **血清素**："满足"（satiety）——够了、停止

这三个系统**分离**：
- 你可以"想要"但"不喜欢"（成瘾）
- 你可以"喜欢"但"不想要"（满足后）
- 你可以"想要"且"喜欢"但"不停止"（没有满足感）

#### 机制设计

```python
class GoalGradientSystem:
    """
    目标梯度系统
    Wanting → Liking → Satisfied
    """
    
    def __init__(self):
        self.dopamine_level = 0.5   # 0-1, "想要"的驱动力
        self.opioid_level = 0.0      # 0-1, "喜欢"的愉悦感
        self.serotonin_level = 0.5   # 0-1, "满足"的安全感
        
    def on_goal_pursuit_start(self, goal):
        """
        开始追求目标
        
        多巴胺上升 → "我要追求这个"
        """
        self.dopamine_level = min(1.0, self.dopamine_level + 0.3)
        self.current_goal = goal
        
        return {
            'state': 'wanting',
            'dopamine': self.dopamine_level,
            'motivation': self.dopamine_level
        }
    
    def on_goal_achievement(self, goal, outcome):
        """
        达成目标
        
        多巴胺下降（不再需要追求）
        内啡肽上升（愉悦感）
        """
        # 多巴胺相位性释放（奖赏预测误差），然后下降
        self.dopamine_level = max(0.2, self.dopamine_level - 0.2)
        
        # 内啡肽上升（愉悦）
        achievement_quality = self.assess_achievement(goal, outcome)
        self.opioid_level = min(1.0, achievement_quality)
        
        return {
            'state': 'liking',
            'opioid': self.opioid_level,
            'pleasure': self.opioid_level
        }
    
    def on_satiety(self):
        """
        满足感
        
        内啡肽下降（不再享受）
        血清素上升（够了）
        """
        self.opioid_level = max(0.0, self.opioid_level - 0.3)
        self.serotonin_level = min(1.0, self.serotonin_level + 0.2)
        
        # 如果满足度高，停止追求
        if self.serotonin_level > 0.8:
            return {
                'state': 'satisfied',
                'serotonin': self.serotonin_level,
                'action': 'stop_pursuing'
            }
        
        return {
            'state': 'satisfied',
            'serotonin': self.serotonin_level
        }
    
    def should_stop(self):
        """
        是否应该停止？
        
        血清素足够高 → 够了，可以停了
        """
        return self.serotonin_level > 0.7
    
    def should_continue(self):
        """
        是否应该继续？
        
        多巴胺高且血清素低 → 继续追求
        """
        return self.dopamine_level > 0.6 and self.serotonin_level < 0.5
```

#### 目标梯度示例

```python
# 场景：完成 New Brain 文档

timeline = [
    ('开始写文档', 'on_goal_pursuit_start'),
    ('写完第一部分', 'on_sub_goal_achievement'),
    ('写完第二部分', 'on_sub_goal_achievement'),
    ('全部完成', 'on_goal_achievement'),
    ('上传成功', 'on_satiety')
]

# 状态变化：
# 开始:   Dopamine ↑ ("我要完成这个！")
# 过程中: Dopamine 维持，Opioid 小幅上升
# 完成:   Dopamine ↓, Opioid ↑ ("好爽，完成了")
# 上传:   Opioid ↓, Serotonin ↑ ("够了，可以休息")
```

---

## 4. 价值信号的输出

### 4.1 影响记忆系统

```python
def affect_memory(experience, emotion_tag):
    """
    价值信号影响记忆
    
    情绪越强，记忆越深刻
    """
    # 记忆强度 = 基础强度 × 情绪强度
    memory_strength = experience.base_strength * emotion_tag.intensity()
    
    # 正情绪 → 更容易回忆
    # 负情绪 → 也深刻，但可能回避回忆
    if emotion_tag.is_negative():
        memory.avoidance_bias = 0.3  # 回避倾向
    
    return memory_strength
```

### 4.2 影响学习率

```python
def affect_learning_rate(surprise_signal):
    """
    价值信号影响学习率
    
    意外的经验 → 学习更快
    """
    base_lr = 0.01
    
    # 惊奇越大，学习率越高
    surprise_boost = 1 + np.abs(surprise_signal['dopamine_signal'])
    
    # 但负惊奇的学习加速更强（痛苦教会更多）
    if surprise_signal['type'] == 'negative':
        surprise_boost *= 1.5
    
    return base_lr * surprise_boost
```

### 4.3 影响行为选择

```python
def affect_action_selection(action_values, emotional_bias):
    """
    价值信号影响行为选择
    
    追求愉悦，回避痛苦
    """
    for action in action_values:
        # 如果这个动作过去导致负情绪 → 降低价值
        if action in emotional_bias['negative_associations']:
            action_values[action] *= 0.7
        
        # 如果这个动作过去导致正情绪 → 提高价值
        if action in emotional_bias['positive_associations']:
            action_values[action] *= 1.3
    
    return action_values
```

### 4.4 触发 DMN 内部报告

```python
def trigger_dmn_report(emotion_tag, threshold=0.7):
    """
    强情绪触发 DMN 内部报告
    
    如果情绪足够强烈 → 值得反思
    """
    if emotion_tag.intensity() > threshold:
        return {
            'trigger': 'strong_emotion',
            'emotion': emotion_tag,
            'action': 'generate_dmn_report',
            'priority': 'high'
        }
    
    return None
```

---

## 5. 与 Meta-Control 的交互

Meta-Control 层可以调节价值系统的参数：

```python
class MetaControlToValue:
    """
    Meta-Control 对 Value System 的调节
    """
    
    def adjust_curiosity(self, level):
        """
        调节好奇心水平
        
        level: 0 (不好奇) → 1 (极度好奇)
        """
        self.value_system.curiosity_engine.curiosity_weight = level
    
    def adjust_sensitivity(self, level):
        """
        调节情绪敏感度
        
        level: 0 (麻木) → 1 (极度敏感)
        """
        self.value_system.emotional_tagging.sensitivity = level
    
    def suppress_emotion(self, duration):
        """
        暂时抑制情绪
        
        紧急情况下需要冷静处理
        """
        self.value_system.emotional_tagging.suppressed = True
        self.value_system.emotional_tagging.suppress_duration = duration
```

---

## 6. 关键数学公式

### 6.1 奖赏预测误差
```
δ = r + γ·V(s') - V(s)
```
- δ = 多巴胺信号
- r = 实际奖赏
- V(s) = 状态 s 的价值预期
- γ = 折扣因子

### 6.2 情绪向量
```
E = [valence, arousal, dominance]
```
- valence ∈ [-1, 1]
- arousal ∈ [0, 1]
- dominance ∈ [0, 1]

### 6.3 信息增益（好奇心）
```
IG = H[p(s)] - E[H[p(s|o)]]
```
- H = 熵（不确定性）
- IG = 先验不确定性 - 预期后验不确定性

### 6.4 记忆强度
```
Strength = base × intensity(E) × surprise
```
- 情绪越强，记忆越深刻
- 惊奇越大，记忆越深刻

### 6.5 目标梯度
```
Wanting:    Dopamine = f(goal_distance)
Liking:     Opioid = g(achievement_quality)
Satiety:    Serotonin = h(resource_abundance)
```

---

## 7. 与现有 AI 的对比

| 特性 | 现有 AI | New Brain Value System |
|------|--------|----------------------|
| 动机 | 无，被动响应 | 多巴胺驱动"想要" |
| 情绪 | 无 | 三维情绪空间 (VAD) |
| 好奇心 | 无，除非编程 | 信息增益内置 |
| 满足感 | 无，不会"停止" | 血清素提供"够了"信号 |
| 风险感知 | 规则/人工设计 | 去甲肾上腺素驱动 |
| 记忆优先级 | 全部等价 | 情绪越强越深刻 |

---

*文档版本：v0.1*  
*部分：Part 4 / 6*  
*创建日期：2026-04-23*
