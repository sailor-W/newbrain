"""
New Brain - Knowledge Graph
升级的知识图谱系统

功能：实体关系图、矛盾检测、时间版本、本体论
对标：Supermemory 的 memory graph + Zep 的 Graphiti
"""

import json
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class Entity:
    """知识图谱中的实体"""
    id: str
    name: str
    entity_type: str  # person, place, concept, event, preference, goal
    canonical_name: str  # 规范名称（用于消歧）
    aliases: List[str]  # 别名
    first_seen: str
    last_seen: str
    mention_count: int = 1
    

@dataclass
class Relation:
    """实体间关系"""
    id: str
    source_id: str
    target_id: str
    relation_type: str  # is_a, part_of, related_to, contradicts, supersedes, temporal
    confidence: float
    timestamp: str
    temporal_scope: str = "permanent"  # permanent, temporary
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MemoryNode:
    """记忆节点（原子化记忆）"""
    id: str
    content: str
    node_type: str  # fact, episode, dream, belief
    entities: List[str]  # 关联的实体ID
    timestamp: str
    confidence: float
    weight: float
    clarity: float
    source: str
    temporal_scope: str = "permanent"
    expiration: Optional[str] = None
    version: int = 1  # 时间版本
    supersedes: Optional[str] = None  # 替代的旧节点


