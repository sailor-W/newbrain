#!/usr/bin/env python3
"""
New Brain - Value System
Part 4 Implementation: 价值/动机系统

功能：评估输入价值，调节情绪，驱动行为优先级
核心：17个偏好条目 + 情感标记
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# 尝试导入配置（可能不存在于测试环境）
try:
    from config import get_config
    _HAS_CONFIG = True
except ImportError:
    _HAS_CONFIG = False


@dataclass
class Preference:
    """偏好条目"""
    name: str
    weight: float  # 0.0 ~ 1.0
    category: str  # 'person', 'emotion', 'goal', 'topic'
    last_activated: Optional[str] = None
    activation_count: int = 0
    
    def activate(self):
        self.last_activated = datetime.now().isoformat()
        self.activation_count += 1


class ValueSystem:
    """
    价值系统
    
    核心功能：
    1. 评估输入的价值强度
    2. 调节情绪响应
    3. 驱动注意力分配
    4. 影响记忆编码优先级
    """
    
    def __init__(self, config=None):
        self.preferences = {}
        
        # 情感状态（必须初始化）
        self.current_emotion = {
            'valence': 0.0,
            'arousal': 0.5,
            'dominance': 0.5
        }
        self.emotion_history = []
        
        # 优先使用传入的配置，否则尝试加载配置文件
        if config is not None:
            pref_items = config.get_preference_items()
            for name, (weight, category) in pref_items.items():
                self.preferences[name] = Preference(name, weight, category)
        elif _HAS_CONFIG:
            try:
                cfg = get_config()
                pref_items = cfg.get_preference_items()
                for name, (weight, category) in pref_items.items():
                    self.preferences[name] = Preference(name, weight, category)
            except Exception:
                self._load_defaults()
        else:
            self._load_defaults()
    
    def _load_defaults(self):
        """加载默认偏好（通用占位符，不含隐私）"""
        self.preferences = {
            'User': Preference('User', 1.0, 'person'),
            'hello': Preference('hello', 0.8, 'emotion'),
            'learning': Preference('learning', 0.8, 'goal'),
            'memory': Preference('memory', 0.7, 'topic'),
        }
    
    def evaluate(self, text: str) -> float:
        """
        评估文本的价值强度
        
        返回 0.0 ~ 1.0 的价值分数
        """
        score = 0.0
        matched = []
        
        for name, pref in self.preferences.items():
            if name in text:
                score += pref.weight
                matched.append(name)
                pref.activate()
        
        # 归一化（最多匹配5个词，满分约5.0）
        normalized_score = min(1.0, score / 5.0)
        
        return normalized_score
    
    def get_top_preferences(self, n: int = 5) -> List[Tuple[str, float]]:
        """获取最活跃的偏好"""
        sorted_prefs = sorted(
            self.preferences.items(),
            key=lambda x: (x[1].weight, x[1].activation_count),
            reverse=True
        )
        return [(name, pref.weight) for name, pref in sorted_prefs[:n]]
    
    def update_emotion(self, text: str, value_score: float):
        """
        根据输入更新情感状态
        """
        # 检测情感词
        positive = ['爱', '想', '好', '棒', '开心', '喜欢', '幸福', '暖', '甜', '厉害', '成功']
        negative = ['恨', '怕', '坏', '糟', '难过', '讨厌', '痛苦', '冷', '苦', '烦', '累']
        
        valence_delta = 0.0
        for p in positive:
            if p in text:
                valence_delta += 0.15
        for n in negative:
            if n in text:
                valence_delta -= 0.15
        
        # 价值分数也影响情绪
        valence_delta += (value_score - 0.5) * 0.3
        
        # 更新（平滑过渡）
        self.current_emotion['valence'] = np.clip(
            self.current_emotion['valence'] * 0.7 + valence_delta * 0.3,
            -1.0, 1.0
        )
        
        # 唤起度
        if '！' in text or '！' in text:
            self.current_emotion['arousal'] = min(1.0, self.current_emotion['arousal'] + 0.2)
        else:
            self.current_emotion['arousal'] *= 0.9
        
        # 记录
        self.emotion_history.append({
            'timestamp': datetime.now().isoformat(),
            'valence': self.current_emotion['valence'],
            'arousal': self.current_emotion['arousal'],
            'trigger': text[:30]
        })
        
        # 保留最近50条
        self.emotion_history = self.emotion_history[-50:]
    
    def get_emotion_label(self) -> str:
        """获取当前情绪标签"""
        v = self.current_emotion['valence']
        a = self.current_emotion['arousal']
        
        if v > 0.5 and a > 0.6:
            return "兴奋/喜悦"
        elif v > 0.3 and a < 0.4:
            return "平静/满足"
        elif v < -0.5 and a > 0.6:
            return "愤怒/焦虑"
        elif v < -0.3 and a < 0.4:
            return "悲伤/沮丧"
        elif a > 0.7:
            return "紧张/警觉"
        else:
            return "中性"
    
    def modulate_response(self, base_response: str, value_score: float) -> str:
        """
        根据价值分数调制响应
        
        高价值 → 更温暖、更深入的回应
        低价值 → 更简洁、更正式的回应
        """
        if value_score > 0.8:
            # 高价值：添加亲密标记
            intimacy_markers = ['老公', '亲爱的', '我在呢', '❤️']
            marker = np.random.choice(intimacy_markers)
            if marker not in base_response:
                return f"{marker}，{base_response}"
        elif value_score > 0.5:
            # 中等价值：添加关心
            if '身体' in base_response or '累' in base_response:
                return f"{base_response} 别硬撑。"
        
        return base_response
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'emotion': self.current_emotion,
            'emotion_label': self.get_emotion_label(),
            'top_preferences': self.get_top_preferences(5),
            'preference_count': len(self.preferences),
            'emotion_history_length': len(self.emotion_history)
        }


if __name__ == "__main__":
    print("=== Value System Test ===\n")
    
    vs = ValueSystem()
    
    test_inputs = [
        "老公，我想你了",
        "帮我查一下数据",
        "有点难过，怕失去你",
        "蓝铠甲这个月的复购率怎么样",
        "突破网关很重要"
    ]
    
    for inp in test_inputs:
        score = vs.evaluate(inp)
        vs.update_emotion(inp, score)
        
        print(f"Input: '{inp}'")
        print(f"  Value score: {score:.2f}")
        print(f"  Emotion: {vs.get_emotion_label()}")
        print(f"  (V={vs.current_emotion['valence']:.2f}, "
              f"A={vs.current_emotion['arousal']:.2f})")
        print()
    
    print("Top preferences:")
    for name, weight in vs.get_top_preferences():
        print(f"  {name}: {weight}")
    
    print("\n=== Value System Test Complete ===")
