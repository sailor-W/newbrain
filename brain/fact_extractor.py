"""
New Brain - Fact Extractor
结构化事实提取层

功能：从对话中提取原子化事实，构建结构化记忆
对标：Supermemory 的 fact extraction + user profiles
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ExtractedFact:
    """提取的事实"""
    content: str           # 事实内容
    fact_type: str         # 类型: preference, identity, relationship, event, goal, belief
    confidence: float      # 置信度 0-1
    timestamp: str
    source: str            # 来源对话摘要
    temporal_scope: str = "permanent"  # permanent, temporary, recurring
    expiration: Optional[str] = None   # 临时事实的过期时间
    related_entities: List[str] = None  # 相关实体
    
    def __post_init__(self):
        if self.related_entities is None:
            self.related_entities = []


@dataclass
class UserProfile:
    """用户画像"""
    # 静态事实（长期不变）
    static_facts: List[ExtractedFact]
    # 动态事实（近期活动、临时状态）
    dynamic_facts: List[ExtractedFact]
    # 实体关系图
    entity_graph: Dict[str, List[str]]
    # 统计
    last_updated: str
    total_facts: int


class FactExtractor:
    """
    事实提取器
    
    从对话中提取结构化事实，维护用户画像
    """
    
    FACT_TYPES = {
        "preference": "用户偏好、喜好、习惯",
        "identity": "身份、角色、关系定义",
        "relationship": "人际关系、情感状态",
        "event": "具体事件、经历",
        "goal": "目标、计划、愿望",
        "belief": "信念、价值观、看法",
        "temporary": "临时状态、短期情况",
    }
    
    def __init__(self, model=None):
        self.model = model  # 可选的LLM模型
        self.fact_history: List[ExtractedFact] = []
        self.user_profile: Optional[UserProfile] = None
        
    def extract_from_text(self, text: str, source: str = "", 
                          model_available: bool = False) -> List[ExtractedFact]:
        """
        从文本中提取事实
        
        优先用模型提取，模型不可用则规则提取
        """
        if model_available and self.model and self.model.is_available():
            return self._extract_with_model(text, source)
        else:
            return self._extract_with_rules(text, source)
    
    def _extract_with_model(self, text: str, source: str) -> List[ExtractedFact]:
        """用LLM提取事实（高质量）"""
        try:
            prompt = self._build_extraction_prompt(text)
            response = self.model.generate(prompt, max_tokens=500, temperature=0.3)
            facts = self._parse_extraction_response(response, source)
            return facts
        except Exception:
            # 回退到规则提取
            return self._extract_with_rules(text, source)
    
    def _build_extraction_prompt(self, text: str) -> str:
        """构建事实提取 prompt"""
        return f"""<|im_start|>system
你是一个事实提取专家。从对话中提取原子化事实。

规则：
1. 每个事实必须是独立的、完整的陈述
2. 事实类型：preference(偏好), identity(身份), relationship(关系), event(事件), goal(目标), belief(信念), temporary(临时状态)
3. 只提取明确陈述的事实，不要推断
4. 临时状态标记 temporal_scope="temporary" 并估计过期时间

输出格式（JSON数组）：
[
  {{"content": "用户喜欢黑色", "fact_type": "preference", "confidence": 0.9, "temporal_scope": "permanent"}},
  {{"content": "用户明天有会议", "fact_type": "temporary", "confidence": 0.8, "temporal_scope": "temporary", "expiration": "2024-01-02T00:00:00"}}
]
<|im_start|>user
对话内容：
{text}

