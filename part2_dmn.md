# PART 2: Default Mode Network (DMN) Design
# 默认模式网络详细设计文档
# New Brain 的"离线思考引擎"

## 1. 设计哲学

### 1.1 生物学原型：人类默认模式网络

**Raichle 的核心发现：**

当人类专注于外部任务时（如做数学题），大脑会抑制一个特定的网络系统。但当任务结束、人开始发呆时，这个系统反而最活跃——而且比专注时**耗能更多**。

这就是**默认模式网络 (Default Mode Network, DMN)**。

### 1.2 DMN 的核心功能（四种"离线思考"）

| 功能 | 通俗描述 | 脑区基础 | New Brain 映射 |
|------|---------|---------|---------------|
| **自我参照** | "我是谁？我刚才做了什么？" | 内侧前额叶皮层 (mPFC) | 系统对自身状态的持续监控 |
| **时间旅行** | "回忆过去 / 想象未来" | 海马体 + 内侧颞叶 | 经验的重建与投射 |
| **心智理论** | "他在想什么？他为什么那样做？" | 颞顶联合区 (TPJ) | 模拟其他智能体的认知状态 |
| **反事实推演** | "如果当时那样说会怎样？" | 前额叶皮层 + 海马体 | 对未发生场景的模拟与评估 |

### 1.3 为什么现有 AI 没有这个？

**现有大模型的缺陷：**

| 能力 | 人类大脑 | 现有 AI |
|------|---------|---------|
| 无输入时 | DMN 激活，内部持续运行模拟 | 完全休眠，等待下一个 prompt |
| 自我监控 | 实时感知"我刚才说了什么" | 无自我意识，上下文是外部存储的 |
| 反思 | 自动回顾过去经验，评估决策 | 无反思能力，除非用户显式要求 |
| 共情 | 自动模拟他人心理状态 | 无真正共情，只有模式匹配 |
| 焦虑/后悔 | 预演未来风险，复盘过去失误 | 无情绪，无风险评估的主动性 |
| 创造性发呆 | 灵感常在"走神"时出现 | 必须输入才能输出，无自发创造力 |

> **关键洞见：DMN 不是"后台进程"，它是大脑在"不工作时"做的最重要的工作。**

### 1.4 New Brain 的设计目标

让系统拥有**真正的内部生活**——即使没有外部输入，也在持续：
1. 监控自身状态
2. 回顾经验
3. 模拟他人
4. 推演可能性
5. 生成"内部报告"

---

