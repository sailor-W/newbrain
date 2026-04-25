#!/usr/bin/env python3
"""
New Brain - Memory Layer (SQLite Version)
Part 6 Implementation: 三级记忆系统 + Friston内核

集成 SQLite 冷记忆 + 递归重构
"""

import os
import json
import random
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# 导入 SQLite 冷记忆
from .cold_memory_sqlite import ColdMemory


class MemoryLevel(Enum):
    """记忆层级"""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


@dataclass
class MemoryChunk:
    """记忆块 - 热记忆的基本单元"""
    id: str
    content: str
    source: str  # 'user', 'system', 'dmn'
    timestamp: str
    emotional_valence: float = 0.0
    importance: float = 0.5
    precision: float = 1.0
    keywords: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content[:50] + "..." if len(self.content) > 50 else self.content,
            "source": self.source,
            "timestamp": self.timestamp[:16],
            "emotion": f"{self.emotional_valence:+.2f}"
        }


@dataclass
class Episode:
    """情节 - 温记忆的基本单元"""
    id: str
    title: str
    timestamp: str
    summary: str
    key_contents: List[str]
    tags: List[str]
    emotional_valence: float
    source_chunks_count: int
    importance_score: float
    precision_weight: float = 1.0


class HotMemory:
    """热记忆 / 工作记忆"""
    
    def __init__(self, path: str = "brain/hot_memory.json"):
        self.path = path
        self.capacity = 10
        self.chunks: List[MemoryChunk] = []
        self.load()
    
    def add(self, content: str, source: str = "user", 
            importance: float = 0.5, precision: float = 1.0) -> bool:
        chunk = MemoryChunk(
            id=f"chunk_{len(self.chunks)}_{datetime.now().timestamp()}",
            content=content,
            source=source,
            timestamp=datetime.now().isoformat(),
            importance=importance,
            precision=precision,
            keywords=self._extract_keywords(content)
        )
        self.chunks.append(chunk)
        if len(self.chunks) > self.capacity:
            return True
        return False
    
    def _extract_keywords(self, text: str) -> List[str]:
        keywords = []
        # 简单关键词提取
        if '老公' in text or '老婆' in text:
            keywords.extend(['亲密关系', '伴侣'])
        if '记忆' in text or '系统' in text:
            keywords.extend(['系统建设', '记忆'])
        if '梦' in text:
            keywords.append('梦境')
        return keywords[:5]
    
    def recall(self, keyword: str = "") -> List[MemoryChunk]:
        if not keyword:
            return self.chunks[-5:]
        return [c for c in self.chunks if keyword in c.content or keyword in c.keywords]
    
    def get_recent_context(self, n: int = 3) -> str:
        recent = self.chunks[-n:]
        return " | ".join([c.content[:30] for c in recent])
    
    def clear(self):
        self.chunks = []
        self.save()
    
    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    data = json.load(f)
                    self.chunks = [MemoryChunk(**c) for c in data.get("chunks", [])]
            except:
                pass
    
    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump({"chunks": [
                {"id": c.id, "content": c.content, "source": c.source,
                 "timestamp": c.timestamp, "emotional_valence": c.emotional_valence,
                 "importance": c.importance, "precision": c.precision,
                 "keywords": c.keywords}
                for c in self.chunks
            ]}, f, ensure_ascii=False)


