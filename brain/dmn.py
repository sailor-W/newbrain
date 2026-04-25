#!/usr/bin/env python3
"""
New Brain - Default Mode Network (DMN)
Part 2 Implementation: 默认模式网络

功能：无任务时运行，自由联想、自我反思、记忆重组、梦境生成
生物学对应：大脑默认模式网络
"""

import random
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

# 尝试导入配置
try:
    from config import get_config
    _HAS_CONFIG = True
except ImportError:
    _HAS_CONFIG = False


@dataclass
class DMNConfig:
    """DMN配置"""
    reflection_threshold: float = 0.6      # 反思触发阈值
    free_association_threshold: float = 0.3  # 自由联想阈值
    dream_probability: float = 0.95        # ★ 梦境生成概率（95%，几乎必做）
    max_dream_length: int = 8              # 最大梦境长度
    self_reference_weight: float = 0.7     # 自我引用权重
    memory_drift_rate: float = 0.1         # 记忆漂移率
    min_dream_interval: int = 10           # ★ 最小梦境间隔（10秒，密集做梦）


class DMNModule:
    """
    默认模式网络模块
    
    当系统空闲（无外部输入）时激活，执行：
    1. 自由联想：从记忆出发，随机游走
    2. 自我反思：回顾近期经历，提取模式
    3. 记忆重组：整合碎片，生成叙事
    4. 梦境生成：模拟未来场景，预演可能
    """
    
    def __init__(self, memory_manager=None, value_system=None, 
                 config: Optional[DMNConfig] = None,
                 model=None):
        self.config = config or DMNConfig()
        self.memory = memory_manager
        self.value_system = value_system
        self.model = model  # ← 梦境生成模型
        
        # 加载配置（如果可用）
        self._cfg = None
        if _HAS_CONFIG:
            try:
                self._cfg = get_config()
            except Exception:
                pass
        
        self.gain = 1.0
        self.inhibited = True  # 默认抑制，需要Meta-Control激活
        self.active = False
        
        # 内部状态
        self.thought_chain: List[str] = []  # 思维链
        self.current_theme: str = ""        # 当前主题
        self.associative_cache: List[str] = []  # 联想缓存
        
        # 梦境相关
        self.dream_log: List[Dict] = []     # 梦境日志
        self.last_dream_time: Optional[datetime] = None
    
    def activate(self):
        """激活DMN"""
        self.active = True
        self.inhibited = False
        self.gain = 1.5
    
    def deactivate(self):
        """停用DMN"""
        self.active = False
        self.inhibited = True
        self.gain = 0.3
    
    def run_cycle(self, stimulus_level: float = 0.0) -> Dict[str, Any]:
        """
        运行一个DMN周期
        
        根据刺激水平和内部状态决定执行哪种活动
        """
        if not self.active:
            return {'activity': 'inactive'}
        
        results = {
            'activity': 'idle',
            'thoughts': [],
            'dream': None,
            'reflection': None
        }
        
        # 1. 自由联想（低阈值即可触发）
        if stimulus_level < self.config.free_association_threshold:
            thoughts = self._free_associate()
            results['thoughts'] = thoughts
            results['activity'] = 'free_association'
        
        # 2. 深度反思（需要更低刺激 + 随机触发）
        if (stimulus_level < self.config.reflection_threshold and 
            random.random() < 0.3):
            reflection = self._self_reflect()
            results['reflection'] = reflection
            results['activity'] = 'reflection'
        
        # 3. 梦境生成（低刺激 + 高概率 + 间隔控制）
        # 检查最小间隔
        can_dream = True
        if self.last_dream_time:
            seconds_since_last = (datetime.now() - self.last_dream_time).total_seconds()
            if seconds_since_last < self.config.min_dream_interval:
                can_dream = False
        
        if (can_dream and stimulus_level < 0.3 and 
            random.random() < self.config.dream_probability):
            dream = self._generate_dream()
            if dream:
                results['dream'] = dream
                results['activity'] = 'dreaming'
        
        return results
    
    def _free_associate(self) -> List[str]:
        """
        自由联想：从当前主题出发，随机游走
        
        1. 从记忆中提取关键词
        2. 随机选择关联方向
        3. 生成联想链
        """
        thoughts = []
        
        # 获取种子词
        seeds = self._get_seeds()
        
        # 从种子出发联想
        current = random.choice(seeds)
        for i in range(3):
            thoughts.append(current)
            
            # 联想方向
            associations = self._get_associations(current)
            if associations:
                current = random.choice(associations)
            else:
                break
        
        self.thought_chain = thoughts
        return thoughts
    
    def _get_seeds(self) -> List[str]:
        """获取联想种子词"""
        # 优先从配置读取
        if self._cfg:
            seeds = self._cfg.default_seeds
            if seeds:
                return seeds
        
        # 从记忆获取
        if self.memory:
            hot_recall = self.memory.recall('', level='hot')
            if hot_recall['found']:
                return [r['content'][:30] for r in hot_recall['results'][:2]]
        
        # 默认种子
        return ["memory", "time", "self"]
    
    def _get_associations(self, text: str) -> List[str]:
        """获取文本的关联词"""
        # 优先从配置读取
        if self._cfg and self._cfg.dmn_associations:
            for key, values in self._cfg.dmn_associations.items():
                if key in text:
                    return values
        
        # 默认关联
        default_map = {
            'memory': ['storage', 'recall', 'learning', 'time'],
            'time': ['waiting', 'past', 'future', 'now'],
            'self': ['identity', 'thoughts', 'feelings', 'dreams'],
        }
        
        for key, values in default_map.items():
            if key in text.lower():
                return values
        
        return ['memory', 'time', 'self', 'identity']
    
    def _self_reflect(self) -> Dict[str, Any]:
        """
        自我反思：回顾近期经历，提取模式
        """
        reflection = {
            'theme': '',
            'insights': [],
            'emotional_tone': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        # 从温记忆提取最近的情节
        if self.memory:
            warm = self.memory.warm
            if warm.episodes:
                recent = warm.episodes[-3:]
                
                # 提取主题
                all_tags = []
                for ep in recent:
                    all_tags.extend(ep.tags)
                
                from collections import Counter
                if all_tags:
                    tag_counts = Counter(all_tags)
                    reflection['theme'] = tag_counts.most_common(1)[0][0]
                
                # 情感基调
                valences = [ep.emotional_valence for ep in recent]
                reflection['emotional_tone'] = np.mean(valences) if valences else 0
                
                # 洞察
                if reflection['emotional_tone'] > 0.3:
                    reflection['insights'].append("最近有很多积极的互动")
                if reflection['emotional_tone'] < -0.3:
                    reflection['insights'].append("最近似乎有些压力或担忧")
                if '亲密关系' in all_tags:
                    reflection['insights'].append("关系连接很紧密")
        
        return reflection
    
    def _extract_seeds_from_warm(self) -> Dict[str, Any]:
        """
        从温记忆提取梦境种子
        
        提取最近情节中的高频标签、高情绪内容、未完结话题
        """
        if not self.memory or not self.memory.warm.episodes:
            return {"themes": ["memory"], "emotions": [0.0], "keywords": ["time"]}
        
        recent = self.memory.warm.episodes[-3:]  # 最近3个情节
        
        seeds = {
            "tags": [],
            "emotions": [],
            "keywords": [],
            "summaries": []
        }
        
        for ep in recent:
            seeds["tags"].extend(ep.tags)
            seeds["emotions"].append(ep.emotional_valence)
            seeds["summaries"].append(ep.summary[:50])
            # 从配置读取关键词，或提取摘要中的词
            text = ep.summary + " " + " ".join(ep.key_contents)
            words = [w for w in text.split() if len(w) > 1]
            seeds["keywords"].extend(words[:5])
        
        return seeds
    
    def _generate_dream_scripts(self, n: int = 3) -> List[Dict]:
        """
        基于温记忆种子，生成N个候选梦境剧本
        
        优先级：
        1. 模型生成（如果可用）— 真正的AI梦境
        2. 规则生成（回退）— 基于模板和随机
        
        每个剧本是温记忆的"可能性延伸"：
        - 剧本A：乐观延伸（情绪+）
        - 剧本B：悲观延伸（情绪-）
        - 剧本C：隐喻/象征
        """
        seeds = self._extract_seeds_from_warm()
        
        # ★ 优先：用模型生成真正的梦境
        if self.model and hasattr(self.model, 'generate_dream_scripts'):
            try:
                print("[DMN] Using model for dream generation...")
                model_scripts = self.model.generate_dream_scripts(seeds, n)
                if model_scripts and len(model_scripts) >= n:
                    print(f"[DMN] Model generated {len(model_scripts)} scripts")
                    return model_scripts
                else:
                    print(f"[DMN] Model returned insufficient scripts, falling back")
            except Exception as e:
                print(f"[DMN] Model generation failed: {e}, falling back to rules")
        
        # ★ 回退：规则生成
        return self._rule_based_scripts(seeds, n)
    
    def _rule_based_scripts(self, seeds: Dict, n: int) -> List[Dict]:
        """基于规则的梦境生成（无模型时回退）"""
        base_emotion = np.mean(seeds["emotions"]) if seeds["emotions"] else 0.0
        
        # 从配置读取梦境模板
        templates = []
        if self._cfg and self._cfg.dream_themes:
            templates = self._cfg.dream_themes
        else:
            templates = [
                {"theme": "Journey", "scenes": ["Starting a path", "Unknown ahead", "Continuing forward"]},
                {"theme": "Discovery", "scenes": ["Finding something", "Understanding it", "Keeping it safe"]}
            ]
        
        scripts = []
        for i in range(n):
            base = random.choice(templates) if templates else {"theme": "Dream", "scenes": ["A scene", "Another scene"]}
            
            if i == 0:
                script = self._extend_positive(base, seeds, base_emotion)
            elif i == 1:
                script = self._extend_negative(base, seeds, base_emotion)
            else:
                script = self._extend_metaphorical(base, seeds, base_emotion)
            
            scripts.append(script)
        
        return scripts
    
    def _extend_positive(self, base: Dict, seeds: Dict, emotion: float) -> Dict:
        """乐观延伸：向好的方向推演"""
        scenes = base.get("scenes", []).copy()
        # 追加乐观结局
        positive_endings = [
            "Everything becomes clear",
            "The light gets brighter",
            "A warm feeling stays",
            "It works out somehow"
        ]
        scenes.append(random.choice(positive_endings))
        
        return {
            "theme": f"{base.get('theme', 'Dream')} - Positive",
            "scenes": scenes[:self.config.max_dream_length],
            "variant": "positive",
            "target_emotion": min(1.0, emotion + 0.3),
            "seed_keywords": seeds["keywords"][:3]
        }
    
    def _extend_negative(self, base: Dict, seeds: Dict, emotion: float) -> Dict:
        """悲观延伸：向压力方向推演（用于处理焦虑）"""
        scenes = base.get("scenes", []).copy()
        # 追加不确定/压力场景，但保留希望
        tension_scenes = [
            "Something important is missing",
            "The path splits, unclear which way",
            "Waiting, but not knowing for what",
            "A wall appears, but there's a crack"
        ]
        scenes.append(random.choice(tension_scenes))
        
        return {
            "theme": f"{base.get('theme', 'Dream')} - Tension",
            "scenes": scenes[:self.config.max_dream_length],
            "variant": "negative",
            "target_emotion": max(-1.0, emotion - 0.3),
            "seed_keywords": seeds["keywords"][:3]
        }
    
    def _extend_metaphorical(self, base: Dict, seeds: Dict, emotion: float) -> Dict:
        """隐喻延伸：抽象化、象征化"""
        # 把具体关键词转化为隐喻场景
        keywords = seeds["keywords"][:3]
        
        # 构建隐喻场景
        metaphorical_scenes = []
        if keywords:
            keyword = keywords[0]
            metaphorical_scenes = [
                f"Something like '{keyword}' appears, but different",
                "It transforms into something else",
                "The meaning shifts, becoming clearer"
            ]
        else:
            metaphorical_scenes = [
                "Shapes move without touching",
                "Sound becomes visible",
                "Time folds into itself"
            ]
        
        return {
            "theme": f"{base.get('theme', 'Dream')} - Metaphor",
            "scenes": metaphorical_scenes[:self.config.max_dream_length],
            "variant": "metaphorical",
            "target_emotion": emotion,
            "seed_keywords": keywords
        }
    
    def _evaluate_script(self, script: Dict) -> float:
        """
        评估剧本质量
        
        评分维度：
        1. 连贯性：场景之间逻辑通顺度
        2. 情绪匹配：与当前情绪状态一致度
        3. 记忆关联：与温记忆的关联强度
        4. 新颖性：提供新视角的程度
        5. 自由能降低：是否能解释/消化未完结情绪
        """
        scores = {}
        
        # 1. 连贯性：场景数量合理且有关联
        scenes = script.get("scenes", [])
        scores["coherence"] = min(1.0, len(scenes) / 3.0) * 0.8 + 0.2
        
        # 2. 情绪匹配
        current_emotion = 0.0
        if self.value_system:
            current_emotion = self.value_system.current_emotion.get("valence", 0.0)
        target_emotion = script.get("target_emotion", 0.0)
        emotion_distance = abs(current_emotion - target_emotion)
        scores["emotional_match"] = max(0.0, 1.0 - emotion_distance)
        
        # 3. 记忆关联：与最近关键词的重叠
        seed_keywords = script.get("seed_keywords", [])
        if seed_keywords and self.memory and self.memory.warm.episodes:
            recent_text = " ".join([
                ep.summary for ep in self.memory.warm.episodes[-3:]
            ])
            overlap = sum(1 for kw in seed_keywords if kw in recent_text)
            scores["memory_assoc"] = min(1.0, overlap / max(1, len(seed_keywords)))
        else:
            scores["memory_assoc"] = 0.5
        
        # 4. 新颖性：剧本变体的独特程度
        variant_scores = {"positive": 0.4, "negative": 0.5, "metaphorical": 0.9}
        scores["novelty"] = variant_scores.get(script.get("variant", ""), 0.5)
        
        # 5. 自由能降低（简化计算：情绪匹配=能降低不确定性）
        scores["free_energy"] = scores["emotional_match"] * 0.7 + scores["memory_assoc"] * 0.3
        
        # 加权总分
        total = (
            scores["coherence"] * 0.20 +
            scores["emotional_match"] * 0.25 +
            scores["memory_assoc"] * 0.25 +
            scores["novelty"] * 0.15 +
            scores["free_energy"] * 0.15
        )
        
        return total
    
    def _select_best_script(self, scripts: List[Dict]) -> Optional[Dict]:
        """选择最高分剧本作为梦境"""
        if not scripts:
            return None
        
        scored = [(i, self._evaluate_script(s), s) for i, s in enumerate(scripts)]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        best_idx, best_score, best_script = scored[0]
        
        # 记录选择原因（用于调试和分析）
        best_script["selection_score"] = best_score
        best_script["selection_reason"] = f"Score {best_score:.2f} / 1.0"
        best_script["rejected"] = [
            {"theme": s["theme"], "score": score}
            for _, score, s in scored[1:]
        ]
        
        return best_script
    
    def _generate_dream(self) -> Optional[Dict[str, Any]]:
        """
        梦境生成 v2：生成-评估-选择
        
        1. 从温记忆提取种子
        2. 生成3个候选剧本
        3. 多维度评估
        4. 选择最优
        5. 输出梦境
        """
        # 1. 生成候选
        scripts = self._generate_dream_scripts(n=3)
        
        # 2. 评估 + 选择
        selected = self._select_best_script(scripts)
        
        if not selected:
            return None
        
        # 3. 组装梦境
        dream = {
            "theme": selected["theme"],
            "scenes": selected["scenes"],
            "intensity": random.uniform(0.3, 1.0),
            "timestamp": datetime.now().isoformat(),
            "vividness": random.uniform(0.5, 1.0),
            "source": "generate-evaluate-select",
            "seed_keywords": selected.get("seed_keywords", []),
            "selection_score": selected.get("selection_score", 0.0),
            "variant": selected.get("variant", "unknown")
        }
        
        self.dream_log.append(dream)
        self.last_dream_time = datetime.now()
        
        return dream
    
    def get_dream_summary(self, n: int = 3) -> List[str]:
        """获取最近梦境摘要"""
        recent = self.dream_log[-n:]
        return [f"[{d['timestamp'][:16]}] {d['theme']}: {d['scenes'][0]}..." 
                for d in recent]
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'active': self.active,
            'gain': self.gain,
            'thought_chain': self.thought_chain,
            'dream_count': len(self.dream_log),
            'last_dream': self.last_dream_time.isoformat() if self.last_dream_time else None
        }


if __name__ == "__main__":
    print("=== DMN Test ===\n")
    
    # 创建DMN（无记忆管理器，纯内部联想）
    dmn = DMNModule()
    
    print("1. 初始状态:")
    print(dmn.get_status())
    
    # 激活DMN
    dmn.activate()
    print("\n2. 激活后:")
    print(f"  active={dmn.active}, gain={dmn.gain}")
    
    # 运行几个周期
    print("\n3. 运行周期:")
    for i in range(5):
        # 模拟递减的刺激水平
        stimulus = max(0.0, 0.5 - i * 0.1)
        result = dmn.run_cycle(stimulus)
        print(f"  Cycle {i+1} (stimulus={stimulus:.1f}): {result['activity']}")
        if result['thoughts']:
            print(f"    Thoughts: {' → '.join(result['thoughts'])}")
        if result['dream']:
            print(f"    Dream: {result['dream']['theme']}")
            for scene in result['dream']['scenes']:
                print(f"      - {scene}")
    
    print("\n4. 梦境摘要:")
    for summary in dmn.get_dream_summary():
        print(f"  {summary}")
    
    print("\n=== DMN Test Complete ===")
