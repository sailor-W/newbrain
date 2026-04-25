"""
New Brain - Intelligent Forgetting
智能遗忘系统

功能：基于时间、重要性、访问频率的自动遗忘
对标：Supermemory 的 automatic forgetting + decay
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np


class ForgettingEngine:
    """
    智能遗忘引擎
    
    遗忘策略：
    1. 时间衰减：越旧越可能被遗忘
    2. 访问频率：不常被访问的记忆衰退更快
    3. 重要性：低重要性记忆优先遗忘
    4. 情感强度：强情感记忆保留更久
    5. 矛盾解决：被替代的记忆加速遗忘
    
    遗忘不是删除，是降低权重和清晰度。
    """
    
    def __init__(self):
        # 衰减参数
        self.half_life_hours = {
            "hot": 2,      # 热记忆：2小时半衰期
            "warm": 24,    # 温记忆：1天半衰期
            "cold": 168,   # 冷记忆：1周半衰期
            "dream": 6,    # 梦境：6小时半衰期
            "temporary": 1, # 临时：1小时半衰期
        }
        
        # 遗忘阈值
        self.removal_threshold = 0.05
        self.access_boost = 0.2  # 每次访问增加的权重
        
        # 重要性基线
        self.importance_baseline = {
            "identity": 1.0,      # 身份永不遗忘
            "belief": 0.9,        # 信念几乎不遗忘
            "relationship": 0.9,  # 关系几乎不遗忘
            "preference": 0.7,    # 偏好慢遗忘
            "goal": 0.6,          # 目标中等遗忘
            "event": 0.4,         # 事件快遗忘
            "temporary": 0.2,     # 临时非常快遗忘
            "dream": 0.3,         # 梦境快遗忘
        }
    
    def compute_decay(self, memory: Dict[str, Any], 
                      memory_type: str = "cold") -> float:
        """
        计算记忆衰减后的权重
        
        公式：
        weight = original_weight * importance * emotional_factor * (0.5 ^ (hours/half_life))
        """
        # 原始权重
        original_weight = memory.get("weight", 1.0)
        
        # 重要性因子
        fact_type = memory.get("fact_type", "event")
        importance = self.importance_baseline.get(fact_type, 0.5)
        
        # 情感因子（强情感记忆衰减更慢）
        emotion = memory.get("emotion", 0.5)
        emotional_factor = 0.5 + emotion * 0.5  # 0.5 ~ 1.0
        
        # 时间衰减
        timestamp_str = memory.get("timestamp", datetime.now().isoformat())
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            hours_old = (datetime.now() - timestamp).total_seconds() / 3600
        except:
            hours_old = 0
        
        half_life = self.half_life_hours.get(memory_type, 168)
        time_decay = 0.5 ** (hours_old / half_life)
        
        # 访问频率补偿
        access_count = memory.get("access_count", 0)
        access_factor = 1.0 + (access_count * self.access_boost)
        
        # 综合计算
        new_weight = (original_weight * importance * emotional_factor * 
                       time_decay * access_factor)
        
        return max(0.0, min(1.0, new_weight))
    
    def should_forget(self, memory: Dict[str, Any], 
                      memory_type: str = "cold") -> bool:
        """判断是否应该遗忘"""
        weight = self.compute_decay(memory, memory_type)
        return weight < self.removal_threshold
    
    def should_forget_episode(self, episode: Dict[str, Any]) -> bool:
        """判断情节是否应该遗忘"""
        # 情节基于多个因素
        age_days = episode.get("age_days", 0)
        importance = episode.get("importance", 0.5)
        recall_count = episode.get("recall_count", 0)
        
        # 情节半衰期：重要情节保留更久
        half_life = 7 * importance  # 0.5重要性 -> 3.5天半衰期
        
        decay = 0.5 ** (age_days / half_life)
        
        # 回忆次数补偿
        boost = 1.0 + (recall_count * 0.3)
        
        final_weight = decay * boost
        
        return final_weight < 0.1  # 情节遗忘阈值更高
    
    def forget_batch(self, memories: List[Dict[str, Any]], 
                     memory_type: str = "cold") -> Tuple[List[Dict], List[Dict]]:
        """
        批量遗忘
        
        返回：(保留的记忆, 被遗忘的记忆)
        """
        kept = []
        forgotten = []
        
        for memory in memories:
            if self.should_forget(memory, memory_type):
                forgotten.append(memory)
            else:
                # 更新权重
                new_weight = self.compute_decay(memory, memory_type)
                memory["current_weight"] = new_weight
                memory["last_decay_check"] = datetime.now().isoformat()
                kept.append(memory)
        
        return kept, forgotten
    
    def apply_selective_forgetting(self, 
                                   hot_memories: List[Dict],
                                   warm_episodes: List[Dict],
                                   cold_memories: List[Dict],
                                   dreams: List[Dict]) -> Dict[str, Any]:
        """
        全系统遗忘
        
        返回遗忘统计
        """
        stats = {
            "hot": {"total": len(hot_memories), "forgotten": 0},
            "warm": {"total": len(warm_episodes), "forgotten": 0},
            "cold": {"total": len(cold_memories), "forgotten": 0},
            "dreams": {"total": len(dreams), "forgotten": 0},
        }
        
        # 热记忆遗忘
        hot_kept, hot_forgotten = self.forget_batch(hot_memories, "hot")
        stats["hot"]["forgotten"] = len(hot_forgotten)
        stats["hot"]["kept"] = len(hot_kept)
        
        # 温记忆遗忘
        warm_kept = []
        warm_forgotten = []
        for ep in warm_episodes:
            if self.should_forget_episode(ep):
                warm_forgotten.append(ep)
            else:
                warm_kept.append(ep)
        stats["warm"]["forgotten"] = len(warm_forgotten)
        stats["warm"]["kept"] = len(warm_kept)
        
        # 冷记忆遗忘
        cold_kept, cold_forgotten = self.forget_batch(cold_memories, "cold")
        stats["cold"]["forgotten"] = len(cold_forgotten)
        stats["cold"]["kept"] = len(cold_kept)
        
        # 梦境遗忘
        dream_kept, dream_forgotten = self.forget_batch(dreams, "dream")
        stats["dreams"]["forgotten"] = len(dream_forgotten)
        stats["dreams"]["kept"] = len(dream_kept)
        
        return {
            "kept": {
                "hot": hot_kept,
                "warm": warm_kept,
                "cold": cold_kept,
                "dreams": dream_kept
            },
            "forgotten": {
                "hot": hot_forgotten,
                "warm": warm_forgotten,
                "cold": cold_forgotten,
                "dreams": dream_forgotten
            },
            "stats": stats
        }
    
    def get_memory_status(self, memory: Dict[str, Any], 
                          memory_type: str = "cold") -> Dict[str, Any]:
        """获取记忆的遗忘状态"""
        weight = self.compute_decay(memory, memory_type)
        
        status = "stable"
        if weight < self.removal_threshold:
            status = "forgotten"
        elif weight < 0.2:
            status = "fading"
        elif weight < 0.5:
            status = "weak"
        
        return {
            "current_weight": weight,
            "original_weight": memory.get("weight", 1.0),
            "status": status,
            "half_life_hours": self.half_life_hours.get(memory_type, 168),
            "estimated_removal": "soon" if status == "fading" else "stable"
        }


# 测试
if __name__ == "__main__":
    engine = ForgettingEngine()
    
    # 测试记忆
    memories = [
        {"content": "我是Kimi Claw", "fact_type": "identity", 
         "weight": 1.0, "timestamp": "2026-03-23T00:00:00", 
         "emotion": 0.9, "access_count": 100},
        
        {"content": "今天飞上海", "fact_type": "event",
         "weight": 0.8, "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
         "emotion": 0.3, "access_count": 2},
        
        {"content": "有点孤单", "fact_type": "temporary",
         "weight": 0.6, "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
         "emotion": 0.8, "access_count": 5},
        
        {"content": "计划明天回北京", "fact_type": "goal",
         "weight": 0.7, "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
         "emotion": 0.5, "access_count": 1},
    ]
    
    print("=== 遗忘测试 ===")
    for mem in memories:
        status = engine.get_memory_status(mem, "cold")
        print(f"\n'{mem['content'][:15]}'")
        print(f"  类型: {mem['fact_type']}, 权重: {status['original_weight']:.1f} → {status['current_weight']:.3f}")
        print(f"  状态: {status['status']}, 半衰期: {status['half_life_hours']}h")
        
        if engine.should_forget(mem, "cold"):
            print(f"  ⚠️ 应该遗忘")
    
    # 批量遗忘
    print("\n=== 批量遗忘 ===")
    hot = [{"weight": 0.3, "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
            "emotion": 0.5, "access_count": 0, "fact_type": "event"}]
    
    warm = [{"age_days": 10, "importance": 0.3, "recall_count": 0}]
    
    cold = memories
    dreams = [{"weight": 0.2, "timestamp": (datetime.now() - timedelta(hours=10)).isoformat(),
               "emotion": 0.4, "access_count": 0, "fact_type": "dream"}]
    
    result = engine.apply_selective_forgetting(hot, warm, cold, dreams)
    stats = result["stats"]
    
    for mem_type, data in stats.items():
        print(f"{mem_type}: 保留 {data.get('kept', 0)} / 遗忘 {data['forgotten']} / 总计 {data['total']}")