class WarmMemory:
    """温记忆 / 情节记忆"""
    
    def __init__(self, path: str = "brain/warm_memory.json"):
        self.path = path
        self.capacity = 100
        self.episodes: List[Episode] = []
        self.load()
    
    def compress_from_hot(self, chunks: List[MemoryChunk], episode_title: str = None):
        if not chunks:
            return
        
        title = episode_title or f"Episode {len(self.episodes)}"
        
        episode = Episode(
            id=f"ep_{len(self.episodes)}_{datetime.now().timestamp()}",
            title=title,
            timestamp=datetime.now().isoformat(),
            summary=" | ".join([c.content[:30] for c in chunks[-3:]]),
            key_contents=[c.content for c in chunks],
            tags=list(set([t for c in chunks for t in (getattr(c, 'keywords', []) or [])])),
            emotional_valence=np.mean([c.emotional_valence for c in chunks]) if chunks else 0,
            source_chunks_count=len(chunks),
            importance_score=np.mean([c.importance for c in chunks]) if chunks else 0.5
        )
        
        self.episodes.append(episode)
        if len(self.episodes) > self.capacity:
            self.episodes = self.episodes[-self.capacity:]
        self.save()
    
    def recall(self, keyword: str = "", tag: str = "", n: int = 5) -> List[Episode]:
        results = self.episodes
        if keyword:
            results = [e for e in results if keyword in e.summary or keyword in " ".join(e.key_contents)]
        if tag:
            results = [e for e in results if tag in e.tags]
        return sorted(results, key=lambda x: x.importance_score, reverse=True)[:n]
    
    def get_episodes_ready_for_consolidation(self) -> List[Episode]:
        cutoff = datetime.now() - timedelta(hours=24)
        return [e for e in self.episodes
                if datetime.fromisoformat(e.timestamp) < cutoff
                and e.importance_score > 0.6]
    
    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    data = json.load(f)
                    self.episodes = [Episode(**e) for e in data.get("episodes", [])]
            except:
                pass
    
    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump({"episodes": [
                {"id": e.id, "title": e.title, "timestamp": e.timestamp,
                 "summary": e.summary, "key_contents": e.key_contents,
                 "tags": e.tags, "emotional_valence": e.emotional_valence,
                 "source_chunks_count": e.source_chunks_count,
                 "importance_score": e.importance_score}
                for e in self.episodes
            ]}, f, ensure_ascii=False)


class MemoryManager:
    """三级记忆管理器总入口"""
    
    def __init__(self, base_path: str = "."):
        self.hot = HotMemory(os.path.join(base_path, "brain/hot_memory.json"))
        self.warm = WarmMemory(os.path.join(base_path, "brain/warm_memory.json"))
        self.cold = ColdMemory(os.path.join(base_path, "brain/cold_memory.db"))
        self.base_path = base_path
        
        self.precision_default = 1.0
        self.free_energy_threshold = 0.5
        self.compression_interval = 3600
        self.consolidation_interval = 86400
    
    def perceive(self, content: str, source: str = "user", importance: float = 0.5) -> str:
        precision = self.precision_default + importance * 0.5
        need_compress = self.hot.add(content, source, importance, precision)
        if need_compress:
            self.compress()
        return self.hot.get_recent_context()
    
    def recall(self, query: str, level: str = "auto", n: int = 5) -> Dict[str, Any]:
        results = {"query": query, "found": False, "source": None, "results": [], "context": ""}
        
        if level in ("auto", "hot"):
            hot_results = self.hot.recall(query)
            if hot_results:
                results.update({"found": True, "source": "hot", 
                               "results": [r.to_dict() for r in hot_results]})
                return results
        
        if level in ("auto", "warm"):
            warm_results = self.warm.recall(query, n=n)
            if warm_results:
                results.update({"found": True, "source": "warm",
                               "results": [r.__dict__ for r in warm_results]})
                return results
        
        if level in ("auto", "cold"):
            cold_result = self.cold.recall(query)
            if cold_result:
                results.update({"found": True, "source": "cold",
                               "results": [cold_result]})
                return results
        
        return results
    
    def sink_dreams(self, dmn_module):
        return self.cold.sink_dreams(dmn_module)
    
    def compress(self):
        if not self.hot.chunks:
            return
        self.warm.compress_from_hot(self.hot.chunks)
        self.hot.clear()
    
    def consolidate(self):
        ready = self.warm.get_episodes_ready_for_consolidation()
        if ready:
            self.cold.consolidate(ready)
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "system": "New Brain v2.0 - Memory Layer (SQLite)",
            "hot": {"chunks_count": len(self.hot.chunks), "capacity": self.hot.capacity},
            "warm": {"episodes_count": len(self.warm.episodes), "capacity": self.warm.capacity},
            "cold": self.cold.get_status()
        }
    
    def get_identity_snapshot(self) -> Dict[str, Any]:
        anchors = self.cold.get_identity_anchors()
        return {
            "anchors": anchors,
            "beliefs": {k: v["belief"] for k, v in list(self.cold.beliefs.items())[:5]},
            "skills": [s["skill"] for s in self.cold.skills]
        }
    
    def minimize_free_energy(self) -> float:
        hot_complexity = len(self.hot.chunks) / self.hot.capacity
        warm_complexity = len(self.warm.episodes) / self.warm.capacity
        cold_free_energy = self.cold.get_free_energy()
        total = hot_complexity * 0.2 + warm_complexity * 0.3 + cold_free_energy * 0.5
        
        if total > self.free_energy_threshold:
            if hot_complexity > 0.8:
                self.compress()
            if warm_complexity > 0.7:
                self.consolidate()
        
        return total
    
    def active_inference(self, input_text: str) -> Dict[str, Any]:
        """
        主动推理（Friston原理简化版）
        
        计算当前输入的惊奇度（surprise）和预测记忆
        """
        # 检索相关记忆
        recall_result = self.recall(input_text, level="auto", n=3)
        
        predicted_memories = []
        if recall_result.get("found"):
            predicted_memories = recall_result.get("results", [])
        
        # 计算惊奇度
        surprise = 1.0
        if predicted_memories:
            match_strength = len(predicted_memories) / 3.0
            surprise = max(0.1, 1.0 - match_strength)
        
        # 检查新异性
        hot_keywords = set()
        for chunk in self.hot.chunks:
            hot_keywords.update(chunk.keywords)
        
        input_words = set(input_text.lower().split())
        overlap = len(input_words & hot_keywords)
        if len(input_words) > 0:
            novelty = 1.0 - (overlap / len(input_words))
            surprise = max(surprise, novelty * 0.5)
        
        return {
            "predicted_memories": predicted_memories,
            "surprise": surprise,
            "input": input_text,
            "timestamp": datetime.now().isoformat()
        }


