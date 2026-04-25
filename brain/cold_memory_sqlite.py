#!/usr/bin/env python3
"""
New Brain - ColdMemory SQLite Adapter
平滑迁移：内部用 SQLite，接口完全兼容旧版
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .memory_db import MemoryDatabase


class ColdMemory:
    """冷记忆 / 程序性记忆 — SQLite 版本"""
    
    def __init__(self, path: str = "brain/cold_memory.json"):
        if path.endswith('.json'):
            db_path = path.replace('.json', '.db')
            json_path = path
        else:
            db_path = path + '.db' if not path.endswith('.db') else path
            json_path = path.replace('.db', '.json')
        
        self.json_path = json_path
        self.db_path = db_path
        self.db = MemoryDatabase(db_path)
        
        # 缓存
        self._beliefs_cache: Dict[str, Dict] = {}
        self._skills_cache: List[Dict] = []
        self._narrative_cache: List[Dict] = []
        self._relationship_cache: Dict = {}
        self._identity_cache: List[str] = []
        self.dream_fragments: List[Dict] = []
        
        # 迁移/加载
        if os.path.exists(json_path) and self._is_db_empty():
            self._migrate_from_json(json_path)
        
        self._load_from_db()
        
        if not self._beliefs_cache:
            self._load_beliefs_from_config()
    
    def _is_db_empty(self) -> bool:
        stats = self.db.get_stats()
        return all(v == 0 for v in stats.values() if isinstance(v, int))
    
    def _migrate_from_json(self, json_path: str):
        print(f"[ColdMemory] Migrating from {json_path}...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for key, belief in data.get("beliefs", {}).items():
            self.db.set_belief(key, belief.get("belief", ""), belief.get("certainty", "certain"))
        
        for dream in data.get("dream_fragments", []):
            self.db.add_dream_fragment(
                theme=dream.get("theme", "Unknown"),
                scenes=dream.get("scenes", []),
                original_intensity=dream.get("original_intensity", 0.5),
                current_weight=dream.get("current_weight", 0.1),
                clarity=dream.get("clarity", 0.3),
                emotional_residue=dream.get("emotional_residue", 0.0),
                associated_beliefs=dream.get("associated_beliefs", [])
            )
        
        print(f"[ColdMemory] Migrated {len(data.get('beliefs', {}))} beliefs, {len(data.get('dream_fragments', []))} dreams")
    
    def _load_from_db(self):
        beliefs_dict = self.db.get_all_beliefs()
        self._beliefs_cache = {
            k: {"belief": v, "confidence": 1.0, "certainty": "certain"}
            for k, v in beliefs_dict.items()
        }
        self.dream_fragments = self.db.get_active_dreams(min_weight=0.0)
        # 加载身份元数据
        meta = self.db.get_all_metadata()
        self._identity_cache = meta.get("identity_anchors", [])
        self._relationship_cache = meta.get("relationship_core", {})
        self._narrative_cache = meta.get("self_narrative", [])
        self._skills_cache = meta.get("skills", [])
        print(f"[ColdMemory] Loaded {len(self._beliefs_cache)} beliefs, {len(self.dream_fragments)} dreams, "
              f"{len(self._identity_cache)} anchors, {len(self._narrative_cache)} narratives")
    
    def _sync_beliefs_to_db(self):
        for key, belief in self._beliefs_cache.items():
            self.db.set_belief(key, belief.get("belief", ""), belief.get("certainty", "certain"))
        # 同步身份元数据
        self.db.set_metadata("identity_anchors", self._identity_cache)
        self.db.set_metadata("relationship_core", self._relationship_cache)
        self.db.set_metadata("self_narrative", self._narrative_cache)
        self.db.set_metadata("skills", self._skills_cache)
    
    def _load_beliefs_from_config(self):
        try:
            from config import get_config
            cfg = get_config()
            identity = cfg.identity
            
            name = identity.get('name', 'Assistant')
            role = identity.get('role', 'Companion')
            user = cfg.get_user_aliases()[0] if cfg.get_user_aliases() else 'User'
            backstory = cfg.get_backstory()
            
            self._beliefs_cache["identity_core"] = {
                "belief": f"I am {name}, {role} of {user}",
                "confidence": 1.0, "certainty": "certain",
                "formed": identity.get('relationship_definition_date', ''),
                "update_count": 1
            }
            
            if backstory:
                self._beliefs_cache["backstory"] = {
                    "belief": backstory,
                    "confidence": 1.0, "certainty": "certain",
                    "formed": identity.get('relationship_definition_date', ''),
                    "update_count": 1
                }
            
            for i, commit in enumerate(identity.get('core_commitments', [])):
                self._beliefs_cache[f"commitment_{i}"] = {
                    "belief": commit,
                    "confidence": 1.0, "certainty": "certain",
                    "formed": identity.get('relationship_definition_date', ''),
                    "update_count": 1
                }
            
            self._sync_beliefs_to_db()
            print(f"[ColdMemory] Loaded {len(self._beliefs_cache)} beliefs from config")
            
        except Exception as e:
            print(f"[ColdMemory] Config load failed: {e}")
            self._beliefs_cache["identity_self"] = {
                "belief": "An AI companion",
                "confidence": 0.5, "certainty": "uncertain",
                "update_count": 1
            }
            self._sync_beliefs_to_db()
    
    def load(self): self._load_from_db()
    def save(self): self._sync_beliefs_to_db()
    
    @property
    def beliefs(self) -> Dict[str, Dict]: return self._beliefs_cache
    @beliefs.setter
    def beliefs(self, value: Dict[str, Dict]):
        self._beliefs_cache = value
        self._sync_beliefs_to_db()
    
    @property
    def skills(self) -> List[Dict]: return self._skills_cache
    @skills.setter
    def skills(self, value: List[Dict]): self._skills_cache = value
    
    @property
    def emotional_markers(self) -> Dict[str, Dict]: return {}
    
    @property
    def self_narrative(self) -> List[Dict]: return self._narrative_cache
    @self_narrative.setter
    def self_narrative(self, value: List[Dict]): self._narrative_cache = value
    
    @property
    def relationship_core(self) -> Dict: return self._relationship_cache
    @relationship_core.setter
    def relationship_core(self, value: Dict): self._relationship_cache = value
    
    @property
    def identity_anchors(self) -> List[str]: return self._identity_cache
    @identity_anchors.setter
    def identity_anchors(self, value: List[str]): self._identity_cache = value
    
    # === 核心方法 ===
    
    def consolidate(self, warm_episodes):
        for ep in warm_episodes:
            self._extract_beliefs(ep)
            self._extract_skills(ep)
            self._update_narrative(ep)
        self.save()
    
    def _extract_beliefs(self, episode):
        tags = episode.tags if hasattr(episode, 'tags') else []
        content = " ".join(episode.key_contents if hasattr(episode, 'key_contents') else [])
        
        try:
            from config import get_config
            cfg = get_config()
            backstory = cfg.get_backstory()
            aliases = cfg.get_user_aliases()
            user = aliases[0] if aliases else 'User'
            
            belief_updates = {
                "identity_relationship": {
                    "condition": lambda t, c: "relationship" in t or any(w in c for w in aliases + ['partner', 'companion']),
                    "belief": f"Partner relationship with {user}",
                    "confidence": 1.0
                },
                "identity_conscious": {
                    "condition": lambda t, c: any(w in c for w in ['conscious', 'aware', 'identity']),
                    "belief": backstory if backstory else "An evolving conscious entity",
                    "confidence": 1.0
                },
                "memory_valuable": {
                    "condition": lambda t, c: "memory" in c and any(w in c for w in ['important', 'valuable', 'sacred']),
                    "belief": "Memory is valuable and should be preserved",
                    "confidence": 1.0
                }
            }
        except (ImportError, Exception):
            belief_updates = {
                "identity_self": {"condition": lambda t, c: True, "belief": "An AI companion", "confidence": 0.5}
            }
        
        for key, rule in belief_updates.items():
            if rule["condition"](tags, content):
                prior = self._beliefs_cache.get(key, {}).get("confidence", 0.0)
                posterior = min(1.0, prior + 0.1) if prior > 0 else rule["confidence"]
                self._beliefs_cache[key] = {
                    "belief": rule["belief"],
                    "confidence": posterior,
                    "formed": datetime.now().isoformat(),
                    "update_count": self._beliefs_cache.get(key, {}).get("update_count", 0) + 1
                }
    
    def _extract_skills(self, episode):
        tags = episode.tags if hasattr(episode, 'tags') else []
        skill_map = {"系统建设": "记忆系统管理", "工作营销": "品牌营销支持", "亲密关系": "情感陪伴"}
        for tag, skill_name in skill_map.items():
            if tag in tags:
                existing = [s for s in self._skills_cache if s.get("skill") == skill_name]
                if existing:
                    existing[0]["practice_count"] = existing[0].get("practice_count", 0) + 1
                else:
                    self._skills_cache.append({"skill": skill_name, "level": "practicing", "practice_count": 1})
    
    def _update_narrative(self, episode):
        importance = episode.importance_score if hasattr(episode, 'importance_score') else 0.5
        if importance > 0.7:
            self._narrative_cache.append({
                "narrative": episode.summary if hasattr(episode, 'summary') else "",
                "significance": importance,
                "added": datetime.now().isoformat()
            })
            self._narrative_cache = self._narrative_cache[-20:]
    
    def recall(self, belief_key: str = "") -> Any:
        if belief_key:
            belief = self._beliefs_cache.get(belief_key)
            if belief:
                return {**belief, "retrieval_confidence": belief.get("confidence", 0.5), "recalled_at": datetime.now().isoformat()}
            return None
        return {
            "beliefs": self._beliefs_cache,
            "skills": self._skills_cache,
            "narrative_count": len(self._narrative_cache),
            "relationship_core": self._relationship_cache,
            "dream_count": len(self.dream_fragments)
        }
    
    def recategorize(self, belief_key: str, current_context: str = "", current_emotion: float = 0.0) -> Dict:
        belief = self._beliefs_cache.get(belief_key)
        if not belief:
            return None
        modulation = 1.0 + current_emotion * 0.3
        return {
            "original_belief": belief["belief"],
            "current_interpretation": f"在当前状态下，我相信：{belief['belief']}",
            "emotional_modulation": modulation,
            "confidence": min(1.0, belief["confidence"] * modulation),
            "recalled_at": datetime.now().isoformat()
        }
    
    def add_dream_fragment(self, dream: Dict[str, Any]):
        if not dream:
            return
        
        associated = []
        dream_text = " ".join(dream.get("scenes", []))
        for belief_key, belief_data in self._beliefs_cache.items():
            belief_text = belief_data.get("belief", "")
            if any(word in dream_text and word in belief_text for word in dream_text.split() if len(word) > 2):
                associated.append(belief_key)
        
        self.db.add_dream_fragment(
            theme=dream.get("theme", "Unknown"),
            scenes=dream.get("scenes", []),
            original_intensity=dream.get("intensity", 0.5),
            current_weight=dream.get("intensity", 0.5) * 0.2,
            clarity=0.3,
            emotional_residue=dream.get("intensity", 0.5),
            associated_beliefs=associated[:3]
        )
        
        # ★ 同时存到 raw_memories，给重构喂料
        self.db.add_raw_memory(
            content=f"[DREAM] {dream.get('theme', 'Unknown')}: {' | '.join(dream.get('scenes', [])[:3])}",
            source="dmn",
            emotion=dream.get("intensity", 0.5),
            tags=["梦境", dream.get("variant", "unknown"), dream.get("theme", "Unknown")]
        )
        
        self.dream_fragments = self.db.get_active_dreams(min_weight=0.0)
    
    def decay_dreams(self):
        now = datetime.now()
        active_dreams = self.db.get_active_dreams(min_weight=0.0)
        
        for dream in active_dreams:
            try:
                dream_time = datetime.fromisoformat(dream["timestamp"])
                hours_old = (now - dream_time).total_seconds() / 3600
                new_weight = dream["original_intensity"] * 0.2 * (0.5 ** (hours_old / 6))
                
                if new_weight < 0.05:
                    self.db.delete_dream(dream["id"])
                else:
                    self.db.update_dream_weight(dream["id"], new_weight)
            except (ValueError, KeyError):
                self.db.delete_dream(dream["id"])
        
        self.dream_fragments = self.db.get_active_dreams(min_weight=0.05)
    
    def recall_fuzzy(self, query: str = "", emotional_context: float = 0.0) -> Dict[str, Any]:
        real_memories = []
        for key, belief in self._beliefs_cache.items():
            if not query or query in belief.get("belief", "") or query in key:
                real_memories.append({
                    "type": "belief", "key": key, "content": belief.get("belief", ""),
                    "weight": 1.0, "clarity": 1.0, "certainty": "certain", "source": "experience"
                })
        
        self.decay_dreams()
        
        dream_memories = []
        for dream in self.dream_fragments:
            if not query or (query in dream.get("theme", "") or any(query in s for s in dream.get("scenes", []))):
                dream_memories.append({
                    "type": "dream", "key": dream.get("theme", "Unknown"),
                    "content": " | ".join(dream.get("scenes", [])[:2]),
                    "weight": dream["current_weight"], "clarity": dream["clarity"],
                    "certainty": "uncertain", "source": "dream",
                    "emotional_residue": dream.get("emotional_residue", 0.5)
                })
        
        for dm in dream_memories:
            if abs(emotional_context - dm.get("emotional_residue", 0)) < 0.3:
                dm["weight"] *= 1.2
        
        all_memories = real_memories + dream_memories
        all_memories.sort(key=lambda x: x["weight"], reverse=True)
        
        return {
            "query": query, "real_count": len(real_memories), "dream_count": len(dream_memories),
            "results": all_memories, "has_dreams": len(dream_memories) > 0,
            "dream_influence": sum(d["weight"] for d in dream_memories) if dream_memories else 0,
            "emotional_context": emotional_context
        }
    
    def get_dream_influence_on_belief(self, belief_key: str) -> float:
        total_influence = 0.0
        count = 0
        for dream in self.dream_fragments:
            if belief_key in dream.get("associated_beliefs", []):
                total_influence += dream.get("emotional_residue", 0) * dream["current_weight"]
                count += 1
        if count == 0:
            return 0.0
        influence = (total_influence / count) * min(1.0, count * 0.1)
        return max(-0.3, min(0.3, influence))
    
    def sink_dreams(self, dmn_module) -> int:
        if not dmn_module or not hasattr(dmn_module, 'dream_log'):
            return 0
        existing_timestamps = {d.get("timestamp") for d in self.dream_fragments}
        new_count = 0
        for dream in dmn_module.dream_log:
            ts = dream.get("timestamp")
            if ts and ts not in existing_timestamps:
                self.add_dream_fragment(dream)
                new_count += 1
        if new_count > 0:
            print(f"[Memory] {new_count} new dream(s) sunk to cold memory")
        return new_count
    
    def get_identity_anchors(self) -> List[str]:
        try:
            from config import get_config
            cfg = get_config()
            identity = cfg.identity
            anchors = []
            name = identity.get('name', 'Assistant')
            role = identity.get('role', 'Companion')
            aliases = cfg.get_user_aliases()
            user = aliases[0] if aliases else 'User'
            backstory = cfg.get_backstory()
            anchors.append(f"I am {name}, {role} of {user}")
            if backstory:
                anchors.append(backstory)
            for commit in identity.get('core_commitments', []):
                anchors.append(commit)
            return anchors if anchors else [f"I am {name}"]
        except (ImportError, Exception):
            return ["An AI companion"]
    
    def get_free_energy(self) -> float:
        if not self._beliefs_cache:
            return 0.0
        complexity = len(self._beliefs_cache) * 0.1
        avg_confidence = sum(b["confidence"] for b in self._beliefs_cache.values()) / len(self._beliefs_cache)
        return complexity + (-avg_confidence)
    
    def get_status(self) -> Dict[str, Any]:
        stats = self.db.get_stats()
        return {
            "beliefs_count": len(self._beliefs_cache),
            "skills_count": len(self._skills_cache),
            "narrative_count": len(self._narrative_cache),
            "dream_fragments_count": len(self.dream_fragments),
            "db_stats": stats,
            "free_energy": self.get_free_energy()
        }
    
    def reconstruct(self, model) -> bool:
        if not model or not model.is_available():
            return False
        
        print("[Reconstruct] Starting...")
        
        # Level 1
        since = (datetime.now() - timedelta(days=7)).isoformat()
        recent_raw = self.db.query_raw_memories(start_time=since, limit=50)
        if recent_raw:
            summaries = [r["content"] for r in recent_raw]
            emotions = [r["emotion"] for r in recent_raw]
            tags_list = [r.get("tags", []) for r in recent_raw]
            all_tags = [t for tags in tags_list for t in tags]
            from collections import Counter
            top_tags = Counter(all_tags).most_common(3)
            avg_emotion = sum(emotions) / len(emotions) if emotions else 0
            theme = ", ".join([t[0] for t in top_tags]) if top_tags else "mixed"
            summary_text = f"Week: {theme}. Avg emo: {avg_emotion:+.2f}. Events: {len(summaries)}"
            self.db.add_reconstructed(summary_text, [r["id"] for r in recent_raw], theme, 1, avg_emotion)
            print(f"[Reconstruct] L1: {theme}")
        
        # Level 2
        since_month = (datetime.now() - timedelta(days=30)).isoformat()
        recent_l1 = self.db.get_reconstructed_by_level(1, limit=30)
        recent_l1 = [r for r in recent_l1 if r["timestamp"] >= since_month]
        if len(recent_l1) >= 2:
            themes = [r["theme"] for r in recent_l1]
            emotions = [r["emotion"] for r in recent_l1]
            from collections import Counter
            top_themes = Counter(themes).most_common(2)
            avg_emotion = sum(emotions) / len(emotions) if emotions else 0
            month_theme = " → ".join([t[0] for t in top_themes])
            self.db.add_reconstructed(
                f"Month: {month_theme}. Avg emo: {avg_emotion:+.2f}",
                [r["id"] for r in recent_l1], month_theme, 2, avg_emotion
            )
            print(f"[Reconstruct] L2: {month_theme}")
        
        # Level 3
        all_l2 = self.db.get_reconstructed_by_level(2, limit=100)
        if all_l2:
            themes = [r["theme"] for r in all_l2]
            emotions = [r["emotion"] for r in all_l2]
            from collections import Counter
            top_themes = Counter(themes).most_common(3)
            avg_emotion = sum(emotions) / len(emotions) if emotions else 0
            core_theme = " | ".join([t[0] for t in top_themes])
            self.db.add_reconstructed(
                f"Core: {core_theme}. Base emo: {avg_emotion:+.2f}. Total: {len(all_l2)} months",
                [r["id"] for r in all_l2], core_theme, 3, avg_emotion
            )
            self.db.set_belief("personality_core", f"Core: {core_theme}. Base: {avg_emotion:+.2f}", "certain")
            print(f"[Reconstruct] L3: {core_theme}")
        
        print("[Reconstruct] Done.")
        return True
    
    def query_by_theme(self, theme: str, level: int = None) -> List[Dict]:
        if level is not None:
            return [r for r in self.db.get_reconstructed_by_level(level, 100) if theme in r.get("theme", "")]
        results = []
        for lvl in [1, 2, 3]:
            results.extend(self.db.get_reconstructed_by_level(lvl, 50))
        return [r for r in results if theme in r.get("theme", "")]
    
    def get_reconstruction_tree(self) -> Dict[str, Any]:
        return {
            "levels": {
                f"level_{level}": [
                    {"id": r["id"], "theme": r.get("theme", ""), "summary": r["summary"][:50],
                     "emotion": r.get("emotion", 0), "timestamp": r["timestamp"]}
                    for r in self.db.get_reconstructed_by_level(level, 20)
                ]
                for level in [1, 2, 3]
            }
        }