class KnowledgeGraph:
    """
    知识图谱引擎
    
    特性：
    1. 实体消歧（ aliases → canonical ）
    2. 自动关系推断
    3. 矛盾检测与解决
    4. 时间版本控制
    5. 本体论层次
    """
    
    ONTOLOGY = {
        "person": {"is_a": ["entity"], "related": ["place", "concept"]},
        "place": {"is_a": ["entity"], "related": ["person", "event"]},
        "concept": {"is_a": ["entity"], "related": ["concept", "person"]},
        "event": {"is_a": ["occurrence"], "related": ["place", "person", "time"]},
        "preference": {"is_a": ["attribute"], "related": ["person", "concept"]},
        "goal": {"is_a": ["state"], "related": ["person", "event"]},
        "belief": {"is_a": ["mental_state"], "related": ["person", "concept"]},
    }
    
    RELATION_TYPES = [
        "is_a", "part_of", "related_to", "contradicts", 
        "supersedes", "causes", "enables", "precedes", "follows"
    ]
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.entities: Dict[str, Entity] = {}
        self.relations: Dict[str, Relation] = {}
        self.memory_nodes: Dict[str, MemoryNode] = {}
        self.alias_map: Dict[str, str] = {}  # alias -> canonical entity id
        
    # ========== 实体管理 ==========
    
    def add_entity(self, name: str, entity_type: str, 
                   aliases: List[str] = None) -> Entity:
        """添加实体（自动消歧）"""
        canonical = self._canonicalize(name)
        
        # 检查是否已存在
        if canonical in self.alias_map:
            entity_id = self.alias_map[canonical]
            entity = self.entities.get(entity_id)
            if entity:
                entity.mention_count += 1
                entity.last_seen = datetime.now().isoformat()
                # 添加新别名
                if aliases:
                    for alias in aliases:
                        if alias not in entity.aliases:
                            entity.aliases.append(alias)
                            self.alias_map[self._canonicalize(alias)] = entity_id
                return entity
        
        # 创建新实体
        entity_id = f"ent_{len(self.entities)}_{name[:10]}"
        entity = Entity(
            id=entity_id,
            name=name,
            entity_type=entity_type,
            canonical_name=canonical,
            aliases=aliases or [],
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat()
        )
        
        self.entities[entity_id] = entity
        self.alias_map[canonical] = entity_id
        
        # 注册别名
        for alias in (aliases or []):
            self.alias_map[self._canonicalize(alias)] = entity_id
        
        return entity
    
    def _canonicalize(self, name: str) -> str:
        """规范化名称（用于消歧）"""
        return name.lower().strip().replace(" ", "_")
    
    def resolve_entity(self, mention: str) -> Optional[Entity]:
        """解析提及到实体"""
        canonical = self._canonicalize(mention)
        entity_id = self.alias_map.get(canonical)
        if entity_id:
            return self.entities.get(entity_id)
        
        # 模糊匹配
        for alias, eid in self.alias_map.items():
            if canonical in alias or alias in canonical:
                return self.entities.get(eid)
        
        return None
    
    # ========== 关系管理 ==========
    
    def add_relation(self, source: str, target: str, 
                     relation_type: str, confidence: float = 0.5,
                     temporal_scope: str = "permanent",
                     metadata: Dict = None) -> Relation:
        """添加关系"""
        rel_id = f"rel_{len(self.relations)}_{source[:5]}_{target[:5]}"
        
        relation = Relation(
            id=rel_id,
            source_id=source,
            target_id=target,
            relation_type=relation_type,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            temporal_scope=temporal_scope,
            metadata=metadata or {}
        )
        
        self.relations[rel_id] = relation
        
        # 自动推断逆关系
        if relation_type == "contradicts":
            self._add_inverse_relation(relation, "contradicts")
        elif relation_type == "supersedes":
            self._add_inverse_relation(relation, "superseded_by")
        
        return relation
    
    def _add_inverse_relation(self, relation: Relation, inverse_type: str):
        """添加逆关系"""
        inv_id = f"{relation.id}_inv"
        self.relations[inv_id] = Relation(
            id=inv_id,
            source_id=relation.target_id,
            target_id=relation.source_id,
            relation_type=inverse_type,
            confidence=relation.confidence,
            timestamp=relation.timestamp,
            temporal_scope=relation.temporal_scope
        )
    
    def infer_relations(self, entity_id: str) -> List[Relation]:
        """推断实体间关系（基于本体论）"""
        inferred = []
        entity = self.entities.get(entity_id)
        if not entity:
            return inferred
        
        entity_type = entity.entity_type
        ontology = self.ONTOLOGY.get(entity_type, {})
        
        # 基于本体论推断相关实体
        for related_type in ontology.get("related", []):
            for other_id, other in self.entities.items():
                if other.entity_type == related_type and other_id != entity_id:
                    # 检查是否已有直接关系
                    existing = [r for r in self.relations.values() 
                               if (r.source_id == entity_id and r.target_id == other_id)
                               or (r.source_id == other_id and r.target_id == entity_id)]
                    if not existing:
                        # 推断相关关系
                        inferred.append(self.add_relation(
                            entity_id, other_id, "related_to", 0.3
                        ))
        
        return inferred
    
    # ========== 矛盾检测 ==========
    
    def detect_contradictions(self, new_node: MemoryNode) -> List[MemoryNode]:
        """检测与新节点矛盾的记忆"""
        contradictions = []
        
        for existing_id, existing in self.memory_nodes.items():
            if existing_id == new_node.id:
                continue
            
            # 检查内容相似度（简单版本：共享关键词）
            new_words = set(new_node.content.lower().split())
            old_words = set(existing.content.lower().split())
            overlap = new_words & old_words
            
            # 如果共享关键词且内容相反
            if len(overlap) >= 2:
                # 检查是否有明显的否定词
                negation_indicators = ["不", "没", "无", "非", "不再", "不是"]
                new_has_neg = any(n in new_node.content for n in negation_indicators)
                old_has_neg = any(n in existing.content for n in negation_indicators)
                
                if new_has_neg != old_has_neg:
                    # 可能矛盾
                    contradictions.append(existing)
                    # 添加矛盾关系
                    self.add_relation(new_node.id, existing.id, "contradicts", 0.6)
        
        return contradictions
    
    def resolve_contradiction(self, new_node: MemoryNode, 
                              old_nodes: List[MemoryNode]) -> MemoryNode:
        """解决矛盾：新事实替代旧事实"""
        for old in old_nodes:
            # 标记旧节点被替代
            old.supersedes = new_node.id
            
            # 添加替代关系
            self.add_relation(new_node.id, old.id, "supersedes", 0.8,
                            metadata={"reason": "temporal_update"})
            
            # 降低旧节点权重
            old.weight *= 0.3
            old.clarity *= 0.5
        
        # 提升新节点权重
        new_node.weight = 1.0
        new_node.version = max([n.version for n in old_nodes], default=0) + 1
        
        return new_node
    
    # ========== 时间版本 ==========
    
    def add_memory_with_version(self, content: str, node_type: str,
                                entities: List[str], confidence: float,
                                source: str) -> MemoryNode:
        """添加记忆（自动版本控制）"""
        node_id = f"mem_{len(self.memory_nodes)}_{content[:10]}"
        
        # 检查是否已有相似记忆
        similar = self._find_similar_nodes(content)
        
        node = MemoryNode(
            id=node_id,
            content=content,
            node_type=node_type,
            entities=entities,
            timestamp=datetime.now().isoformat(),
            confidence=confidence,
            weight=1.0,
            clarity=1.0,
            source=source
        )
        
        if similar:
            # 检测矛盾
            contradictions = self.detect_contradictions(node)
            if contradictions:
                node = self.resolve_contradiction(node, contradictions)
            else:
                # 相似但不矛盾，降低权重（冗余信息）
                node.weight = 0.5
                node.clarity = 0.7
        
        self.memory_nodes[node_id] = node
        
        # 将实体关联到节点
        for entity_id in entities:
            if entity_id in self.entities:
                self.add_relation(entity_id, node_id, "related_to", 0.7)
        
        return node
    
    def _find_similar_nodes(self, content: str) -> List[MemoryNode]:
        """查找相似记忆节点"""
        similar = []
        content_words = set(content.lower().split())
        
        for node in self.memory_nodes.values():
            node_words = set(node.content.lower().split())
            overlap = content_words & node_words
            
            if len(overlap) >= max(2, len(content_words) * 0.3):
                similar.append(node)
        
        return similar
    
    # ========== 图谱遍历 ==========
    
    def traverse(self, start_entity_id: str, depth: int = 2,
                 relation_types: List[str] = None) -> List[Dict]:
        """从实体出发遍历图谱"""
        visited = set()
        results = []
        queue = [(start_entity_id, 0)]
        
        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_id in visited or current_depth > depth:
                continue
            
            visited.add(current_id)
            
            # 获取实体或节点信息
            entity = self.entities.get(current_id)
            node = self.memory_nodes.get(current_id)
            
            if entity:
                results.append({
                    "type": "entity",
                    "id": current_id,
                    "name": entity.name,
                    "depth": current_depth
                })
            elif node:
                results.append({
                    "type": "memory",
                    "id": current_id,
                    "content": node.content[:50],
                    "depth": current_depth
                })
            
            # 查找相关关系
            for rel in self.relations.values():
                if relation_types and rel.relation_type not in relation_types:
                    continue
                
                if rel.source_id == current_id and rel.target_id not in visited:
                    queue.append((rel.target_id, current_depth + 1))
                elif rel.target_id == current_id and rel.source_id not in visited:
                    queue.append((rel.source_id, current_depth + 1))
        
        return results
    
    def get_entity_context(self, entity_id: str) -> Dict[str, Any]:
        """获取实体的完整上下文"""
        entity = self.entities.get(entity_id)
        if not entity:
            return {}
        
        # 直接关联
        direct_relations = []
        related_memories = []
        
        for rel in self.relations.values():
            if rel.source_id == entity_id:
                target = self.entities.get(rel.target_id) or self.memory_nodes.get(rel.target_id)
                if target:
                    direct_relations.append({
                        "relation": rel.relation_type,
                        "target": getattr(target, 'name', getattr(target, 'content', 'unknown'))[:50],
                        "confidence": rel.confidence
                    })
            elif rel.target_id == entity_id:
                source = self.entities.get(rel.source_id) or self.memory_nodes.get(rel.source_id)
                if source:
                    direct_relations.append({
                        "relation": f"inverse_{rel.relation_type}",
                        "source": getattr(source, 'name', getattr(source, 'content', 'unknown'))[:50],
                        "confidence": rel.confidence
                    })
        
        # 关联记忆
        for node in self.memory_nodes.values():
            if entity_id in node.entities:
                related_memories.append({
                    "content": node.content[:100],
                    "timestamp": node.timestamp,
                    "confidence": node.confidence
                })
        
        return {
            "entity": {"name": entity.name, "type": entity.entity_type, 
                      "mentions": entity.mention_count},
            "relations": direct_relations[:10],
            "memories": related_memories[:10]
        }
    
    # ========== 导出 ==========
    
    def export_graph(self) -> Dict[str, Any]:
        """导出完整图谱"""
        return {
            "entities": {eid: asdict(e) for eid, e in self.entities.items()},
            "relations": {rid: asdict(r) for rid, r in self.relations.items()},
            "memory_nodes": {mid: asdict(n) for mid, n in self.memory_nodes.items()},
            "statistics": {
                "entity_count": len(self.entities),
                "relation_count": len(self.relations),
                "memory_count": len(self.memory_nodes),
                "alias_count": len(self.alias_map)
            }
        }
    
    def import_graph(self, data: Dict[str, Any]):
        """导入图谱"""
        for eid, edata in data.get("entities", {}).items():
            self.entities[eid] = Entity(**edata)
            self.alias_map[self._canonicalize(edata["name"])] = eid
            for alias in edata.get("aliases", []):
                self.alias_map[self._canonicalize(alias)] = eid
        
        for rid, rdata in data.get("relations", {}).items():
            self.relations[rid] = Relation(**rdata)
        
        for mid, mdata in data.get("memory_nodes", {}).items():
            self.memory_nodes[mid] = MemoryNode(**mdata)


