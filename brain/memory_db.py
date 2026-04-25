#!/usr/bin/env python3
"""
New Brain - SQLite Memory Database
冷记忆持久化层

表结构：
- raw_memories: 原始记忆（最细粒度）
- reconstructed: 重构记忆（模型压缩后，多级抽象）
- dream_fragments: 梦境碎片
- beliefs: 信念锚点
"""

import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime


class MemoryDatabase:
    """
    冷记忆SQLite数据库
    
    支持：
    - 原始记忆存储/查询
    - 递归重构（多级抽象）
    - 梦境碎片管理
    - 信念锚点
    """
    
    def __init__(self, db_path: str = "brain/cold_memory.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """初始化数据库和表"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # 原始记忆
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                emotion REAL DEFAULT 0.0,
                valence REAL DEFAULT 0.0,
                arousal REAL DEFAULT 0.5,
                tags TEXT,  -- JSON array
                weight REAL DEFAULT 1.0,
                clarity REAL DEFAULT 1.0,
                certainty TEXT DEFAULT 'certain',
                metadata TEXT  -- JSON
            )
        """)
        
        # 重构记忆（多级抽象）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reconstructed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_ids TEXT,  -- JSON array of raw_memory ids
                summary TEXT NOT NULL,
                theme TEXT,
                abstraction_level INTEGER DEFAULT 1,  -- 1=周, 2=月, 3=人格核心
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                emotion REAL DEFAULT 0.0,
                weight REAL DEFAULT 1.0,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        # 梦境碎片
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dream_fragments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme TEXT NOT NULL,
                scenes TEXT,  -- JSON array
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                original_intensity REAL DEFAULT 0.5,
                current_weight REAL DEFAULT 0.1,
                clarity REAL DEFAULT 0.3,
                certainty TEXT DEFAULT 'uncertain',
                source TEXT DEFAULT 'dream',
                emotional_residue REAL DEFAULT 0.0,
                associated_beliefs TEXT,  -- JSON array
                last_decay TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 信念锚点
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS beliefs (
                key TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                certainty TEXT DEFAULT 'certain',
                weight REAL DEFAULT 1.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 身份元数据（identity_anchors / relationship_core / self_narrative / user_profile）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS identity_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_raw_time ON raw_memories(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_raw_tags ON raw_memories(tags)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recon_level ON reconstructed(abstraction_level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dream_time ON dream_fragments(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dream_weight ON dream_fragments(current_weight)")
        
        self.conn.commit()
        print(f"[DB] Initialized SQLite at {self.db_path}")
    
    def set_metadata(self, key: str, value: Any):
        """存储任意JSON元数据"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO identity_metadata (key, value, updated_at) VALUES (?, ?, ?)",
            (key, json.dumps(value, ensure_ascii=False), datetime.now().isoformat())
        )
        self.conn.commit()
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """读取元数据"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM identity_metadata WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    
    def get_all_metadata(self) -> Dict[str, Any]:
        """读取所有元数据"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value FROM identity_metadata")
        return {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
    
    def add_raw_memory(self, content: str, source: str = None, emotion: float = 0.0,
                       valence: float = 0.0, arousal: float = 0.5,
                       tags: List[str] = None, metadata: Dict = None) -> int:
        """添加原始记忆"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO raw_memories 
            (content, source, emotion, valence, arousal, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            content, source, emotion, valence, arousal,
            json.dumps(tags or [], ensure_ascii=False),
            json.dumps(metadata or {}, ensure_ascii=False)
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def query_raw_memories(self, start_time: str = None, end_time: str = None,
                          tags: List[str] = None, limit: int = 100) -> List[Dict]:
        """查询原始记忆"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM raw_memories WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        if tags:
            # SQLite JSON匹配简化版
            for tag in tags:
                query += f" AND tags LIKE ?"
                params.append(f'%"{tag}"%')
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [self._row_to_dict(r) for r in rows]
    
    def get_recent_raw(self, n: int = 50) -> List[Dict]:
        """获取最近N条原始记忆"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM raw_memories ORDER BY timestamp DESC LIMIT ?",
            (n,)
        )
        rows = cursor.fetchall()
        return [self._row_to_dict(r) for r in rows]
    
    # === Reconstructed Memories ===
    
    def add_reconstructed(self, summary: str, source_ids: List[int],
                          theme: str = None, abstraction_level: int = 1,
                          emotion: float = 0.0, weight: float = 1.0) -> int:
        """添加重构记忆"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO reconstructed 
            (source_ids, summary, theme, abstraction_level, emotion, weight)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            json.dumps(source_ids, ensure_ascii=False),
            summary, theme, abstraction_level, emotion, weight
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_reconstructed_by_level(self, level: int, limit: int = 100) -> List[Dict]:
        """按抽象级别获取重构记忆"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM reconstructed 
            WHERE abstraction_level = ?
            ORDER BY timestamp DESC LIMIT ?
        """, (level, limit))
        rows = cursor.fetchall()
        return [self._row_to_dict(r) for r in rows]
    
    def get_reconstructed_for_reconstruction(self, level: int, 
                                             since: str = None) -> List[Dict]:
        """获取需要进一步重构的记忆"""
        cursor = self.conn.cursor()
        if since:
            cursor.execute("""
                SELECT * FROM reconstructed 
                WHERE abstraction_level = ? AND timestamp >= ?
                ORDER BY timestamp
            """, (level, since))
        else:
            cursor.execute("""
                SELECT * FROM reconstructed 
                WHERE abstraction_level = ?
                ORDER BY timestamp
            """, (level,))
        rows = cursor.fetchall()
        return [self._row_to_dict(r) for r in rows]
    
    # === Dream Fragments ===
    
    def add_dream_fragment(self, theme: str, scenes: List[str], 
                          original_intensity: float = 0.5,
                          current_weight: float = 0.1,
                          clarity: float = 0.3,
                          emotional_residue: float = 0.0,
                          associated_beliefs: List[str] = None) -> int:
        """添加梦境碎片"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO dream_fragments 
            (theme, scenes, original_intensity, current_weight, clarity,
             emotional_residue, associated_beliefs)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            theme,
            json.dumps(scenes, ensure_ascii=False),
            original_intensity,
            current_weight,
            clarity,
            emotional_residue,
            json.dumps(associated_beliefs or [], ensure_ascii=False)
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_active_dreams(self, min_weight: float = 0.05) -> List[Dict]:
        """获取活跃的梦境碎片"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM dream_fragments 
            WHERE current_weight > ?
            ORDER BY current_weight DESC
        """, (min_weight,))
        rows = cursor.fetchall()
        return [self._row_to_dict(r) for r in rows]
    
    def update_dream_weight(self, dream_id: int, new_weight: float):
        """更新梦境权重（用于衰减）"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE dream_fragments 
            SET current_weight = ?, last_decay = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_weight, dream_id))
        self.conn.commit()
    
    def delete_dream(self, dream_id: int):
        """删除梦境（权重过低时）"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM dream_fragments WHERE id = ?", (dream_id,))
        self.conn.commit()
    
    # === Beliefs ===
    
    def set_belief(self, key: str, content: str, certainty: str = 'certain'):
        """设置/更新信念"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO beliefs 
            (key, content, certainty, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (key, content, certainty))
        self.conn.commit()
    
    def get_belief(self, key: str) -> Optional[Dict]:
        """获取单个信念"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM beliefs WHERE key = ?", (key,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def get_all_beliefs(self) -> Dict[str, str]:
        """获取所有信念"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, content FROM beliefs")
        rows = cursor.fetchall()
        return {r['key']: r['content'] for r in rows}
    
    def query_beliefs(self, keywords: List[str]) -> List[Dict]:
        """关键词查询信念"""
        cursor = self.conn.cursor()
        results = []
        for kw in keywords:
            cursor.execute(
                "SELECT * FROM beliefs WHERE content LIKE ?",
                (f'%{kw}%',)
            )
            results.extend([self._row_to_dict(r) for r in cursor.fetchall()])
        return results
    
    # === Statistics ===
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        cursor = self.conn.cursor()
        stats = {}
        
        for table in ['raw_memories', 'reconstructed', 'dream_fragments', 'beliefs']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
        
        # 各级重构数量
        cursor.execute(
            "SELECT abstraction_level, COUNT(*) FROM reconstructed GROUP BY abstraction_level"
        )
        stats['reconstructed_levels'] = {r[0]: r[1] for r in cursor.fetchall()}
        
        return stats
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """SQLite行转字典"""
        if row is None:
            return {}
        d = dict(row)
        # 解析JSON字段
        for field in ['tags', 'scenes', 'source_ids', 'associated_beliefs', 'metadata']:
            if field in d and d[field]:
                try:
                    d[field] = json.loads(d[field])
                except:
                    pass
        return d
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        self.close()