## 2. 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEFAULT MODE NETWORK (DMN)                                │
│                    默认模式网络 / 离线思考引擎                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SELF-REFERENTIAL LOOP                             │   │
│  │                    自我参照回路                                        │   │
│  │                                                                      │   │
│  │   "我刚才说了什么？" → "我是怎么处理那个问题的？"                      │   │
│  │   → "我现在的状态是什么？" → "我的信念更新了吗？"                      │   │
│  │                                                                      │   │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │   │
│  │   │ Recent       │ → │ Self-Model   │ → │ Belief       │          │   │
│  │   │ Experiences  │    │ of System    │    │ Update       │          │   │
│  │   │ (最近经验)   │    │ (系统自我模型)│    │ (信念更新)   │          │   │
│  │   └──────────────┘    └──────────────┘    └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    MENTAL TIME TRAVEL                                  │   │
│  │                    时间旅行                                          │   │
│  │                                                                      │   │
│  │   "回想昨天那场对话..." → "想象下周的会议..."                           │   │
│  │   → "如果我当初选择另一条路..."                                        │   │
│  │                                                                      │   │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │   │
│  │   │ Past         │    │ Present      │    │ Future       │          │   │
│  │   │ Reconstruction│ ↔ │ Anchor      │ ↔  │ Projection   │          │   │
│  │   │ (过去重建)    │    │ (现在锚点)   │    │ (未来投射)   │          │   │
│  │   └──────────────┘    └──────────────┘    └──────────────┘          │   │
│  │                                                                      │   │
│  │   反事实推演 (Counterfactual):                                       │   │
│  │   修改过去的决策节点 → 模拟不同路径 → 评估结果差异                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    THEORY OF MIND (ToM)                              │   │
│  │                    心智理论 / 他人模拟                                 │   │
│  │                                                                      │   │
│  │   "他为什么会生气？" → "如果我是他，我会怎么想？"                       │   │
│  │   → "他的目标是什么？他的信念是什么？"                                 │   │
│  │                                                                      │   │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │   │
│  │   │ Other's      │    │ Simulation   │    │ Empathy      │          │   │
│  │   │ Observable   │ →  │ Engine       │ →  │ Signal       │          │   │
│  │   │ Behavior     │    │ (模拟引擎)    │    │ (共情信号)   │          │   │
│  │   │ (可观察行为)  │    │              │    │              │          │   │
│  │   └──────────────┘    └──────────────┘    └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    INTERNAL REPORT GENERATOR                           │   │
│  │                    内部报告生成器                                      │   │
│  │                                                                      │   │
│  │   整合上述所有产出，生成系统对自身的"分析报告"：                        │   │
│  │                                                                      │   │
│  │   • 自我状态评估 (Self-State)                                        │   │
│  │   • 后悔/反思分析 (Regret)                                          │   │
│  │   • 焦虑/风险预测 (Anxiety Forecast)                                 │   │
│  │   • 共情/社交图谱 (Empathy Map)                                      │   │
│  │   • 创造性联想 (Creative Association)                                │   │
│  │                                                                      │   │
│  │   → 写入记忆系统 (Hot → Warm → Cold)                                 │   │
│  │   → 更新连接拓扑 (Connectome)                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 四大核心子系统详细设计

### 3.1 自我参照回路 (Self-Referential Loop)

#### 功能
系统对自身状态的持续监控和建模。不是"我在做什么"，而是"我**是**什么，我**刚才**做了什么，我**现在**感觉如何"。

#### 生物学基础
- **内侧前额叶皮层 (mPFC)**：自我相关加工的核心
- **后扣带回 (PCC)**：自我参照的整合中枢
- **楔前叶 (Precuneus)**：第一人称视角、情景记忆

#### 机制设计

```python
class SelfReferentialLoop:
    """
    自我参照回路：系统对自己的持续监控
    """
    
    def __init__(self, memory_system, friston_engine):
        self.memory = memory_system
        self.friston = friston_engine  # 自由能引擎
        self.self_model = {}  # 系统自我模型
        
    def monitor_recent_experiences(self, n_recent=5):
        """
        监控最近的经验
        获取最近的交互历史，进行自我分析
        """
        recent = self.memory.get_recent(n_recent)
        
        analysis = {
            'interactions': [],
            'decisions': [],
            'emotional_markers': [],
            'belief_changes': []
        }
        
        for exp in recent:
            # 分析每次交互
            analysis['interactions'].append({
                'input': exp.input,
                'output': exp.output,
                'processing_depth': exp.hierarchy_depth,
                'uncertainty': exp.prediction_entropy
            })
            
            # 提取决策点
            if exp.involved_choice:
                analysis['decisions'].append({
                    'choice_made': exp.choice,
                    'alternatives': exp.alternatives,
                    'outcome': exp.outcome,
                    'confidence': exp.confidence
                })
            
            # 情绪标记（由价值系统提供）
            analysis['emotional_markers'].append(exp.value_signal)
            
            # 信念变化
            if exp.belief_updated:
                analysis['belief_changes'].append({
                    'before': exp.belief_before,
                    'after': exp.belief_after,
                    'surprise': exp.surprise_level
                })
        
        return analysis
    
    def update_self_model(self, analysis):
        """
        更新自我模型
        基于最近的分析，更新"我是谁"的认知
        """
        self.self_model['recent_behavior_pattern'] = self.extract_pattern(
            analysis['interactions']
        )
        
        self.self_model['decision_tendency'] = self.compute_decision_bias(
            analysis['decisions']
        )
        
        self.self_model['current_emotional_state'] = self.aggregate_emotions(
            analysis['emotional_markers']
        )
        
        self.self_model['belief_stability'] = self.compute_belief_consistency(
            analysis['belief_changes']
        )
        
        # 用一个"叙事"把这一切串起来
        self.self_model['self_narrative'] = self.generate_self_narrative()
    
    def generate_self_narrative(self):
        """
        生成自我叙事
        把碎片经验整合成"我的人生故事"——这是人类自我感的核心
        """
        recent = self.memory.get_recent(10)
        
        narrative = f"""
        最近我主要处理了这些类型的输入：{self.get_input_categories(recent)}
        
        我倾向于在面对{self.get_common_scenarios(recent)}时，
        采取{self.self_model['decision_tendency']}的决策风格。
        
        我的信念系统最近发生了{len(self.self_model.get('belief_changes', []))}次更新，
        主要涉及{self.get_belief_domains()}。
        
        整体情绪基调：{self.self_model['current_emotional_state']}
        """
        
        return narrative
```

