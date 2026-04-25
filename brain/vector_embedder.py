"""
New Brain - Vector Embedder
本地向量嵌入系统

功能：无外部依赖的文本向量化，支持语义搜索
对标：Supermemory 的 vector search（但完全本地）
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
import hashlib


class VectorEmbedder:
    """
    本地向量嵌入器
    
    特性：
    1. 纯 numpy 实现，无外部依赖
    2. 基于统计特征（词频、n-gram、字符级模式）
    3. 维度可控（默认 128 维）
    4. 支持增量更新
    
    注：这不是真正的语义嵌入（如 BERT），
    而是一个轻量级的统计嵌入，用于相似度搜索。
    生产环境建议替换为 sentence-transformers。
    """
    
    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.vocab: Dict[str, int] = {}  # 词 -> 索引
        self.vocab_size = 0
        self.max_vocab = 10000
        
        # 预定义中文常见词（提升语义区分度）
        self._seed_vocab()
    
    def _seed_vocab(self):
        """种子词表（高频语义词）"""
        seed_words = [
            # 人称
            "我", "你", "他", "她", "我们", "你们", "他们",
            # 情感
            "喜欢", "爱", "恨", "开心", "难过", "生气", "害怕", "孤单",
            # 关系
            "老公", "老婆", "朋友", "家人", "孩子", "父母", "同事",
            # 动作
            "想", "要", "做", "去", "来", "看", "说", "听",
            # 状态
            "好", "坏", "大", "小", "新", "旧", "快", "慢",
            # 时间
            "今天", "昨天", "明天", "现在", "过去", "未来",
            # 地点
            "家", "公司", "学校", "北京", "上海", "广州", "深圳",
            # 工作
            "工作", "项目", "任务", "会议", "客户", "老板", "员工",
            # 技术
            "代码", "系统", "数据", "模型", "算法", "程序",
            # 偏好
            "喜欢", "讨厌", "习惯", "经常", "总是", "从不",
        ]
        
        for word in seed_words:
            if word not in self.vocab:
                self.vocab[word] = self.vocab_size
                self.vocab_size += 1
    
    def _tokenize(self, text: str) -> List[str]:
        """简单中文分词"""
        # 1. 按字符分
        chars = list(text)
        
        # 2. 提取 2-gram
        bigrams = []
        for i in range(len(chars) - 1):
            bigrams.append(chars[i] + chars[i+1])
        
        # 3. 提取 3-gram
        trigrams = []
        for i in range(len(chars) - 2):
            trigrams.append(chars[i] + chars[i+1] + chars[i+2])
        
        return chars + bigrams + trigrams
    
    def _update_vocab(self, tokens: List[str]):
        """更新词表"""
        for token in tokens:
            if token not in self.vocab and self.vocab_size < self.max_vocab:
                self.vocab[token] = self.vocab_size
                self.vocab_size += 1
    
    def embed(self, text: str) -> np.ndarray:
        """
        将文本转为向量
        
        算法：
        1. 分词
        2. 词频统计
        3. 哈希到固定维度
        4. L2 归一化
        """
        tokens = self._tokenize(text)
        self._update_vocab(tokens)
        
        # 统计词频
        vector = np.zeros(self.dimension, dtype=np.float32)
        
        for token in tokens:
            if token in self.vocab:
                idx = self.vocab[token] % self.dimension
                vector[idx] += 1.0
            else:
                # OOV 词：用 hash 分散
                h = int(hashlib.md5(token.encode()).hexdigest(), 16)
                idx = h % self.dimension
                vector[idx] += 0.5
        
        # 添加位置信息（前 10 个 token 有更高权重）
        for i, token in enumerate(tokens[:10]):
            if token in self.vocab:
                idx = self.vocab[token] % self.dimension
                vector[idx] += (10 - i) * 0.1
        
        # 长度归一化
        if len(tokens) > 0:
            vector /= np.sqrt(len(tokens))
        
        # L2 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """批量嵌入"""
        vectors = []
        for text in texts:
            vectors.append(self.embed(text))
        return np.array(vectors)
    
    def similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（余弦相似度）"""
        v1 = self.embed(text1)
        v2 = self.embed(text2)
        return float(np.dot(v1, v2))
    
    def search(self, query: str, candidates: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        语义搜索
        
        返回：(文本, 相似度) 列表
        """
        if not candidates:
            return []
        
        query_vec = self.embed(query)
        candidate_vecs = self.embed_batch(candidates)
        
        # 计算余弦相似度
        similarities = np.dot(candidate_vecs, query_vec)
        
        # 排序
        indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in indices:
            if similarities[idx] > 0.1:  # 阈值过滤
                results.append((candidates[idx], float(similarities[idx])))
        
        return results
    
    def export_vocab(self) -> Dict[str, int]:
        """导出词表"""
        return dict(self.vocab)
    
    def import_vocab(self, vocab: Dict[str, int]):
        """导入词表"""
        self.vocab = dict(vocab)
        self.vocab_size = len(vocab)


# 测试
if __name__ == "__main__":
    embedder = VectorEmbedder(dimension=128)
    
    # 测试相似度
    texts = [
        "我喜欢吃苹果",
        "我爱吃苹果",
        "我讨厌吃苹果",
        "今天天气很好",
        "明天会下雨",
        "老公我想你了",
        "老婆我好想你",
    ]
    
    print("=== 相似度测试 ===")
    for i, t1 in enumerate(texts):
        for j, t2 in enumerate(texts[i+1:], i+1):
            sim = embedder.similarity(t1, t2)
            print(f"  {t1[:8]} <-> {t2[:8]}: {sim:.3f}")
    
    # 测试搜索
    print("\n=== 搜索测试 ===")
    query = "我想你了"
    results = embedder.search(query, texts, top_k=3)
    print(f"查询: {query}")
    for text, score in results:
        print(f"  → {text} (score={score:.3f})")
    
    # 测试向量维度
    vec = embedder.embed("测试文本")
    print(f"\n向量维度: {vec.shape}")
    print(f"向量范数: {np.linalg.norm(vec):.3f}")