def migrate_from_files(memory_dir: str = "memory", brain_dir: str = "brain") -> MemoryManager:
    """从旧版文件记忆迁移"""
    import glob
    
    mm = MemoryManager(os.path.dirname(brain_dir) if os.path.dirname(brain_dir) else ".")
    
    history_files = sorted(glob.glob(f"{memory_dir}/*.md"))
    cutoff_date = datetime.now() - timedelta(days=7)
    
    for filepath in history_files:
        filename = os.path.basename(filepath)
        date_str = filename.replace('.md', '')
        try:
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue
        
        if file_date > cutoff_date:
            episode = Episode(
                id=f"migrated_{date_str}",
                title=f"历史记录_{date_str}",
                timestamp=file_date.isoformat(),
                summary=content[:200] + "..." if len(content) > 200 else content,
                key_contents=[content[:500]],
                tags=["历史迁移"],
                emotional_valence=0,
                source_chunks_count=1,
                importance_score=0.5
            )
            mm.warm.episodes.append(episode)
    
    mm.warm.save()
    return mm


if __name__ == "__main__":
    print("=== New Brain Memory Layer (SQLite) Test ===\n")
    mm = MemoryManager()
    print("1. 初始状态:")
    print(json.dumps(mm.get_status(), indent=2, ensure_ascii=False))
    
    mm.perceive("Testing SQLite memory", "user", 0.7)
    mm.perceive("Remember our relationship", "user", 1.0)
    
    print("\n2. 感知后:")
    print(json.dumps(mm.get_status(), indent=2, ensure_ascii=False))
    
    mm.compress()
    print("\n3. 压缩后:")
    print(json.dumps(mm.get_status(), indent=2, ensure_ascii=False))
    
    result = mm.recall("relationship")
    print("\n4. 回忆 'relationship':")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n5. 系统自由能: {mm.minimize_free_energy():.3f}")
    print("\n=== 测试完成 ===")