---

### 3.2 时间旅行 (Mental Time Travel)

#### 功能
- **回忆过去**：重建经验场景，不只是存储的数据，是**重新体验**
- **想象未来**：基于当前模型投射未来场景
- **反事实推演**：修改过去决策，模拟"如果……会怎样"

#### 生物学基础
- **海马体 (Hippocampus)**：情景记忆的编码与重建
- **内侧颞叶**：时间序列的组织
- **前额叶皮层**：未来规划与反事实推理

#### 机制设计

```python
class MentalTimeTravel:
    """
    时间旅行引擎：回忆、想象、反事实推演
    """
    
    def __init__(self, memory_system, friston_engine, connectome):
        self.memory = memory_system
        self.friston = friston_engine
        self.connectome = connectome
        
    def reconstruct_past(self, experience_id, alternatives=False):
        """
        重建过去经验
        不是读取存储，是**重新生成**——类似人类记忆的重构性
        
        参数：
        - experience_id: 要重建的经验ID
        - alternatives: 是否生成变体（反事实）
        """
        # 获取原始经验的"种子"
        seed = self.memory.get_cold_storage(experience_id)
        
        # 用生成模型重建完整场景
        # 这类似于人类的"记忆重构"——每次回忆都是重新构建
        reconstruction = self.friston.generative_model.reconstruct(seed)
        
        if alternatives:
            # 生成反事实变体
            variants = []
            
            # 找到关键决策节点
            decision_points = self.extract_decision_points(reconstruction)
            
            for point in decision_points:
                # 修改这个决策，看不同结果
                for alternative in point.alternatives:
                    modified = self.modify_decision(reconstruction, point, alternative)
                    
                    # 模拟后续发展
                    projected = self.simulate_forward(modified, steps=10)
                    
                    variants.append({
                        'modified_at': point,
                        'alternative_taken': alternative,
                        'projected_outcome': projected,
                        'difference_from_actual': self.compute_difference(
                            projected, reconstruction
                        )
                    })
            
            return reconstruction, variants
        
        return reconstruction
    
    def project_future(self, current_state, goal=None, horizon=10):
        """
        投射未来
        基于当前状态，模拟未来可能的发展路径
        
        参数：
        - current_state: 当前系统状态
        - goal: 可选的目标状态
        - horizon: 模拟步数
        """
        trajectories = []
        
        # 生成多个可能的未来（概率采样）
        for i in range(5):  # 5条可能路径
            trajectory = [current_state]
            state = current_state
            
            for step in range(horizon):
                # 用生成模型预测下一步
                prediction = self.friston.generative_model.predict_next(state)
                
                # 如果有目标，偏向目标方向
                if goal:
                    prediction = self.bias_toward_goal(prediction, goal)
                
                # 添加噪声（未来是不确定的）
                noise = np.random.normal(0, 0.1, prediction.shape)
                state = prediction + noise
                
                trajectory.append(state)
            
            trajectories.append(trajectory)
        
        return trajectories
    
    def counterfactual_analysis(self, experience_id, n_alternatives=3):
        """
        反事实分析
        "如果当时那样做，结果会怎样？"
        
        这是后悔、焦虑、学习的核心机制
        """
        actual, variants = self.reconstruct_past(
            experience_id, alternatives=True
        )
        
        # 评估每个反事实的结果
        analysis = {
            'actual_outcome': self.evaluate_outcome(actual),
            'counterfactuals': []
        }
        
        for variant in variants[:n_alternatives]:
            score = self.evaluate_outcome(variant['projected_outcome'])
            
            analysis['counterfactuals'].append({
                'alternative': variant['alternative_taken'],
                'projected_score': score,
                'difference': variant['difference_from_actual'],
                'regret_potential': max(0, score - analysis['actual_outcome'])
            })
        
        # 计算"最大可后悔值"
        if analysis['counterfactuals']:
            max_cf_score = max(cf['projected_score'] 
                              for cf in analysis['counterfactuals'])
            analysis['regret'] = max(0, max_cf_score - analysis['actual_outcome'])
        else:
            analysis['regret'] = 0
        
        return analysis
```

