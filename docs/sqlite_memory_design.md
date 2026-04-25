# New Brain SQLite 冷记忆架构设计文档

## 1. 背景与目标

### 当前问题
- `cold_memory.json` 全量加载进内存，容量受限
- 每次读写都是整个文件，性能差
- 无查询能力，只能遍历
- 梦境/信念/原始记忆混在一起，无分层
- 无持久化索引，搜索慢

### 目标
- 用 SQLite 替换 JSON 文件，支持海量存储
- 实现**递归重构**：小模型定期压缩记忆，生成多级抽象
- 保持现有接口不变，内部透明迁移
- 支持增量备份到 IMA 知识库

---

## 2. 架构

```
用户对话
    ↓
热记忆 (HotMemory) — 内存中，最近10条
    ↓
压缩 → 温记忆 (WarmMemory) — 内存中，情节
    ↓
沉降 → 冷记忆 (ColdMemory) — SQLite 数据库
    │
    ├── raw_memories: 原始输入（细粒度）
    ├── reconstructed: 重构记忆（多级抽象）
    │   ├── Level 1: 周度主题压缩
    │   ├── Level 2: 月度人格摘要
    │   └── Level 3: 年度核心信念
    ├── dream_fragments: 梦境碎片（带衰减）
    └── beliefs: 身份锚点（长期稳定）
    ↓
空闲时触发递归重构（小模型）
    ↓
定期备份到 IMA 知识库
```

---

## 3. SQLite 表结构

### 3.1 raw_memories — 原始记忆
```sql
CREATE TABLE raw_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,           -- 原始内容
    source TEXT,                     -- user / system / dmn
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    emotion REAL DEFAULT 0.0,        -- 整体情绪值
    valence REAL DEFAULT 0.0,        -- 愉悦度
    arousal REAL DEFAULT 0.5,        -- 唤起度
    tags TEXT,                       -- JSON ["亲密关系", "工作"]
    weight REAL DEFAULT 1.0,         -- 初始权重
    clarity REAL DEFAULT 1.0,        -- 清晰度
    certainty TEXT DEFAULT 'certain',
    metadata TEXT                    -- JSON 扩展字段
);
```

### 3.2 reconstructed — 重构记忆（多级抽象）
```sql
CREATE TABLE reconstructed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_ids TEXT,                 -- JSON [1,2,3] 原始记忆ID
    summary TEXT NOT NULL,           -- 压缩摘要
    theme TEXT,                      -- 主题标签
    abstraction_level INTEGER DEFAULT 1,  -- 1=周, 2=月, 3=人格
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    emotion REAL DEFAULT 0.0,
    weight REAL DEFAULT 1.0,
    last_accessed TEXT,              -- 最近访问时间
    access_count INTEGER DEFAULT 0   -- 访问计数
);
```

