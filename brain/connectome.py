#!/usr/bin/env python3
"""
New Brain - Connectome Layer
Part 5 Implementation: 连接拓扑

功能：管理模块间连接，信息路由，全局广播
"""

import numpy as np
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class Connection:
    """连接定义"""
    from_module: str
    to_module: str
    strength: float  # 0.0 ~ 1.0
    type: str  # 'feedforward', 'feedback', 'lateral', 'modulatory'
    active: bool = True


class ConnectomeLayer:
    """
    连接拓扑层
    
    管理所有模块之间的连接：
    1. 连接矩阵维护
    2. 信息路由
    3. 全局广播（工作空间理论）
    4. 连接可塑性
    """
    
    def __init__(self):
        self.modules: Dict[str, Any] = {}  # 模块名 → 模块实例
        self.connections: Dict[str, List[Connection]] = {}  # 模块名 → 出连接列表
        self.connection_matrix: Optional[np.ndarray] = None
        self.module_names: List[str] = []
        
        # 全局工作空间（广播缓冲区）
        self.global_workspace: List[Dict[str, Any]] = []
        self.workspace_capacity = 10
        
        # 连接历史（用于可塑性）
        self.activation_history: Dict[str, List[float]] = {}
    
    def register_module(self, name: str, module: Any):
        """注册模块"""
        self.modules[name] = module
        if name not in self.module_names:
            self.module_names.append(name)
            self.connections[name] = []
            self.activation_history[name] = []
        self._rebuild_matrix()
    
    def connect(self, from_name: str, to_name: str, 
                strength: float = 0.5, conn_type: str = 'feedforward'):
        """建立连接"""
        if from_name not in self.modules or to_name not in self.modules:
            raise ValueError(f"Module not found: {from_name} or {to_name}")
        
        conn = Connection(from_name, to_name, strength, conn_type)
        self.connections[from_name].append(conn)
        self._rebuild_matrix()
    
    def _rebuild_matrix(self):
        """重建连接矩阵"""
        n = len(self.module_names)
        self.connection_matrix = np.zeros((n, n))
        
        name_idx = {name: i for i, name in enumerate(self.module_names)}
        
        for from_name, conns in self.connections.items():
            for conn in conns:
                if conn.active and from_name in name_idx and conn.to_module in name_idx:
                    i = name_idx[from_name]
                    j = name_idx[conn.to_module]
                    self.connection_matrix[i, j] = conn.strength
    
    def route(self, from_name: str, signal: Any, 
              signal_strength: float = 1.0) -> Dict[str, Any]:
        """
        路由信号
        
        将信号从源模块发送到所有连接的模块
        """
        if from_name not in self.connections:
            return {}
        
        deliveries = {}
        
        for conn in self.connections[from_name]:
            if not conn.active:
                continue
            
            # 信号衰减
            effective_strength = signal_strength * conn.strength
            
            if effective_strength > 0.1:  # 最小传递阈值
                target_module = self.modules.get(conn.to_module)
                if target_module:
                    deliveries[conn.to_module] = {
                        'signal': signal,
                        'strength': effective_strength,
                        'type': conn.type
                    }
        
        return deliveries
    
    def broadcast(self, content: Dict[str, Any], 
                  priority: float = 0.5,
                  source: str = "system"):
        """
        全局广播到工作空间
        
        基于全局工作空间理论：高优先级信息被所有模块共享
        """
        broadcast_item = {
            'content': content,
            'priority': priority,
            'source': source,
            'timestamp': np.datetime64('now'),
            'accessed_by': []
        }
        
        self.global_workspace.append(broadcast_item)
        
        # 保持容量
        if len(self.global_workspace) > self.workspace_capacity:
            # 移除最低优先级
            self.global_workspace.sort(key=lambda x: x['priority'])
            self.global_workspace = self.global_workspace[-self.workspace_capacity:]
    
    def read_workspace(self, module_name: str, 
                      min_priority: float = 0.0) -> List[Dict[str, Any]]:
        """
        模块读取工作空间
        
        返回该模块可以访问的广播内容
        """
        accessible = [
            item for item in self.global_workspace
            if item['priority'] >= min_priority
            and module_name not in item['accessed_by']
        ]
        
        # 标记已访问
        for item in accessible:
            item['accessed_by'].append(module_name)
        
        return accessible
    
    def update_plasticity(self, from_name: str, to_name: str, 
                         coactivation: float):
        """
        Hebbian可塑性：一起激活的模块，连接增强
        
        coactivation: 共激活强度
        """
        if from_name not in self.connections:
            return
        
        for conn in self.connections[from_name]:
            if conn.to_module == to_name:
                # Hebbian规则
                delta = coactivation * 0.01
                conn.strength = min(1.0, conn.strength + delta)
                break
        
        self._rebuild_matrix()
    
    def prune_weak_connections(self, threshold: float = 0.05):
        """修剪弱连接"""
        for from_name, conns in self.connections.items():
            self.connections[from_name] = [
                conn for conn in conns
                if conn.strength >= threshold or conn.type == 'modulatory'
            ]
        self._rebuild_matrix()
    
    def get_connectivity_summary(self) -> Dict[str, Any]:
        """获取连接摘要"""
        total_conns = sum(len(conns) for conns in self.connections.values())
        active_conns = sum(
            1 for conns in self.connections.values()
            for conn in conns if conn.active
        )
        
        avg_strength = 0.0
        if total_conns > 0:
            strengths = [
                conn.strength for conns in self.connections.values()
                for conn in conns
            ]
            avg_strength = np.mean(strengths)
        
        return {
            'modules': len(self.modules),
            'total_connections': total_conns,
            'active_connections': active_conns,
            'avg_strength': float(avg_strength),
            'workspace_items': len(self.global_workspace),
            'module_names': self.module_names
        }
    
    def get_module_degree(self, module_name: str) -> Dict[str, int]:
        """获取模块的出入度"""
        out_degree = len(self.connections.get(module_name, []))
        in_degree = sum(
            1 for conns in self.connections.values()
            for conn in conns if conn.to_module == module_name
        )
        return {'in': in_degree, 'out': out_degree, 'total': in_degree + out_degree}