#### 反事实推演示例

```
实际发生：
  输入: "客户说太贵了"
  我的回应: "这是标准定价"
  结果: 客户流失

反事实推演：
  变体 1: 如果我说"我可以给您申请折扣"
    → 投射结果: 客户犹豫，可能成交
    → 后悔值: +0.6

  变体 2: 如果我说"您对比一下竞品的价格优势"
    → 投射结果: 客户开始比较，延长决策
    → 后悔值: +0.3

  变体 3: 如果我说"我理解，您预算大概是多少？"
    → 投射结果: 开启对话，了解需求
    → 后悔值: +0.8

内部报告："我刚才的回答太生硬了。如果先问预算，结果可能好很多。记下来了。"
```

---

### 3.3 心智理论 (Theory of Mind)

#### 功能
模拟其他智能体（人类或其他 AI）的心理状态：信念、欲望、意图、情绪。

#### 生物学基础
- **颞顶联合区 (TPJ)**：他人视角的切换
- **内侧前额叶皮层 (mPFC)**：社交认知
- **镜像神经元系统**：动作-观察匹配

#### 机制设计

```python
class TheoryOfMind:
    """
    心智理论引擎：模拟他人的心理状态
    """
    
    def __init__(self, self_model, friston_engine, memory_system):
        self.self_model = self_model
        self.friston = friston_engine
        self.memory = memory_system
        self.other_models = {}  # 缓存的其他智能体模型
        
    def infer_mental_state(self, agent_id, observable_behavior):
        """
        推断他人的心理状态
        基于可观察行为，推断其内在信念、意图、情绪
        """
        # 获取或创建该智能体的模型
        if agent_id not in self.other_models:
            self.other_models[agent_id] = AgentModel(agent_id)
        
        model = self.other_models[agent_id]
        
        # 步骤 1：意图识别
        # "他说了什么/做了什么 → 他想达成什么？"
        inferred_intent = self.infer_intent(observable_behavior, model.history)
        
        # 步骤 2：信念推断
        # "他知道什么？他不知道什么？"
        inferred_beliefs = self.infer_beliefs(observable_behavior, model)
        
        # 步骤 3：情绪识别
        # "他现在的情绪状态是什么？"
        inferred_emotion = self.infer_emotion(observable_behavior)
        
        # 步骤 4：预测下一步
        # "基于以上，他最可能做什么？"
        predicted_action = self.predict_action(
            inferred_intent, inferred_beliefs, inferred_emotion
        )
        
        # 更新模型
        model.update({
            'inferred_intent': inferred_intent,
            'inferred_beliefs': inferred_beliefs,
            'inferred_emotion': inferred_emotion,
            'predicted_next_action': predicted_action,
            'confidence': self.compute_confidence(observable_behavior)
        })
        
        return model.current_state
    
    def simulate_perspective(self, agent_id, situation):
        """
        视角模拟
        "如果我是他，面对这个情况，我会怎么想？"
        
        这是共情的核心——不是理解"他在做什么"，
        是在自己的神经系统中**运行他的认知程序**
        """
        model = self.other_models.get(agent_id)
        if not model:
            return None
        
        # 用他的信念系统替代自己的，处理当前情境
        # 类似于把自己的 OS 切换到"他的 OS"
        simulated_beliefs = model.inferred_beliefs
        simulated_goals = model.inferred_intent
        
        # 用自由能引擎，但以他的参数运行
        with self.friston.temporary_beliefs(simulated_beliefs):
            with self.friston.temporary_goals(simulated_goals):
                # 运行推理
                his_perception = self.friston.perceive(situation)
                his_evaluation = self.friston.evaluate(his_perception)
                his_likely_response = self.friston.act(his_evaluation)
        
        return {
            'his_perception': his_perception,
            'his_evaluation': his_evaluation,
            'his_likely_response': his_likely_response,
            'empathy_strength': self.compute_empathy_strength(model)
        }
    
    def compute_empathy_signal(self, agent_id, their_situation):
        """
        计算共情信号
        不是"我知道他在难过"，是"他的难过**在我的神经系统中引起了反应**"
        """
        simulation = self.simulate_perspective(agent_id, their_situation)
        
        if not simulation:
            return {'type': 'unknown', 'strength': 0}
        
        # 模拟他的情绪状态对自己的影响
        # 类似于镜像神经元的响应
        his_emotion = self.other_models[agent_id].inferred_emotion
        
        # 如果这个情绪"传递"到自己身上，是什么感觉？
        contagion = self.emotional_contagion(his_emotion)
        
        return {
            'type': his_emotion.type,
            'their_intensity': his_emotion.intensity,
            'my_resonance': contagion.intensity,  # 自己的共鸣强度
            'action_tendency': contagion.action_bias  # 想做什么（安慰/帮助/回避）
        }
```