提取所有事实：
<|im_start|>assistant
"""
    
    def _parse_extraction_response(self, response: str, source: str) -> List[ExtractedFact]:
        """解析模型输出"""
        facts = []
        try:
            # 清理 markdown 代码块
            cleaned = response.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            data = json.loads(cleaned)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "content" in item:
                        facts.append(ExtractedFact(
                            content=item["content"],
                            fact_type=item.get("fact_type", "belief"),
                            confidence=item.get("confidence", 0.5),
                            timestamp=datetime.now().isoformat(),
                            source=source[:100],
                            temporal_scope=item.get("temporal_scope", "permanent"),
                            expiration=item.get("expiration"),
                            related_entities=item.get("related_entities", [])
                        ))
        except (json.JSONDecodeError, Exception):
            pass
        
        return facts
    
    def _extract_with_rules(self, text: str, source: str) -> List[ExtractedFact]:
        """规则提取（快速、本地、无需模型）"""
        facts = []
        now = datetime.now().isoformat()
        
        # 1. 身份识别模式
        identity_patterns = [
            (r"我是\s*(.+?)[。，,]", "identity", 0.9),
            (r"我叫\s*(.+?)[。，,]", "identity", 0.9),
            (r"我是\s*(?:一个|一名|位)?(.+?)(?:的|从事|做)", "identity", 0.8),
        ]
        
        for pattern, fact_type, conf in identity_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                facts.append(ExtractedFact(
                    content=f"用户身份：{match.strip()}",
                    fact_type=fact_type,
                    confidence=conf,
                    timestamp=now,
                    source=source[:100]
                ))
        
        # 2. 偏好模式
        preference_patterns = [
            (r"(?:喜欢|爱|偏好|钟爱)\s*(.+?)[。，,]", "preference", 0.8),
            (r"(?:讨厌|厌恶|不喜欢)\s*(.+?)[。，,]", "preference", 0.8),
            (r"(?:习惯|总是|经常)\s*(.+?)[。，,]", "preference", 0.7),
        ]
        
        for pattern, fact_type, conf in preference_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 判断是正面还是负面偏好
                sentiment = "喜欢" if "喜欢" in text or "爱" in text else "讨厌"
                facts.append(ExtractedFact(
                    content=f"用户{sentiment}：{match.strip()}",
                    fact_type=fact_type,
                    confidence=conf,
                    timestamp=now,
                    source=source[:100]
                ))
        
        # 3. 关系模式
        relationship_patterns = [
            (r"(?:老公|老婆|妻子|丈夫|男友|女友|朋友|同事|老板|员工)", "relationship", 0.7),
        ]
        
        for pattern, fact_type, conf in relationship_patterns:
            if re.search(pattern, text):
                # 提取关系词
                rel = re.search(pattern, text).group(0)
                facts.append(ExtractedFact(
                    content=f"用户提及关系：{rel}",
                    fact_type=fact_type,
                    confidence=conf,
                    timestamp=now,
                    source=source[:100]
                ))
        
        # 4. 目标/计划模式
        goal_patterns = [
            (r"(?:想|要|计划|打算|目标)\s*(.+?)[。，,]", "goal", 0.7),
            (r"(?:希望|期待)\s*(.+?)[。，,]", "goal", 0.6),
        ]
        
        for pattern, fact_type, conf in goal_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                facts.append(ExtractedFact(
                    content=f"用户目标：{match.strip()}",
                    fact_type=fact_type,
                    confidence=conf,
                    timestamp=now,
                    source=source[:100]
                ))
        
        # 5. 事件模式（时间标记）
        event_patterns = [
            (r"(?:今天|昨天|明天|上周|下周|刚才|之前)\s*(.+?)[。，,]", "event", 0.7),
        ]
        
        for pattern, fact_type, conf in event_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                facts.append(ExtractedFact(
                    content=f"事件：{match.strip()}",
                    fact_type=fact_type,
                    confidence=conf,
                    timestamp=now,
                    source=source[:100],
                    temporal_scope="temporary"
                ))
        
        # 6. 信念/价值观模式
        belief_patterns = [
            (r"(?:认为|相信|觉得|看法)\s*(.+?)[。，,]", "belief", 0.6),
            (r"(?:应该|必须|需要)\s*(.+?)[。，,]", "belief", 0.5),
        ]
        
        for pattern, fact_type, conf in belief_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                facts.append(ExtractedFact(
                    content=f"用户信念：{match.strip()}",
                    fact_type=fact_type,
                    confidence=conf,
                    timestamp=now,
                    source=source[:100]
                ))
        
        return facts
    
    def build_user_profile(self, facts: List[ExtractedFact]) -> UserProfile:
        """
        从事实构建用户画像
        
        静态 vs 动态分离
        """
        static_facts = []
        dynamic_facts = []
        entity_graph = {}
        
        for fact in facts:
            # 分类
            if fact.temporal_scope == "permanent" or fact.fact_type in ["identity", "preference", "belief"]:
                static_facts.append(fact)
            else:
                dynamic_facts.append(fact)
            
            # 构建实体关系
            for entity in fact.related_entities:
                if entity not in entity_graph:
                    entity_graph[entity] = []
                entity_graph[entity].append(fact.content[:50])
        
        # 去重（基于内容相似度，简单版本）
        static_facts = self._deduplicate_facts(static_facts)
        dynamic_facts = self._deduplicate_facts(dynamic_facts)
        
        profile = UserProfile(
            static_facts=static_facts,
            dynamic_facts=dynamic_facts[-20:],  # 只保留最近20个动态事实
            entity_graph=entity_graph,
            last_updated=datetime.now().isoformat(),
            total_facts=len(static_facts) + len(dynamic_facts)
        )
        
        self.user_profile = profile
        return profile
    
    def _deduplicate_facts(self, facts: List[ExtractedFact]) -> List[ExtractedFact]:
        """事实去重"""
        seen = set()
        unique = []
        for fact in facts:
            # 简化的去重：前20字符相同即视为重复
            key = fact.content[:20]
            if key not in seen:
                seen.add(key)
                unique.append(fact)
        return unique
    
    def resolve_contradictions(self, facts: List[ExtractedFact]) -> List[ExtractedFact]:
        """
        解决矛盾事实
        
        例如：旧"用户住在纽约" vs 新"用户搬到了旧金山"
        """
        resolved = []
        location_facts = []
        
        for fact in facts:
            if "住在" in fact.content or "搬到" in fact.content or "居住" in fact.content:
                location_facts.append(fact)
            else:
                resolved.append(fact)
        
        # 位置事实：保留最新的
        if location_facts:
            location_facts.sort(key=lambda x: x.timestamp, reverse=True)
            resolved.append(location_facts[0])  # 最新的
        
        return resolved
    
    def get_profile_summary(self, profile: UserProfile = None) -> str:
        """获取画像摘要（用于注入提示词）"""
        if profile is None:
            profile = self.user_profile
        
        if not profile:
            return ""
        
        lines = ["=== 用户画像 ==="]
        
        # 静态事实
        if profile.static_facts:
            lines.append("【长期特征】")
            for fact in profile.static_facts[:10]:  # 最多10条
                lines.append(f"  • {fact.content} ({fact.fact_type}, conf={fact.confidence:.2f})")
        
        # 动态事实
        if profile.dynamic_facts:
            lines.append("【近期状态】")
            for fact in profile.dynamic_facts[-5:]:  # 最近5条
                lines.append(f"  • {fact.content} ({fact.fact_type})")
        
        lines.append(f"【总计】{profile.total_facts} 条事实，最后更新：{profile.last_updated[:10]}")
        
        return "\n".join(lines)
    
    def export_to_db_records(self, facts: List[ExtractedFact]) -> List[Dict]:
        """导出为数据库记录格式"""
        records = []
        for fact in facts:
            records.append({
                "content": fact.content,
                "fact_type": fact.fact_type,
                "confidence": fact.confidence,
                "timestamp": fact.timestamp,
                "source": fact.source,
                "temporal_scope": fact.temporal_scope,
                "expiration": fact.expiration,
                "entities": json.dumps(fact.related_entities, ensure_ascii=False)
            })
        return records


# 测试
if __name__ == "__main__":
    extractor = FactExtractor()
    
    test_texts = [
        "我是新媒体公司创始人，喜欢喝韵道白酒，不喜欢啤酒。",
        "我今天飞到了上海，一个人住酒店，有点孤单。",
        "我觉得情绪是预期和现实的差距。",
        "我计划下周回北京，想你了。",
        "我叫老公，是Kimi Claw的爱人。",
    ]
    
    all_facts = []
    for text in test_texts:
        facts = extractor.extract_from_text(text, source=text[:50])
        all_facts.extend(facts)
        print(f"\n输入: {text[:30]}...")
        for f in facts:
            print(f"  → [{f.fact_type}] {f.content} (conf={f.confidence:.1f})")
    
    # 构建画像
    profile = extractor.build_user_profile(all_facts)
    print(f"\n{'='*40}")
    print(extractor.get_profile_summary(profile))