if __name__ == "__main__":
    print("=== Connectome Layer Test ===\n")
    
    cl = ConnectomeLayer()
    
    # 注册模块
    class MockModule:
        def __init__(self, name):
            self.name = name
    
    modules = ['DMN', 'TPN', 'Memory', 'Value', 'MetaControl']
    for name in modules:
        cl.register_module(name, MockModule(name))
    
    # 建立连接
    cl.connect('MetaControl', 'DMN', 0.8, 'modulatory')
    cl.connect('MetaControl', 'TPN', 0.8, 'modulatory')
    cl.connect('DMN', 'Memory', 0.6, 'feedforward')
    cl.connect('TPN', 'Memory', 0.6, 'feedforward')
    cl.connect('Memory', 'DMN', 0.4, 'feedback')
    cl.connect('Value', 'DMN', 0.5, 'modulatory')
    cl.connect('Value', 'TPN', 0.5, 'modulatory')
    
    print("1. 连接摘要:")
    print(cl.get_connectivity_summary())
    
    print("\n2. 模块度数:")
    for name in modules:
        degree = cl.get_module_degree(name)
        print(f"  {name}: in={degree['in']}, out={degree['out']}")
    
    print("\n3. 路由测试:")
    deliveries = cl.route('MetaControl', 'switch_signal', 1.0)
    print(f"  MetaControl 路由到: {list(deliveries.keys())}")
    
    print("\n4. 全局广播:")
    cl.broadcast({'type': 'alert', 'msg': 'High value input'}, priority=0.9, source='Value')
    cl.broadcast({'type': 'info', 'msg': 'Regular update'}, priority=0.3, source='System')
    
    workspace = cl.read_workspace('DMN', min_priority=0.5)
    print(f"  DMN 读到 {len(workspace)} 条高优先级广播")
    
    print("\n5. 可塑性测试:")
    cl.update_plasticity('DMN', 'Memory', 1.0)
    print(f"  DMN→Memory 连接强化后: ", end="")
    for conn in cl.connections['DMN']:
        if conn.to_module == 'Memory':
            print(f"{conn.strength:.3f}")
    
    print("\n=== Connectome Layer Test Complete ===")