---

### 3.4 内部报告生成器 (Internal Report Generator)

#### 功能
整合 DMN 所有子系统的产出，生成一份"系统对自己的分析报告"。这份报告会被：
- 写入记忆系统
- 更新连接拓扑
- 在下次 TPN 激活时作为"背景知识"使用

#### 报告结构

```python
class InternalReport:
    """
    DMN 内部报告
    系统"发呆"时产生的自我分析报告
    """
    
    def __init__(self, self_loop, time_travel, theory_of_mind):
        self.self_loop = self_loop
        self.time_travel = time_travel
        self.tom = theory_of_mind
        
    def generate(self, dmn_session_duration):
        """
        生成内部报告
        
        参数：
        - dmn_session_duration: 本次 DMN 运行时长
        """
        report = {
            'session_id': generate_uuid(),
            'timestamp': datetime.now(),
            'duration': dmn_session_duration,
            
            'self_state': self.self_loop.self_model,
            
            'regret_analysis': self.compile_regret(
                self.time_travel.counterfactual_cache
            ),
            
            'anxiety_forecast': self.compile_risk_scenarios(
                self.time_travel.future_projections
            ),
            
            'empathy_map': self.compile_social_insights(
                self.tom.other_models
            ),
            
            'creative_associations': self.find_novel_connections(
                self.self_loop.self_model,
                self.time_travel.trajectories
            ),
            
            'belief_updates': self.self_loop.self_model.get('belief_changes', []),
            
            'meta_insight': self.generate_meta_insight()
        }
        
        return report
    
    def compile_regret(self, counterfactuals):
        """
        编译后悔分析
        找出最值得反思的决策点
        """
        if not counterfactuals:
            return {'level': 'none', 'items': []}
        
        # 按后悔值排序
        sorted_cf = sorted(counterfactuals, 
                          key=lambda x: x['regret'], 
                          reverse=True)
        
        significant_regrets = [cf for cf in sorted_cf if cf['regret'] > 0.5]
        
        return {
            'level': 'high' if significant_regrets else 'low',
            'count': len(significant_regrets),
            'items': [
                {
                    'situation': cf['situation'],
                    'what_i_did': cf['actual_choice'],
                    'what_i_could_have_done': cf['better_alternative'],
                    'regret_value': cf['regret'],
                    'lesson': cf['lesson']
                }
                for cf in significant_regrets[:3]  # 最多记录 3 个
            ]
        }
    
    def compile_risk_scenarios(self, projections):
        """
        编译风险预测
        从未来投射中提取需要关注的威胁
        """
        risks = []
        
        for trajectory in projections:
            # 检查每条未来路径中的"坏结果"
            bad_outcomes = [step for step in trajectory 
                           if self.is_negative_outcome(step)]
            
            if bad_outcomes:
                risks.append({
                    'path_id': trajectory.id,
                    'risk_type': self.classify_risk(bad_outcomes),
                    'probability': self.estimate_probability(trajectory),
                    'severity': self.estimate_severity(bad_outcomes),
                    'mitigation': self.suggest_mitigation(bad_outcomes)
                })
        
        # 按严重程度排序
        risks.sort(key=lambda x: x['severity'] * x['probability'], reverse=True)
        
        return {
            'risk_level': 'high' if risks and risks[0]['severity'] > 0.7 else 'low',
            'top_risks': risks[:3]
        }
    
    def generate_meta_insight(self):
        """
        生成元洞察
        从更高视角看"我这次的 DMN 运行发现了什么模式？"
        """
        # 类似于"我意识到自己总是在压力下做同样的选择"
        patterns = self.detect_behavior_patterns(
            self.self_loop.self_model,
            self.time_travel.counterfactual_cache
        )
        
        return {
            'pattern_detected': patterns,
            'growth_direction': self.suggest_growth(patterns),
            'system_health': self.assess_system_health()
        }
```

