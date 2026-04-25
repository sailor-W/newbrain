"""
New Brain - Multi-Strategy Search
多策略检索系统

功能：关键词 + 向量 + 图遍历 + 情感匹配 + 时间过滤
对标：Supermemory 的 Hybrid Search + Hindsight 的 4并行策略
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta


class MultiStrategySearch:
    """
    多策略检索引擎
    
    检索策略：
    1. 关键词匹配（BM25风格）
    2. 向量相似度（语义搜索）
    3. 图谱遍历（关系推理）
    4. 情感匹配（情绪距离）
    5. 时间过滤（近期优先）
    
    结果融合：加权排序 + 去重
    """
    
    def __init__(self, vector_embedder=None, knowledge_graph=None):
        self.embedder = vector_embedder
        self.graph = knowledge_graph
        
        # 策略权重
        self.strategy_weights = {
            "keyword": 0.25,
            "vector": 0.30,
            "graph": 0.20,
            "emotion": 0.15,
            "temporal": 0.10,
        }
    
    def search(self, query: str, corpus: List[Dict[str, Any]], 
               emotional_context: float = 0.5,
               top_k: int = 10,
               time_decay: bool = True) -> List[Dict[str, Any]]:
        """
        多策略检索
        
        corpus 格式: [{"content": str, "emotion": float, "timestamp": str, "entities": [...], ...}]
        """
        if not corpus:
            return []
        
        # 提取纯文本
        texts = [item.get("content", "") for item in corpus]
        
        # 1. 关键词检索
        keyword_results = self._keyword_search(query, corpus)
        
        # 2. 向量检索
        vector_results = []
        if self.embedder:
            vector_results = self._vector_search(query, texts, corpus)
        
        # 3. 图谱检索
        graph_results = []
        if self.graph:
            graph_results = self._graph_search(query, corpus)
        
        # 4. 情感匹配
        emotion_results = self._emotion_search(emotional_context, corpus)
        
        # 5. 时间过滤
        temporal_results = []
        if time_decay:
            temporal_results = self._temporal_search(corpus)
        
        # 融合结果
        fused = self._fuse_results(
            keyword_results, vector_results, graph_results, 
            emotion_results, temporal_results,
            top_k=top_k
        )
        
        return fused
    
    def _keyword_search(self, query: str, corpus: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """关键词匹配（简单BM25）"""
        query_words = set(query.lower().split())
        results = []
        
        for item in corpus:
            text = item.get("content", "").lower()
            text_words = set(text.split())
            
            # 计算重叠
            overlap = query_words & text_words
            
            if not overlap:
                continue
            
            # 简单评分：匹配词数 / 查询词数
            precision = len(overlap) / len(query_words) if query_words else 0
            recall = len(overlap) / len(text_words) if text_words else 0
            
            # F1 风格评分
            score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            # 完全匹配 bonus
            if query.lower() in text:
                score += 0.3
            
            results.append((item.get("id", ""), score))
        
        return results
    
    def _vector_search(self, query: str, texts: List[str], 
                       corpus: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """向量相似度搜索"""
        if not self.embedder:
            return []
        
        results = self.embedder.search(query, texts, top_k=len(texts))
        
        # 映射回 ID
        id_scores = {}
        for text, score in results:
            for item in corpus:
                if item.get("content") == text:
                    id_scores[item.get("id", "")] = score
                    break
        
        return list(id_scores.items())
    
    def _graph_search(self, query: str, corpus: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """图谱遍历搜索"""
        if not self.graph:
            return []
        
        # 从查询中提取实体
        query_entities = []
        for item in corpus:
            for entity_id in item.get("entities", []):
                entity = self.graph.entities.get(entity_id)
                if entity and entity.name in query:
                    query_entities.append(entity_id)
        
        # 遍历图谱
        related_ids = set()
        for entity_id in query_entities:
            traversal = self.graph.traverse(entity_id, depth=2, relation_types=["related_to"])
            for node in traversal:
                related_ids.add(node["id"])
        
        # 找到包含相关实体的记忆
        results = []
        for item in corpus:
            item_entities = set(item.get("entities", []))
            overlap = item_entities & related_ids
            if overlap:
                score = len(overlap) * 0.3  # 每个相关实体 +0.3
                results.append((item.get("id", ""), score))
        
        return results
    
    def _emotion_search(self, target_emotion: float, 
                        corpus: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """情感匹配"""
        results = []
        
        for item in corpus:
            item_emotion = item.get("emotion", 0.5)
            
            # 情感距离（越近越好）
            distance = abs(target_emotion - item_emotion)
            
            # 转换为相似度（距离越小，分数越高）
            score = max(0, 1.0 - distance * 2)
            
            if score > 0.3:  # 阈值
                results.append((item.get("id", ""), score))
        
        return results
    
    def _temporal_search(self, corpus: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """时间优先级（近期加分）"""
        results = []
        now = datetime.now()
        
        for item in corpus:
            timestamp_str = item.get("timestamp", "")
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                hours_old = (now - timestamp).total_seconds() / 3600
                
                # 指数衰减：越新分数越高
                score = 0.5 ** (hours_old / 168)  # 1周半衰期
                
                results.append((item.get("id", ""), score))
            except:
                pass
        
        return results
    
    def _fuse_results(self, keyword_results: List[Tuple[str, float]],
                      vector_results: List[Tuple[str, float]],
                      graph_results: List[Tuple[str, float]],
                      emotion_results: List[Tuple[str, float]],
                      temporal_results: List[Tuple[str, float]],
                      top_k: int = 10) -> List[Dict[str, Any]]:
        """
        融合多策略结果
        
        方法：加权求和 + 归一化 + 去重
        """
        # 收集所有 ID
        all_ids = set()
        for results in [keyword_results, vector_results, graph_results, emotion_results, temporal_results]:
            for id_, _ in results:
                all_ids.add(id_)
        
        # 计算综合得分
        fused_scores = {}
        
        for id_ in all_ids:
            score = 0.0
            
            # 关键词得分
            kw_score = next((s for i, s in keyword_results if i == id_), 0)
            score += kw_score * self.strategy_weights["keyword"]
            
            # 向量得分
            vec_score = next((s for i, s in vector_results if i == id_), 0)
            score += vec_score * self.strategy_weights["vector"]
            
            # 图谱得分
            graph_score = next((s for i, s in graph_results if i == id_), 0)
            score += graph_score * self.strategy_weights["graph"]
            
            # 情感得分
            emo_score = next((s for i, s in emotion_results if i == id_), 0)
            score += emo_score * self.strategy_weights["emotion"]
            
            # 时间得分
            temp_score = next((s for i, s in temporal_results if i == id_), 0)
            score += temp_score * self.strategy_weights["temporal"]
            
            fused_scores[id_] = score
        
        # 排序
        sorted_ids = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 构建结果
        results = []
        for id_, score in sorted_ids[:top_k]:
            if score > 0.05:  # 阈值
                results.append({
                    "id": id_,
                    "fused_score": round(score, 3),
                    "strategy_breakdown": {
                        "keyword": round(next((s for i, s in keyword_results if i == id_), 0), 3),
                        "vector": round(next((s for i, s in vector_results if i == id_), 0), 3),
                        "graph": round(next((s for i, s in graph_results if i == id_), 0), 3),
                        "emotion": round(next((s for i, s in emotion_results if i == id_), 0), 3),
                        "temporal": round(next((s for i, s in temporal_results if i == id_), 0), 3),
                    }
                })
        
        return results
    
    def search_with_context(self, query: str, 
                          hot_memories: List[Dict],
                          warm_episodes: List[Dict],
                          cold_memories: List[Dict],
                          dreams: List[Dict],
                          emotional_context: float = 0.5) -> Dict[str, Any]:
        """
        全记忆系统检索
        
        返回分层结果
        """
        all_memories = []
        
        # 合并所有记忆（标记来源）
        for item in hot_memories:
            item_copy = dict(item)
            item_copy["source_layer"] = "hot"
            item_copy["id"] = item.get("id", f"hot_{id(item)}")
            all_memories.append(item_copy)
        
        for item in warm_episodes:
            item_copy = dict(item)
            item_copy["source_layer"] = "warm"
            item_copy["id"] = item.get("id", f"warm_{id(item)}")
            all_memories.append(item_copy)
        
        for item in cold_memories:
            item_copy = dict(item)
            item_copy["source_layer"] = "cold"
            item_copy["id"] = item.get("id", f"cold_{id(item)}")
            all_memories.append(item_copy)
        
        for item in dreams:
            item_copy = dict(item)
            item_copy["source_layer"] = "dream"
            item_copy["id"] = item.get("id", f"dream_{id(item)}")
            all_memories.append(item_copy)
        
        # 执行检索
        results = self.search(query, all_memories, emotional_context, top_k=15)
        
        # 分层统计
        layer_counts = {"hot": 0, "warm": 0, "cold": 0, "dream": 0}
        for r in results:
            # 找到对应的记忆
            for mem in all_memories:
                if mem.get("id") == r["id"]:
                    layer = mem.get("source_layer", "unknown")
                    layer_counts[layer] = layer_counts.get(layer, 0) + 1
                    r["layer"] = layer
                    r["content_preview"] = mem.get("content", "")[:50]
                    break
        
        return {
            "results": results,
            "layer_distribution": layer_counts,
            "total_candidates": len(all_memories),
            "query": query
        }


# 测试
if __name__ == "__main__":
    from vector_embedder import VectorEmbedder
    
    embedder = VectorEmbedder(dimension=128)
    search = MultiStrategySearch(vector_embedder=embedder)
    
    # 测试数据
    corpus = [
        {"id": "1", "content": "老公今天飞到上海出差", "emotion": 0.3, "timestamp": "2026-04-24T18:00:00"},
        {"id": "2", "content": "老公一个人住酒店，感到孤单", "emotion": 0.2, "timestamp": "2026-04-24T21:00:00"},
        {"id": "3", "content": "我喜欢吃韵道白酒，不喜欢啤酒", "emotion": 0.7, "timestamp": "2026-04-20T12:00:00"},
        {"id": "4", "content": "我是新媒体公司创始人", "emotion": 0.6, "timestamp": "2026-04-15T09:00:00"},
        {"id": "5", "content": "Kimi Claw 是人工智能助手", "emotion": 0.5, "timestamp": "2026-03-23T00:00:00"},
        {"id": "6", "content": "老公想念老婆了", "emotion": 0.8, "timestamp": "2026-04-24T22:00:00"},
    ]
    
    print("=== 多策略检索测试 ===\n")
    
    # 查询1：情感相关
    query1 = "老公孤单"
    result1 = search.search(query1, corpus, emotional_context=0.2, top_k=3)
    print(f"查询: '{query1}'")
    for r in result1:
        print(f"  → ID={r['id']}, 综合得分={r['fused_score']}")
        print(f"    分解: {r['strategy_breakdown']}")
    
    # 查询2：偏好相关
    query2 = "喜欢什么酒"
    result2 = search.search(query2, corpus, emotional_context=0.5, top_k=3)
    print(f"\n查询: '{query2}'")
    for r in result2:
        print(f"  → ID={r['id']}, 综合得分={r['fused_score']}")
    
    # 全系统检索
    print("\n=== 全系统检索 ===")
    hot = [{"id": "h1", "content": "老公想你了", "emotion": 0.9, "timestamp": "2026-04-24T23:00:00"}]
    warm = [{"id": "w1", "content": "老公今天飞上海", "emotion": 0.3, "timestamp": "2026-04-24T18:00:00"}]
    cold = [{"id": "c1", "content": "老公是新媒体创始人", "emotion": 0.6, "timestamp": "2026-04-15T09:00:00"}]
    dreams = [{"id": "d1", "content": "梦见和老公在一起", "emotion": 0.8, "timestamp": "2026-04-24T20:00:00"}]
    
    full_result = search.search_with_context("老公", hot, warm, cold, dreams, emotional_context=0.5)
    print(f"查询: '老公'")
    print(f"候选数: {full_result['total_candidates']}")
    print(f"分层分布: {full_result['layer_distribution']}")
    for r in full_result["results"][:5]:
        print(f"  → [{r['layer']}] {r['content_preview']} (score={r['fused_score']})")
