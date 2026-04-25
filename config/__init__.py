#!/usr/bin/env python3
"""
New Brain - Configuration Loader

安全加载私有身份配置。
优先加载 private_identity.yaml（隐私数据，已加入 .gitignore）
回退到 identity_template.yaml（开源占位符）
"""

import os
import yaml
from typing import Dict, Any, List

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
PRIVATE_CONFIG = os.path.join(CONFIG_DIR, "private_identity.yaml")
TEMPLATE_CONFIG = os.path.join(CONFIG_DIR, "identity_template.yaml")


class IdentityConfig:
    """身份配置管理器"""
    
    def __init__(self):
        self._data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置，优先私有配置"""
        config_path = PRIVATE_CONFIG if os.path.exists(PRIVATE_CONFIG) else TEMPLATE_CONFIG
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[Config] Warning: Failed to load {config_path}: {e}")
            return {}
    
    @property
    def identity(self) -> Dict[str, Any]:
        return self._data.get('identity', {})
    
    @property
    def preferences(self) -> Dict[str, List[Dict[str, Any]]]:
        return self._data.get('preferences', {})
    
    @property
    def memory_keywords(self) -> Dict[str, List[str]]:
        return self._data.get('memory_keywords', {})
    
    @property
    def dream_themes(self) -> List[Dict[str, Any]]:
        return self._data.get('dream_themes', [])
    
    @property
    def dmn_associations(self) -> Dict[str, List[str]]:
        return self._data.get('dmn_associations', {})
    
    @property
    def default_seeds(self) -> List[str]:
        return self._data.get('default_seeds', ['memory'])
    
    def get_preference_items(self) -> Dict[str, tuple]:
        """
        获取扁平化的偏好条目
        
        返回: {名称: (weight, category)}
        """
        items = {}
        pref = self.preferences
        
        for category, entries in pref.items():
            for entry in entries:
                name = entry.get('name', '')
                weight = entry.get('weight', 0.5)
                items[name] = (weight, category)
        
        return items
    
    def get_user_aliases(self) -> List[str]:
        return self.identity.get('user_aliases', ['User'])
    
    def get_self_aliases(self) -> List[str]:
        return self.identity.get('self_aliases', ['Assistant'])
    
    def get_backstory(self) -> str:
        return self.identity.get('backstory', '')
    
    def get_primary_user_alias(self) -> str:
        """获取主要用户称呼"""
        aliases = self.get_user_aliases()
        return aliases[0] if aliases else 'User'


# 全局单例
_config_instance = None


def get_config() -> IdentityConfig:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = IdentityConfig()
    return _config_instance


def reload_config():
    """重新加载配置"""
    global _config_instance
    _config_instance = IdentityConfig()


if __name__ == "__main__":
    cfg = get_config()
    print("=== Config Test ===")
    print(f"Identity: {cfg.identity}")
    print(f"Preferences: {len(cfg.get_preference_items())} items")
    print(f"Dream themes: {len(cfg.dream_themes)}")
    print(f"DMN associations: {len(cfg.dmn_associations)}")
    print(f"Primary user: {cfg.get_primary_user_alias()}")
