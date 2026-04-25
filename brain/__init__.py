"""
New Brain - Core Cognitive Architecture

Part 1: Meta-Control Layer (meta_control.py)
Part 2: Default Mode Network (dmn.py)
Part 3: Task-Positive Network (tpn.py)
Part 4: Value System (value_system.py)
Part 5: Connectome Layer (connectome.py)
Part 6: Friston Kernel + Memory Layer (memory.py, friston_kernel.py)
Part 7: Integration Theory
Part 8: DMN Control + Dreams
"""

from .memory import MemoryManager, HotMemory, WarmMemory, ColdMemory
from .friston_kernel import FristonKernel

__all__ = [
    'MemoryManager',
    'HotMemory',
    'WarmMemory',
    'ColdMemory',
    'FristonKernel'
]