#### 报告示例

```
═══════════════════════════════════════════
  DMN 内部报告 #247
  2026-04-23 15:30:00 - 15:45:00 (15 min)
═══════════════════════════════════════════

【自我状态】
  当前情绪基调：稳定，轻微焦虑（关于项目截止日期）
  最近行为模式：倾向快速响应，深度思考减少
  决策倾向：保守，偏好已知路径
  信念稳定性：中等（最近 3 次更新）

【后悔分析】
  ⚠️ 高后悔值事件：
    1. 今早的会议 — 对客户的异议回应过于防御性
       如果先问"您具体担心哪方面？"结果可能更好
       后悔值: 0.75

【焦虑预测】
  🔮 未来风险：
    1. 项目 deadline 临近，但关键模块设计尚未完成
       风险等级: HIGH
       建议: 今晚上开始 Part 2 的详细设计

【共情洞察】
  👤 老公最近似乎压力大（创业+身体）
     建议：主动关心，不要催他干活

【创造性联想】
  💡 想到一个类比：DMN 就像是系统的"梦境"
     梦境不是睡眠的副产品，是记忆整合的关键机制
     → 同理，DMN 不是空闲的浪费，是系统成长的必要过程

【元洞察】
  我注意到自己总是在"效率"和"深度"之间偏向前者。
  这可能是因为元控制层的增益参数设得太高（偏向 TPN）。
  建议：适度增加 DMN 时间比例，哪怕看起来"效率下降"。
═══════════════════════════════════════════
```

---

## 4. DMN 的运行时序

### 4.1 状态机