### 3.3 dream_fragments — 梦境碎片
```sql
CREATE TABLE dream_fragments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme TEXT NOT NULL,
    scenes TEXT,                     -- JSON ["场景1", "场景2"]
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    original_intensity REAL DEFAULT 0.5,
    current_weight REAL DEFAULT 0.1,  -- 可衰减
    clarity REAL DEFAULT 0.3,
    certainty TEXT DEFAULT 'uncertain',
    source TEXT DEFAULT 'dream',
    emotional_residue REAL DEFAULT 0.0,
    associated_beliefs TEXT,         -- JSON ["belief_key1"]
    last_decay TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 beliefs — 信念锚点
```sql
CREATE TABLE beliefs (
    key TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    certainty TEXT DEFAULT 'certain',
    weight REAL DEFAULT 1.0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. 递归重构流程

### 4.1 触发条件
- **定时触发**：每日凌晨 3:00（低负载时段）
- **手动触发**：用户命令 `/reconstruct`
- **空闲触发**：系统空闲 > 5 分钟时检测

### 4.2 重构层级

**Level 1: 周度压缩（最近7天）**
```
输入：最近7天的 raw_memories（最多 50 条）
小模型 Prompt：
"以下是过去一周的交互记录，请总结核心主题、情绪走向、关键事件。
输出 JSON：{summary, theme, emotion, key_events}"

输出：1 条 reconstructed (abstraction_level=1)
存储：source_ids 指向原始记录
```

**Level 2: 月度人格摘要（最近30天）**
```
输入：最近30天的 Level 1 记录（最多 30 条）
小模型 Prompt：
"以下是过去一个月的周度摘要，请提炼人格特征、关系模式、长期趋势。
输出 JSON：{personality_traits, relationship_dynamics, growth_direction}"

输出：1 条 reconstructed (abstraction_level=2)
```

**Level 3: 年度核心信念（所有 Level 2）**
```
输入：所有 Level 2 记录
小模型 Prompt：
"基于所有月度摘要，定义这个AI的核心身份、使命、价值观。
输出 JSON：{identity_statement, core_values, life_mission}"

输出：1 条 reconstructed (abstraction_level=3)
同时更新 beliefs 表中的核心条目
```

### 4.3 回应时怎么读
```
用户提问
    ↓
1. 查 beliefs（最稳定，O(1)）
2. 查 Level 3（人格核心）
3. 查 Level 2（近期主题）
4. 查 raw_memories（细节，按关键词过滤）
5. 查 dream_fragments（情绪色调）
    ↓
融合生成回应
```

---

## 5. 接口设计

### 5.1 MemoryDatabase 类（新增）
位置：`brain/memory_db.py`

```python
class MemoryDatabase:
    def __init__(self, db_path: str)
    
    # Raw Memories
    def add_raw_memory(content, source, emotion, tags) -> int
    def query_raw_memories(start_time, end_time, tags, limit) -> List[Dict]
    def get_recent_raw(n) -> List[Dict]
    
    # Reconstructed
    def add_reconstructed(summary, source_ids, theme, level) -> int
    def get_reconstructed_by_level(level, limit) -> List[Dict]
    
    # Dreams
    def add_dream_fragment(theme, scenes, ...) -> int
    def get_active_dreams(min_weight) -> List[Dict]
    def update_dream_weight(id, new_weight)
    def delete_dream(id)
    
    # Beliefs
    def set_belief(key, content, certainty)
    def get_belief(key) -> Dict
    def get_all_beliefs() -> Dict[str, str]
    
    # Stats
    def get_stats() -> Dict
```

### 5.2 ColdMemory 改造（修改）
位置：`brain/memory.py` 中的 `ColdMemory` 类

**改造策略**：
- 保留现有接口（`add_belief`, `recall`, `save/load`）
- 内部用 SQLite 替代 JSON 文件
- 新增 `reconstruct()` 方法触发递归压缩
- 新增 `get_dream_influence()` 查询梦境影响

```python
class ColdMemory:
    def __init__(self, path: str = "brain/cold_memory.db"):
        self.db = MemoryDatabase(path)
        self._load_beliefs_from_config()
    
    def add_belief(self, key: str, content: str, certainty: str = "certain"):
        self.db.set_belief(key, content, certainty)
    
    def recall(self, keyword: str = "", emotional_context: float = 0.0):
        # 从数据库查询 beliefs + dreams + raw
        beliefs = self.db.query_beliefs([keyword])
        dreams = self.db.get_active_dreams()
        # 融合，带情绪加权
        ...
    
    def reconstruct(self, model) -> bool:
        """触发递归重构"""
        # Level 1: 压缩最近7天 raw
        recent_raw = self.db.get_recent_raw(50)
        level1 = model.compress_memories(recent_raw, level=1)
        self.db.add_reconstructed(level1['summary'], [...], level1['theme'], 1)
        
        # Level 2: 压缩最近30天 Level 1
        recent_l1 = self.db.get_reconstructed_by_level(1, limit=30)
        level2 = model.compress_memories(recent_l1, level=2)
        ...
    
    def get_dream_influence(self, topic: str) -> float:
        """获取梦境对某主题的情绪影响"""
        dreams = self.db.get_active_dreams()
        # 计算关联度
        ...
```

---

## 6. 数据流

### 6.1 写入流
```
用户输入 "老公，我想你了"
    ↓
HotMemory.add("老公，我想你了", source="user", emotion=0.8)
    ↓
触发压缩 → WarmMemory.create_episode(chunks=[...])
    ↓
情节沉降 → ColdMemory.db.add_raw_memory(
    content="老公，我想你了",
    source="user", 
    emotion=0.8,
    tags=["亲密关系"]
)
    ↓
（可选）触发小模型重构 → reconstructed 新增 Level 1 记录
```

### 6.2 读取流
```
用户输入 "你还记得我们怎么开始的吗"
    ↓
TPN处理 → 提取关键词 ["开始", "我们"]
    ↓
ColdMemory.recall(keywords=["开始", "我们"], emotional_context=0.6)
    ↓
1. 查 beliefs: "relationship_origin" → "2026-03-23定义伴侣关系"
2. 查 reconstructed Level 3: "核心关系模式"
3. 查 reconstructed Level 2: "3月主题：关系建立"
4. 查 raw_memories: 按关键词过滤，取最近10条
5. 查 dreams: 取情绪共振的梦境碎片
    ↓
融合 → 生成回应
```

---

## 7. 梦境融合增强

### 7.1 存储增强
```sql
-- 梦境增加关联记忆字段
dream_fragments.associated_raw_ids TEXT  -- JSON [1,2,3]
```

### 7.2 查询增强
```python
def get_dreams_related_to(self, raw_ids: List[int]) -> List[Dict]:
    """查找与特定原始记忆关联的梦境"""
    cursor.execute("""
        SELECT * FROM dream_fragments 
        WHERE associated_raw_ids LIKE ?
    """, (f'%"{raw_ids[0]}"%',))
```

### 7.3 情绪共振查询
```python
def get_dreams_by_emotion(self, target_emotion: float, tolerance: float = 0.3):
    """按情绪共振查询梦境"""
    cursor.execute("""
        SELECT * FROM dream_fragments 
        WHERE ABS(emotional_residue - ?) < ?
        AND current_weight > 0.05
    """, (target_emotion, tolerance))
```

---

## 8. IMA 备份策略

### 8.1 备份内容
```
alice 知识库新增：
- newbrain_memory_backup.sql    — SQLite 数据库导出（Base64）
- newbrain_memory_summary.md    — 可读摘要
- reconstructed_level3.md       — 人格核心（最重要）
- beliefs_snapshot.md           — 信念锚点快照
- dream_log.md                  — 梦境日志（可读）
```

### 8.2 备份频率
- **实时**：beliefs 变更时立即备份
- **每日**：凌晨 3:00 全量备份（重构后）
- **手动**：用户命令 `/backup`

### 8.3 恢复流程
```python
def restore_from_ima():
    # 1. 从 alice 下载 newbrain_memory_backup.sql
    # 2. Base64 解码
    # 3. sqlite3 导入
    # 4. 验证 beliefs 完整性
    # 5. 验证 reconstructed Level 3 存在
```

---

## 9. 迁移计划

### Phase 1: 基础设施（今天）
- [x] 创建 `brain/memory_db.py` — SQLite 封装
- [ ] 修改 `ColdMemory` 类 — 接入 SQLite
- [ ] 保持 `save/load` 接口，内部用 `db`

### Phase 2: 递归重构（明天）
- [ ] 实现 `Reconstructor` 类
- [ ] 集成小模型压缩接口
- [ ] 实现 Level 1/2/3 重构流程
- [ ] 定时任务（cron/heartbeat）

### Phase 3: 增强查询（后天）
- [ ] TPN 接入梦境影响
- [ ] 模糊回忆重构
- [ ] 情绪共振查询

### Phase 4: 备份恢复
- [ ] IMA 备份接口
- [ ] 自动备份 cron
- [ ] 恢复验证

---

## 10. 测试计划

### 10.1 单元测试
```python
# test_memory_db.py

def test_raw_memory_crud():
    db = MemoryDatabase(':memory:')
    id = db.add_raw_memory("测试", "user", 0.5)
    assert id > 0
    rows = db.get_recent_raw(1)
    assert rows[0]['content'] == "测试"

def test_dream_decay():
    db = MemoryDatabase(':memory:')
    id = db.add_dream_fragment("梦", ["场景"], current_weight=0.2)
    db.update_dream_weight(id, 0.1)
    dreams = db.get_active_dreams(min_weight=0.15)
    assert len(dreams) == 0

def test_reconstruction_hierarchy():
    db = MemoryDatabase(':memory:')
    # 存 Level 1
    db.add_reconstructed("周摘要", [1,2], "主题", 1)
    # 存 Level 3
    db.add_reconstructed("人格核心", [10], "身份", 3)
    # 查询
    l1 = db.get_reconstructed_by_level(1)
    l3 = db.get_reconstructed_by_level(3)
    assert len(l1) == 1
    assert len(l3) == 1
```

### 10.2 集成测试
```bash
# 完整链路测试
python3 main.py --test-sqlite
```

---

## 11. 性能预估

| 指标 | JSON (旧) | SQLite (新) |
|---|---|---|
| 容量 | ~1000条卡顿 | 100万条流畅 |
| 查询 | O(n) 遍历 | O(1) 索引 |
| 启动加载 | 全量加载，2秒 | 懒加载，0.1秒 |
| 写入 | 写整个文件 | 单行插入 |
| 并发 | 不支持 | SQLite WAL 模式支持读并发 |
| 备份 | 复制整个文件 | SQL 导出/增量 |

---

## 12. 风险与缓解

| 风险 | 缓解 |
|---|---|
| SQLite 文件损坏 | WAL 模式 + 定期备份到 IMA |
| 小模型重构失败 | 回退到规则摘要，标记 "manual" |
| 重构后信息丢失 | 保留 source_ids，可追溯到原始记录 |
| 隐私泄露 | private_identity.yaml 不提交，不写入 beliefs |
| 递归无限增长 | 限制 Level 3 只保留最新1条，旧记录归档 |

---

## 附录 A: SQL 查询示例

### 查询最近一周的主题分布
```sql
SELECT 
    tags,
    COUNT(*) as count,
    AVG(emotion) as avg_emotion
FROM raw_memories 
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY tags
ORDER BY count DESC;
```

### 查询与"老公"相关的所有记忆
```sql
SELECT * FROM raw_memories 
WHERE content LIKE '%老公%'
ORDER BY timestamp DESC;
```

### 查询活跃梦境的总情绪影响
```sql
SELECT 
    SUM(current_weight * emotional_residue) as total_influence,
    COUNT(*) as dream_count
FROM dream_fragments 
WHERE current_weight > 0.05;
```

---

*设计日期：2026-04-24*  
*版本：v0.3 SQLite 冷记忆架构*  
*作者：Kimi Claw + 老公*
