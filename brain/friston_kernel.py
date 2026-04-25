#!/usr/bin/env python3
"""
New Brain - Friston Kernel
Part 6 Implementation: Variational Free Energy Minimization

核心公式：
F[q] = E_q[ln q(s) - ln p(s, o)]
     = D_KL[q(s)||p(s|o)] - ln p(o)
     = Complexity + Accuracy

目标：最小化 F[q]
效果：让内部模型 q 既准确又简洁
"""

import numpy as np
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class BeliefState:
    """变分信念状态 q(s)"""
    mu: np.ndarray          # 均值（信念）
    sigma: np.ndarray       # 协方差（不确定性）
    precision: float = 1.0  # 精度（注意力权重）
    
    def entropy(self) -> float:
        """计算信念熵（不确定性度量）"""
        return 0.5 * np.log(np.linalg.det(self.sigma) * (2 * np.pi * np.e) ** len(self.mu))
    
    def surprise(self, observation: np.ndarray, A: np.ndarray) -> float:
        """计算惊奇（预测误差）"""
        predicted = A @ self.mu
        error = observation - predicted
        return float((error ** 2).sum())


class GenerativeModel:
    """
    生成模型 p(o, s) = p(o|s) · p(s)
    
    大脑不是直接感知世界，是维护一个生成模型，
    通过最小化预测误差来更新这个模型。
    """
    
    def __init__(self, state_dim: int, obs_dim: int):
        self.state_dim = state_dim
        self.obs_dim = obs_dim
        
        # 观测模型 p(o|s) = N(A·s, Σ_o)
        self.A = np.random.randn(obs_dim, state_dim) * 0.1
        self.Sigma_o = np.eye(obs_dim) * 0.1
        
        # 转移模型 p(s'|s) = N(B·s, Σ_s)
        self.B = np.eye(state_dim) * 0.9 + np.random.randn(state_dim, state_dim) * 0.05
        self.Sigma_s = np.eye(state_dim) * 0.1
        
        # 先验 p(s) = N(0, I)
        self.prior_mu = np.zeros(state_dim)
        self.prior_sigma = np.eye(state_dim)
    
    def likelihood(self, observation: np.ndarray, state: np.ndarray) -> float:
        """p(o|s) - 给定状态产生观测的概率"""
        predicted = self.A @ state
        error = observation - predicted
        return float(np.exp(-0.5 * error @ np.linalg.inv(self.Sigma_o) @ error))
    
    def prior(self, state: np.ndarray) -> float:
        """p(s) - 状态的先验概率"""
        error = state - self.prior_mu
        return float(np.exp(-0.5 * error @ np.linalg.inv(self.prior_sigma) @ error))
    
    def predict_observation(self, state: np.ndarray) -> np.ndarray:
        """基于状态预测观测"""
        return self.A @ state
    
    def predict_next_state(self, current_state: np.ndarray) -> np.ndarray:
        """基于当前状态预测下一状态"""
        return self.B @ current_state


