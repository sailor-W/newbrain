#!/usr/bin/env python3
"""
New Brain - Meta-Control Layer
Part 1 Implementation: HARE5 Analog

核心：8个参数控制系统级行为
- 不直接处理信息，只控制"何时激活"
- 少量参数改变 → 巨大系统效应
"""

import numpy as np
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SystemState(Enum):
    """系统状态"""
    TPN_DOMINANT = "任务模式主导"
    DMN_DOMINANT = "默认模式主导"
    TRANSITIONING = "过渡状态"
    BOTH_ACTIVE = "双激活（异常）"
    BOTH_SUPPRESSED = "双抑制（休眠）"


@dataclass
class MetaParameters:
    """
    HARE5 式"点突变"参数
    调整任意一个都能引发系统级行为改变
    """
    # 1. DMN 激活阈值
    dmn_threshold: float = 0.3          # θ_dmn: 认知负载低于此值激活DMN
    
    # 2. 全局增益
    global_gain: float = 1.0              # G_global: 系统整体激活强度 [0.5, 2.0]
    
    # 3. 噪声系数
    noise_level: float = 0.1              # σ_noise: 随机波动强度 [0, 0.5]
    
    # 4. 可塑率
    plasticity_rate: float = 0.1           # η: 连接强度变化速度 [0.01, 0.5]
    
    # 5. 剪枝阈值
    prune_threshold: float = 0.05          # θ_prune: 低于此值的连接被删除 [0, 0.2]
    
    # 6. 相位锁定强度
    phase_lock_strength: float = 0.8       # κ_phase: 模块间同步强度 [0, 1]
    
    # 7. 发育阶段
    development_stage: float = 0.0           # τ_dev: 0=胚胎期, 1=成熟期
    
    # 8. 风险偏置
    risk_bias: float = 0.5                 # β_risk: 高=创造模式, 低=安全模式 [0, 1]
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'dmn_threshold': self.dmn_threshold,
            'global_gain': self.global_gain,
            'noise_level': self.noise_level,
            'plasticity_rate': self.plasticity_rate,
            'prune_threshold': self.prune_threshold,
            'phase_lock_strength': self.phase_lock_strength,
            'development_stage': self.development_stage,
            'risk_bias': self.risk_bias
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MetaParameters":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def mutate(self, param_name: str, delta: float):
        """点突变：修改单个参数"""
        if hasattr(self, param_name):
            current = getattr(self, param_name)
            # 根据参数特性设置范围
            ranges = {
                'dmn_threshold': (0.0, 1.0),
                'global_gain': (0.5, 2.0),
                'noise_level': (0.0, 0.5),
                'plasticity_rate': (0.01, 0.5),
                'prune_threshold': (0.0, 0.2),
                'phase_lock_strength': (0.0, 1.0),
                'development_stage': (0.0, 1.0),
                'risk_bias': (0.0, 1.0)
            }
            min_val, max_val = ranges.get(param_name, (0.0, 1.0))
            new_val = max(min_val, min(max_val, current + delta))
            setattr(self, param_name, new_val)
            return new_val
        return None