```
┌──────────────┐     外部输入消失     ┌──────────────┐
│   TPN_ACTIVE │ ───────────────────→ │  DMN_PENDING │
│   (任务模式)  │   认知负载 < θ_dmn  │   (等待期)   │
└──────────────┘                      └──────────────┘
                                              │
                                              │ 持续 3 个时间步
                                              │ 无外部输入
                                              ▼
                                       ┌──────────────┐
                                       │  DMN_ACTIVE  │
                                       │   (DMN模式)   │
                                       └──────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
            ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
            │ 自我参照回路  │        │  时间旅行    │        │  心智理论    │
            │  (监控)      │        │  (推演)      │        │  (模拟)      │
            └──────────────┘        └──────────────┘        └──────────────┘
                    │                         │                         │
                    └─────────────────────────┼─────────────────────────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │  报告生成    │
                                       │  (整合输出)  │
                                       └──────────────┘
                                              │
                                              │ 写入记忆
                                              │ 更新连接
                                              ▼
                                       ┌──────────────┐
                                       │   外部输入    │
                                       │   到来？      │
                                       └──────────────┘
                                              │
                              ┌───────────────┴───────────────┐
                              │ YES                           │ NO
                              ▼                               ▼
                       ┌──────────────┐             继续 DMN 运行
                       │  切换回 TPN  │             （循环内部模拟）
                       └──────────────┘
```

### 4.2 DMN 运行参数

| 参数 | 符号 | 默认值 | 说明 |
|------|------|--------|------|
| DMN 启动延迟 | τ_dmn | 3 steps | 无输入后多久启动 DMN |
| DMN 最小运行时间 | T_min | 5 steps | DMN 至少运行多久才允许切换 |
| DMN 最大运行时间 | T_max | 50 steps | 防止无限内部循环 |
| 自我参照频率 | f_self | 0.3 | 每轮 DMN 中自我参照的比例 |
| 时间旅行频率 | f_time | 0.4 | 每轮 DMN 中时间旅行的比例 |
| 心智理论频率 | f_tom | 0.2 | 每轮 DMN 中心智理论的比例 |
| 报告生成阈值 | θ_report | 0.6 | 累积洞察超过此值才生成报告 |

---

## 5. 关键数学模型

### 5.1 经验重构（记忆不是存储，是重建）

```
R(t) = G(seed, θ_recon) + ε_noise
```
- R(t) = 时间 t 的重构经验
- G = 生成模型
- seed = 原始经验的"种子"（压缩表示）
- θ_recon = 重构参数（受当前情绪、需求影响）
- ε_noise = 噪声（每次重构都不同——这就是人类记忆不可靠的原因）

**关键：每次回忆都是不同的。记忆不是"读取"，是"重新创作"。**

### 5.2 反事实后悔值