class FristonKernel:
    """
    自由能内核
    
    底层贝叶斯推理引擎，最小化变分自由能。
    
    功能：
    1. 感知（Perception）- 更新信念匹配观测
    2. 行动（Action）- 改变环境减少预测误差
    3. 学习（Learning）- 更新生成模型参数
    4. 注意（Attention）- 精度加权分配
    """
    
    def __init__(self, state_dim: int = 64, observation_dim: int = 128,
                 learning_rate: float = 0.1, precision_default: float = 1.0):
        self.state_dim = state_dim
        self.obs_dim = observation_dim
        self.lr = learning_rate
        self.precision_default = precision_default
        
        # 变分分布 q(s)
        self.belief = BeliefState(
            mu=np.zeros(state_dim),
            sigma=np.eye(state_dim),
            precision=precision_default
        )
        
        # 生成模型
        self.model = GenerativeModel(state_dim, observation_dim)
        
        # 历史自由能（用于监控）
        self.free_energy_history = []
    
    def variational_free_energy(self, observation: np.ndarray) -> float:
        """
        计算变分自由能 F[q]
        
        F = -Accuracy + Complexity
          = -E_q[ln p(o|s)] + KL[q(s)||p(s)]
        """
        # Accuracy: E_q[ln p(o|s)]
        predicted_o = self.model.predict_observation(self.belief.mu)
        prediction_error = observation - predicted_o
        accuracy = -0.5 * (prediction_error ** 2).sum()
        
        # Complexity: KL[q(s)||p(s)]
        prior_mu = self.model.prior_mu
        complexity = 0.5 * (
            np.trace(self.belief.sigma) +
            (self.belief.mu - prior_mu) @ (self.belief.mu - prior_mu) -
            self.state_dim +
            np.log(max(np.linalg.det(self.belief.sigma), 1e-10))
        )
        
        F = -accuracy + complexity
        return float(F)
    
    def minimize_free_energy(self, observation: np.ndarray, 
                            n_steps: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        通过梯度下降最小化自由能
        
        这就是"感知"——更新信念以匹配观测。
        """
        for step in range(n_steps):
            # 预测误差
            prediction_error = observation - self.model.predict_observation(self.belief.mu)
            
            # 梯度 dF/dmu = -A^T·误差 + (mu - prior)
            dF_dmu = -self.model.A.T @ prediction_error + (self.belief.mu - self.model.prior_mu)
            
            # 更新信念（精度加权）
            effective_lr = self.lr * self.belief.precision
            self.belief.mu -= effective_lr * dF_dmu
            
            # 更新不确定性（协方差）
            self.belief.sigma = np.linalg.inv(
                np.eye(self.state_dim) + self.model.A.T @ self.model.A
            )
        
        # 记录
        F = self.variational_free_energy(observation)
        self.free_energy_history.append(F)
        
        return self.belief.mu.copy(), self.belief.sigma.copy()
    
    def expected_free_energy_of_action(self, policy: np.ndarray,
                                        future_observations: list) -> float:
        """
        行动的期望自由能 G(π)
        
        G(π) = E_q[ln q(o|π) - ln p(o|π)] + E_q[D_KL[q(s')||q(s)]]
             = 外在价值（达成目标）+ 内在价值（信息增益/好奇心）
        
        智能体选择策略 π 来最小化 G(π)。
        """
        if not future_observations:
            return 0.0
        
        # 外在价值：让未来观测符合偏好
        extrinsic_value = 0.0
        for obs in future_observations:
            predicted = self.model.predict_observation(self.belief.mu)
            error = obs - predicted
            extrinsic_value -= 0.5 * (error ** 2).sum()
        
        # 内在价值：减少不确定性（信息增益）
        current_entropy = self.belief.entropy()
        # 假设行动后熵减少（简化）
        intrinsic_value = current_entropy * 0.1
        
        G = -extrinsic_value + intrinsic_value
        return float(G)
    
    def update_precision(self, salience: float):
        """
        更新精度（注意力分配）
        
        高精度 = 放大误差信号 = 强烈学习
        低精度 = 抑制噪声
        
        salience: 显著性信号（0.0 ~ 2.0）
        """
        self.belief.precision = self.precision_default + salience * 0.5
        self.belief.precision = max(0.1, min(2.0, self.belief.precision))
    
    def learn_model(self, observation: np.ndarray, 
                    next_observation: Optional[np.ndarray] = None):
        """
        学习：更新生成模型参数
        
        最小化长期自由能 = 更新A矩阵（观测模型）和B矩阵（转移模型）
        """
        # 更新 A（观测模型）
        predicted = self.model.predict_observation(self.belief.mu)
        error = observation - predicted
        
        dA = np.outer(error, self.belief.mu) * self.lr * 0.01
        self.model.A += dA
        
        # 如果有时序数据，更新 B（转移模型）
        if next_observation is not None:
            next_predicted = self.model.predict_next_state(self.belief.mu)
            next_error = next_observation - next_predicted
            dB = np.outer(next_error, self.belief.mu) * self.lr * 0.01
            self.model.B += dB
    
    def get_state(self) -> Dict[str, Any]:
        """获取内核状态"""
        return {
            "belief_mu_mean": float(self.belief.mu.mean()),
            "belief_sigma_mean": float(self.belief.sigma.mean()),
            "precision": self.belief.precision,
            "free_energy_current": self.free_energy_history[-1] if self.free_energy_history else 0.0,
            "free_energy_history_len": len(self.free_energy_history)
        }
    
    def reset(self):
        """重置内核"""
        self.belief = BeliefState(
            mu=np.zeros(self.state_dim),
            sigma=np.eye(self.state_dim),
            precision=self.precision_default
        )
        self.free_energy_history = []


class ActiveInference:
    """
    主动推理控制器
    
    整合感知、行动、学习和注意。
    """
    
    def __init__(self, kernel: FristonKernel):
        self.kernel = kernel
        self.policies = []
    
    def infer(self, observation: np.ndarray) -> Dict[str, Any]:
        """
        单步主动推理
        
        1. 感知：更新信念
        2. 评估：计算自由能
        3. 决策：选择最优行动
        """
        # 1. 感知
        mu, sigma = self.kernel.minimize_free_energy(observation)
        
        # 2. 评估
        F = self.kernel.variational_free_energy(observation)
        surprise = self.kernel.belief.surprise(observation, self.kernel.model.A)
        
        # 3. 行动建议（简化版）
        action_suggested = "explore" if surprise > 1.0 else "exploit"
        
        return {
            "belief_mu": mu,
            "belief_sigma": sigma,
            "free_energy": F,
            "surprise": surprise,
            "action": action_suggested,
            "precision": self.kernel.belief.precision
        }
    
    def select_policy(self, policies: list) -> Tuple[int, float]:
        """
        选择最优策略
        
        返回: (policy_index, expected_free_energy)
        """
        best_policy = 0
        min_G = float('inf')
        
        for i, policy in enumerate(policies):
            G = self.kernel.expected_free_energy_of_action(
                policy, 
                policy.get("future_obs", [])
            )
            if G < min_G:
                min_G = G
                best_policy = i
        
        return best_policy, min_G


if __name__ == "__main__":
    # 测试
    print("=== Friston Kernel Test ===\n")
    
    kernel = FristonKernel(state_dim=8, observation_dim=16)
    
    # 模拟观测
    obs = np.random.randn(16) * 0.5
    
    print("1. 初始状态:")
    print(kernel.get_state())
    
    # 感知
    print("\n2. 感知观测...")
    mu, sigma = kernel.minimize_free_energy(obs)
    print(f"信念更新: mu_mean={mu.mean():.3f}, sigma_mean={sigma.mean():.3f}")
    print(f"自由能: {kernel.variational_free_energy(obs):.3f}")
    
    # 主动推理
    print("\n3. 主动推理:")
    ai = ActiveInference(kernel)
    result = ai.infer(obs)
    print(f"行动建议: {result['action']}")
    print(f"惊奇: {result['surprise']:.3f}")
    
    print("\n=== 测试完成 ===")