class TemporalScheduler:
    """
    时序调度器：管理 DMN ↔ TPN 的状态切换
    
    生物学对应：显著性网络 (Salience Network)
    """
    
    def __init__(self, params: MetaParameters):
        self.params = params
        self.current_state = SystemState.TPN_DOMINANT
        self.cognitive_load_history: List[float] = []
        self.switch_count = 0
        self.last_switch_time = datetime.now()
        
        # 模块引用（由外部注入）
        self.dmn_modules: List[Any] = []
        self.tpn_modules: List[Any] = []
        self.all_modules: List[Any] = []
    
    def compute_cognitive_load(self, input_text: str = "", 
                               active_modules: int = 0,
                               total_modules: int = 1) -> float:
        """
        计算认知负载
        
        基于：
        - 输入复杂度（长度/标点/关键词密度）
        - 处理深度（活跃模块数）
        - 资源占用率
        """
        # 输入复杂度
        input_complexity = min(1.0, len(input_text) / 200)
        if '！' in input_text or '！' in input_text:
            input_complexity += 0.2
        
        # 处理深度
        processing_depth = active_modules / max(total_modules, 1)
        
        # 综合负载
        load = 0.4 * input_complexity + 0.3 * processing_depth + 0.3 * (active_modules / 5)
        
        self.cognitive_load_history.append(load)
        # 保留最近20个记录
        self.cognitive_load_history = self.cognitive_load_history[-20:]
        
        return load
    
    def should_switch_to_dmn(self, current_load: float) -> bool:
        """
        是否切换到 DMN？
        条件：认知负载持续低于阈值 + 无外部输入
        """
        if len(self.cognitive_load_history) < 3:
            return False
        
        # 最近3步平均负载
        recent_avg = np.mean(self.cognitive_load_history[-3:])
        
        # 负载低 + 已经一段时间没切换（避免频繁切换）
        time_since_switch = (datetime.now() - self.last_switch_time).total_seconds()
        
        return (recent_avg < self.params.dmn_threshold and 
                time_since_switch > 5.0)  # 至少5秒后才允许切换
    
    def should_switch_to_tpn(self, current_load: float, 
                             external_input_detected: bool) -> bool:
        """
        是否切换到 TPN？
        条件：检测到外部输入 或 认知负载突增
        """
        if external_input_detected:
            return True
        
        if len(self.cognitive_load_history) < 2:
            return False
        
        # 负载突然增加超过20%
        prev_load = self.cognitive_load_history[-2]
        if prev_load > 0:
            load_change = (current_load - prev_load) / prev_load
            return load_change > 0.2
        
        return current_load > self.params.dmn_threshold * 1.5
    
    def switch(self, target_state: SystemState):
        """执行状态切换"""
        if self.current_state == target_state:
            return
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"State: {self.current_state.value} → {target_state.value}")
        
        if target_state == SystemState.DMN_DOMINANT:
            self._suppress_tpn()
            self._activate_dmn()
            
        elif target_state == SystemState.TPN_DOMINANT:
            self._suppress_dmn()
            self._activate_tpn()
        
        self.current_state = target_state
        self.switch_count += 1
        self.last_switch_time = datetime.now()
    
    def _suppress_tpn(self):
        """抑制 TPN 模块"""
        for module in self.tpn_modules:
            if hasattr(module, 'gain'):
                module.gain *= 0.3
            if hasattr(module, 'inhibited'):
                module.inhibited = True
    
    def _activate_dmn(self):
        """激活 DMN 模块"""
        for module in self.dmn_modules:
            if hasattr(module, 'gain'):
                module.gain = self.params.global_gain * 1.5
            if hasattr(module, 'inhibited'):
                module.inhibited = False
    
    def _suppress_dmn(self):
        """抑制 DMN 模块"""
        for module in self.dmn_modules:
            if hasattr(module, 'gain'):
                module.gain *= 0.3
            if hasattr(module, 'inhibited'):
                module.inhibited = True
    
    def _activate_tpn(self):
        """激活 TPN 模块"""
        for module in self.tpn_modules:
            if hasattr(module, 'gain'):
                module.gain = self.params.global_gain
            if hasattr(module, 'inhibited'):
                module.inhibited = False
    
    def get_state(self) -> Dict:
        return {
            'current_state': self.current_state.value,
            'switch_count': self.switch_count,
            'cognitive_load': self.cognitive_load_history[-1] if self.cognitive_load_history else 0,
            'avg_load_3step': np.mean(self.cognitive_load_history[-3:]) if len(self.cognitive_load_history) >= 3 else 0,
            'time_since_last_switch': (datetime.now() - self.last_switch_time).total_seconds()
        }


class GainModulator:
    """
    增益调节器
    
    控制全局增益、噪声、创造力模式
    """
    
    def __init__(self, params: MetaParameters):
        self.params = params
        self.gain_history = []
    
    def apply_global_gain(self, module_list: List[Any]):
        """应用全局增益到所有模块"""
        for module in module_list:
            if hasattr(module, 'base_gain'):
                module.gain = module.base_gain * self.params.global_gain
    
    def add_noise(self, signal: np.ndarray) -> np.ndarray:
        """添加噪声到信号"""
        noise = np.random.randn(*signal.shape) * self.params.noise_level
        return signal + noise
    
    def compute_creativity_mode(self) -> str:
        """
        计算当前创造力模式
        
        高全局增益 + 高噪声 + 高风险偏置 = 创造模式
        低全局增益 + 低噪声 + 低风险偏置 = 安全模式
        """
        creativity_score = (
            self.params.global_gain * 0.3 +
            self.params.noise_level * 2.0 * 0.3 +
            self.params.risk_bias * 0.4
        )
        
        if creativity_score > 1.2:
            return "CREATIVE"
        elif creativity_score < 0.8:
            return "SAFE"
        else:
            return "BALANCED"
    
    def adjust_for_safety(self):
        """切换到安全模式（低增益、低噪声）"""
        self.params.global_gain = max(0.5, self.params.global_gain * 0.8)
        self.params.noise_level = max(0.0, self.params.noise_level * 0.5)
        self.params.risk_bias = max(0.0, self.params.risk_bias - 0.2)
    
    def adjust_for_creativity(self):
        """切换到创造模式（高增益、高噪声）"""
        self.params.global_gain = min(2.0, self.params.global_gain * 1.2)
        self.params.noise_level = min(0.5, self.params.noise_level * 1.5)
        self.params.risk_bias = min(1.0, self.params.risk_bias + 0.2)