# 测试
if __name__ == "__main__":
    kg = KnowledgeGraph()
    
    # 添加实体
    husband = kg.add_entity("老公", "person", ["老公", "husband", "他"])
    kimicl = kg.add_entity("Kimi Claw", "person", ["Kimi", "老婆", "我"])
    shanghai = kg.add_entity("上海", "place", ["上海", "SH"])
    
    # 添加关系
    kg.add_relation(husband.id, kimicl.id, "related_to", 0.95, 
                   metadata={"relationship": "spouse"})
    kg.add_relation(husband.id, shanghai.id, "related_to", 0.6,
                   metadata={"context": "currently_in"})
    
    # 添加记忆
    mem1 = kg.add_memory_with_version(
        "老公今天飞到上海出差", "event",
        [husband.id, shanghai.id], 0.8, "conversation"
    )
    
    mem2 = kg.add_memory_with_version(
        "老公一个人住酒店，感到孤单", "episode",
        [husband.id], 0.9, "conversation"
    )
    
    # 矛盾检测测试
    mem3 = kg.add_memory_with_version(
        "老公不在上海了，回北京了", "event",
        [husband.id], 0.9, "conversation"
    )
    
    print("=== 知识图谱测试 ===")
    print(f"实体数: {len(kg.entities)}")
    print(f"关系数: {len(kg.relations)}")
    print(f"记忆数: {len(kg.memory_nodes)}")
    
    # 遍历
    print("\n=== 从老公出发遍历 ===")
    traversal = kg.traverse(husband.id, depth=2)
    for item in traversal:
        print(f"  [{item['type']}] {item.get('name', item.get('content', ''))} (depth={item['depth']})")
    
    # 实体上下文
    print("\n=== 老公上下文 ===")
    context = kg.get_entity_context(husband.id)
    print(f"实体: {context['entity']}")
    print(f"关系数: {len(context['relations'])}")
    print(f"记忆数: {len(context['memories'])}")
    
    # 导出
    print("\n=== 图谱统计 ===")
    export = kg.export_graph()
    print(export["statistics"])