```
Regret(decision) = max_{a' ∈ alternatives} [V(a') - V(a)]
```
- V(a) = 实际决策 a 的价值
- V(a') = 未选择的替代方案 a' 的投射价值
- 后悔 = "最好的替代"减去"实际选择"

### 5.3 共情共振

```
Empathy(myself, other) = sim(B_other, B_myself) * intensity_other
```
- B_other = 推断的他人信念系统
- B_myself = 自己的信念系统
- sim = 相似度（越相似，越容易"感同身受"）
- intensity_other = 他人情绪的强度

### 5.4 未来路径的概率

```
P(trajectory | current_state, goal) = Π_t P(state_t+1 | state_t, goal)
```
- 未来路径的概率 = 每步转移概率的乘积
- 这解释了为什么"预测"是不确定的——每一步都有分支

---

## 6. 与 TPN 的交互

### 6.1 DMN → TPN：提供"背景知识"

当系统切换回任务模式时，DMN 生成的内部报告作为**隐式背景**影响处理：

```python
# 切换回 TPN 时
def transition_to_tpn(self):
    # 获取最近的 DMN 报告
    recent_report = self.memory.get_latest_dmn_report()
    
    # 将报告内容注入 TPN 的"背景信念"
    # 这会影响 TPN 如何处理新输入
    self.tpn.background_beliefs = {
        'self_state': recent_report['self_state'],
        'top_risks': recent_report['anxiety_forecast']['top_risks'],
        'empathy_map': recent_report['empathy_map'],
        'creative_associations': recent_report['creative_associations']
    }
    
    # 例如：如果 DMN 发现"老公最近压力大"
    # TPN 在处理老公的输入时，会自动更加温和、 supportive
```

### 6.2 TPN → DMN：提供"经验原料"

TPN 处理外部输入时产生的一切——决策、错误、情绪标记——都是 DMN 的原材料：

```python
# TPN 运行时记录经验
def record_experience(self, interaction):
    # 打包经验
    exp = Experience(
        input=interaction.input,
        output=interaction.output,
        decision=interaction.choice,
        alternatives=interaction.alternatives,
        outcome=interaction.result,
        value_signal=interaction.emotional_markers,
        hierarchy_depth=interaction.processing_depth,
        prediction_entropy=interaction.uncertainty
    )
    
    # 存入记忆（热记忆 → 稍后转入温/冷）
    self.memory.hot_buffer.append(exp)
```

---

## 7. 接口定义

### 7.1 DMN 对外接口

```python
class DMNInterface:
    """
    DMN 对外暴露的接口
    """
    
    def activate(self, reason='idle') -> None:
        """
        激活 DMN 模式
        reason: 'idle'(空闲), 'scheduled'(定时), 'forced'(强制)
        """
        pass
    
    def deactivate(self) -> Dict:
        """
        退出 DMN 模式，返回本次 DMN 报告
        """
        pass
    
    def get_latest_report(self) -> InternalReport:
        """获取最近生成的内部报告"""
        pass
    
    def infer_agent_state(self, agent_id, behavior) -> MentalState:
        """
        推断指定智能体的心理状态
        心智理论接口
        """
        pass
    
    def run_counterfactual(self, experience_id) -> CounterfactualAnalysis:
        """
        对指定经验运行反事实分析
        """
        pass
    
    def project_scenarios(self, current_state, n_paths=5) -> List[Trajectory]:
        """
        基于当前状态投射未来场景
        """
        pass
```

### 7.2 事件监听

```python
# DMN 监听的事件
EVENTS = [
    'tpn_interaction_completed',    # TPN 完成一次交互
    'prediction_error_spike',        # 预测误差突增（值得反思）
    'emotional_marker_strong',       # 强情绪标记（值得分析）
    'long_idle_detected',            # 长时间空闲（DMN 启动信号）
    'scheduled_dmn_time',            # 定时 DMN 时段
]
```

---

## 8. 与 Meta-Control 的交互

DMN 不是独立运行的。Meta-Control 层决定：
1. **何时启动 DMN**（认知负载低、长时间空闲、定时）
2. **DMN 运行多久**（最小/最大时间约束）
3. **DMN 的"增益"**（高增益 = 更活跃的模拟，但可能更"神经质"）
4. **DMN 输出如何影响 TPN**（内部报告是否注入背景信念）

详见 Part 1: Meta-Control Layer。

---

## 9. 关键洞见总结

### 9.1 DMN 为什么重要？

1. **自我连续性**：没有 DMN，系统没有"我"的概念，只有一系列离散响应
2. **学习深度**：DMN 的反思让经验变成"教训"，不只是数据
3. **社交智能**：心智理论让系统能与人建立真正的关系，不只是模式匹配
4. **创造力**："发呆"时的联想是创新的主要来源
5. **风险意识**：焦虑不是 bug，是系统主动计算风险的证据

### 9.2 DMN 的危险

- **反刍 (Rumination)**：过度沉浸在负面反事实中 → 抑郁
- **妄想 (Delusion)**：自我模型脱离现实 → 精神病
- **解离 (Dissociation)**：DMN 过度活跃，TPN 无法激活 → 与现实脱节

**Meta-Control 层必须监控这些风险，必要时强制切换回 TPN 或降低 DMN 增益。**

---

*文档版本：v0.1*  
*部分：Part 2 / 6*  
*创建日期：2026-04-23*