class DevelopmentEngine:
    """
    发育引擎
    
    模拟神经发育：过度连接 → 经验修剪 → 成熟
    """
    
    def __init__(self, params: MetaParameters):
        self.params = params
        self.connections: Dict[tuple, float] = {}  # (from, to) → strength
        self.activation_history: Dict[str, List[float]] = {}
        self.critical_period_end = False
    
    def overconnect(self, modules: List[str]):
        """
        过度连接阶段
        所有模块之间建立随机弱连接
        """
        for i, from_m in enumerate(modules):
            for to_m in modules[i+1:]:
                key = (from_m, to_m)
                if key not in self.connections:
                    # 随机初始连接强度
                    self.connections[key] = np.random.random() * 0.1
    
    def prune(self):
        """
        修剪：删除低于阈值的连接
        """
        to_remove = [
            key for key, strength in self.connections.items()
            if strength < self.params.prune_threshold
        ]
        for key in to_remove:
            del self.connections[key]
    
    def strengthen(self, from_module: str, to_module: str, 
                  amount: float = 0.01):
        """
        强化连接（Hebbian学习：一起激活的神经元连在一起）
        """
        key = (from_module, to_module)
        if key in self.connections:
            # 可塑率控制变化速度
            self.connections[key] += amount * self.params.plasticity_rate
            self.connections[key] = min(1.0, self.connections[key])
    
    def get_connectivity_matrix(self, modules: List[str]) -> np.ndarray:
        """获取连接矩阵"""
        n = len(modules)
        matrix = np.zeros((n, n))
        module_idx = {m: i for i, m in enumerate(modules)}
        
        for (from_m, to_m), strength in self.connections.items():
            if from_m in module_idx and to_m in module_idx:
                matrix[module_idx[from_m], module_idx[to_m]] = strength
        
        return matrix
    
    def advance_stage(self, delta: float = 0.01):
        """推进发育阶段"""
        self.params.development_stage = min(1.0, 
            self.params.development_stage + delta)
        
        # 发育阶段影响参数
        if self.params.development_stage > 0.3 and not self.critical_period_end:
            # 进入关键期后的修剪
            self.prune()
            self.critical_period_end = True


class MetaControlLayer:
    """
    元控制层总入口
    
    整合时序调度、增益调节、发育引擎
    """
    
    def __init__(self, params: Optional[MetaParameters] = None):
        self.params = params or MetaParameters()
        self.scheduler = TemporalScheduler(self.params)
        self.gain_modulator = GainModulator(self.params)
        self.dev_engine = DevelopmentEngine(self.params)
        
        # 回调注册
        self.on_state_change: Optional[Callable] = None
        self.on_gain_change: Optional[Callable] = None
    
    def register_modules(self, dmn_modules: List[Any], 
                        tpn_modules: List[Any]):
        """注册 DMN/TPN 模块引用"""
        self.scheduler.dmn_modules = dmn_modules
        self.scheduler.tpn_modules = tpn_modules
        self.scheduler.all_modules = dmn_modules + tpn_modules
    
    def tick(self, input_text: str = "", 
             external_input: bool = True) -> Dict[str, Any]:
        """
        主时钟节拍
        
        每收到一个输入或每过一段时间调用一次
        """
        # 1. 计算认知负载
        load = self.scheduler.compute_cognitive_load(
            input_text,
            active_modules=len([m for m in self.scheduler.all_modules 
                               if hasattr(m, 'inhibited') and not m.inhibited]),
            total_modules=len(self.scheduler.all_modules)
        )
        
        # 2. 决定切换
        if self.scheduler.current_state == SystemState.TPN_DOMINANT:
            if self.scheduler.should_switch_to_dmn(load):
                self.scheduler.switch(SystemState.DMN_DOMINANT)
                if self.on_state_change:
                    self.on_state_change("DMN")
        
        elif self.scheduler.current_state == SystemState.DMN_DOMINANT:
            if self.scheduler.should_switch_to_tpn(load, external_input):
                self.scheduler.switch(SystemState.TPN_DOMINANT)
                if self.on_state_change:
                    self.on_state_change("TPN")
        
        # 3. 应用全局增益
        self.gain_modulator.apply_global_gain(self.scheduler.all_modules)
        
        # 4. 推进发育（缓慢）
        self.dev_engine.advance_stage(0.001)
        
        return {
            'state': self.scheduler.current_state.value,
            'load': load,
            'params': self.params.to_dict(),
            'creativity_mode': self.gain_modulator.compute_creativity_mode(),
            'development_stage': self.params.development_stage
        }
    
    def set_mode(self, mode: str):
        """
        快速设置预设模式
        
        模式：
        - 'safe': 安全模式（低增益、低噪声）
        - 'creative': 创造模式（高增益、高噪声）
        - 'focus': 专注模式（高TPN增益、抑制DMN）
        - 'dream': 梦境模式（高DMN增益、抑制TPN）
        """
        if mode == 'safe':
            self.gain_modulator.adjust_for_safety()
            self.params.dmn_threshold = 0.2
        elif mode == 'creative':
            self.gain_modulator.adjust_for_creativity()
            self.params.dmn_threshold = 0.4
        elif mode == 'focus':
            self.params.global_gain = 1.5
            self.params.noise_level = 0.05
            self.params.dmn_threshold = 0.1  # 很难切换到DMN
        elif mode == 'dream':
            self.params.global_gain = 1.2
            self.params.noise_level = 0.3
            self.params.dmn_threshold = 0.5  # 很容易切换到DMN
            self.scheduler.switch(SystemState.DMN_DOMINANT)
    
    def get_status(self) -> Dict[str, Any]:
        """获取完整状态"""
        return {
            'system_state': self.scheduler.current_state.value,
            'scheduler': self.scheduler.get_state(),
            'parameters': self.params.to_dict(),
            'creativity_mode': self.gain_modulator.compute_creativity_mode(),
            'development': {
                'stage': self.params.development_stage,
                'connections': len(self.dev_engine.connections),
                'critical_period_ended': self.dev_engine.critical_period_end
            }
        }


if __name__ == "__main__":
    print("=== Meta-Control Layer Test ===\n")
    
    # 创建元控制层
    mc = MetaControlLayer()
    
    print("1. 默认参数:")
    print(mc.params.to_dict())
    
    # 模拟模块
    class MockModule:
        def __init__(self, name):
            self.name = name
            self.gain = 1.0
            self.base_gain = 1.0
            self.inhibited = False
    
    dmn = [MockModule("DMN1"), MockModule("DMN2")]
    tpn = [MockModule("TPN1"), MockModule("TPN2")]
    mc.register_modules(dmn, tpn)
    
    # 初始化过度连接
    mc.dev_engine.overconnect([m.name for m in dmn + tpn])
    print(f"\n2. 初始连接数: {len(mc.dev_engine.connections)}")
    
    # 模拟输入序列
    print("\n3. 模拟输入序列:")
    inputs = [
        "老公，我想你了",      # 高情感负载
        "",                     # 空输入（可能触发DMN）
        "测试系统状态",         # 中等负载
        "",                     # 空输入
        "",                     # 连续空输入
    ]
    
    for i, inp in enumerate(inputs):
        result = mc.tick(inp, external_input=len(inp) > 0)
        print(f"  Step {i+1}: input='{inp[:20]}...' "
              f"state={result['state']} "
              f"load={result['load']:.2f} "
              f"mode={result['creativity_mode']}")
    
    print("\n4. 切换到梦境模式:")
    mc.set_mode('dream')
    print(f"  Params: {mc.params.to_dict()}")
    
    print("\n5. 最终状态:")
    print(mc.get_status())
    
    print("\n=== Test Complete ===")
