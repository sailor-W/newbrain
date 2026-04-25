#!/usr/bin/env python3
"""
New Brain Daemon - 常驻记忆系统

启动后：
- 每 30秒 自动压缩热记忆 → 温记忆
- 每 60秒 DMN 漫游（空闲时生成梦境）
- 每 300秒 温记忆 → 冷记忆固化
- 状态实时写入 brain/state.json（供 OpenClaw 快速读取）
- 输入通过 brain/input.txt / brain/response.txt 文件通信

用法：
  python3 brain_daemon.py start   # 后台启动
  python3 brain_daemon.py stop    # 停止
  python3 brain_daemon.py status  # 查看状态
"""

import os
import sys
import time
import json
import signal
import subprocess
import random
from pathlib import Path

# 把 newbrain 加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PIDFILE = '/tmp/newbrain_daemon.pid'
STATE_FILE = os.path.join(os.path.dirname(__file__), 'brain', 'state.json')
INPUT_FILE = os.path.join(os.path.dirname(__file__), 'brain', 'input.txt')
RESPONSE_FILE = os.path.join(os.path.dirname(__file__), 'brain', 'response.txt')
LOG_FILE = '/tmp/newbrain_daemon.log'

class SuppressPrint:
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')
        return self
    def __exit__(self, *args):
        sys.stdout = self._stdout

def write_state(brain, extra=None):
    """把当前状态写入 JSON 文件"""
    status = brain.get_status()
    vs = status['value_system']
    em = vs['emotion'] if isinstance(vs['emotion'], dict) else {'valence': 0.0, 'arousal': 0.5}
    state = {
        "timestamp": time.time(),
        "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
        "system_state": status['meta_control']['system_state'],
        "creativity_mode": status['meta_control']['creativity_mode'],
        "emotion": vs['emotion_label'],
        "emotion_valence": em.get('valence', 0.0),
        "emotion_arousal": em.get('arousal', 0.5),
        "hot_count": status['memory']['hot']['chunks_count'],
        "warm_count": status['memory']['warm']['episodes_count'],
        "cold_beliefs": len(brain.memory.cold.beliefs) if hasattr(brain.memory.cold, 'beliefs') else 0,
        "cold_dreams": len(brain.memory.cold.dream_fragments) if hasattr(brain.memory.cold, 'dream_fragments') else 0,
        "identity_anchors": len(brain.memory.cold.identity_anchors) if hasattr(brain.memory.cold, 'identity_anchors') else 0,
        "narrative_count": len(brain.memory.cold.self_narrative) if hasattr(brain.memory.cold, 'self_narrative') else 0,
        "idle_time": brain.idle_time,
        "dream_count": len(brain.dmn.dream_log) if hasattr(brain, 'dmn') else 0,
    }
    if extra:
        state.update(extra)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def handle_input(brain):
    """检查 input.txt，有输入就处理，写入 response.txt"""
    if not os.path.exists(INPUT_FILE):
        return
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    if not content:
        return
    
    # 处理输入
    response = brain.perceive(content)
    
    # 写入响应
    with open(RESPONSE_FILE, 'w', encoding='utf-8') as f:
        f.write(response)
    
    # 清空输入（已处理）
    with open(INPUT_FILE, 'w') as f:
        f.write('')
    
    return response

def run_daemon():
    """主循环"""
    with SuppressPrint():
        from main import NewBrain
        brain = NewBrain()
    
    # 初始化状态
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    write_state(brain, {"event": "daemon_started"})
    
    # 初始化输入文件
    with open(INPUT_FILE, 'w') as f:
        f.write('')
    with open(RESPONSE_FILE, 'w') as f:
        f.write('')
    
    last_compress = 0
    last_dream = 0
    last_consolidate = 0
    
    while True:
        now = time.time()
        
        # 1. 检查输入
        handle_input(brain)
        
        # 2. 热记忆压缩（30秒）
        if now - last_compress > 30:
            compressed = brain.memory.compress()
            if compressed:
                write_state(brain, {"event": "hot_compressed", "new_episodes": len(compressed)})
            last_compress = now
        
        # 3. DMN 漫游（60秒，概率）
        if now - last_dream > 60:
            brain.idle_tick()
            if (brain.meta_control.scheduler.current_state.value == "DMN漫游" 
                or random.random() < brain.dmn.config.dream_probability):
                brain.dream_cycle()
                write_state(brain, {"event": "dream_generated", "dream_count": len(brain.dmn.dream_log)})
            last_dream = now
        
        # 4. 温记忆固化（300秒）
        if now - last_consolidate > 300:
            brain.memory.consolidate()
            write_state(brain, {"event": "warm_consolidated"})
            last_consolidate = now
        
        # 5. 定期写状态（10秒）
        write_state(brain)
        
        time.sleep(1)

def start_daemon():
    """后台启动（使用 nohup + 子进程）"""
    if os.path.exists(PIDFILE):
        with open(PIDFILE) as f:
            old_pid = f.read().strip()
        if old_pid and os.path.exists(f"/proc/{old_pid}"):
            print(f"Daemon already running (PID {old_pid})")
            return
    
    print("Starting New Brain daemon...")
    # 用 subprocess 在后台启动，输出重定向到日志
    proc = subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "_run"],
        stdout=open(LOG_FILE, 'w'),
        stderr=subprocess.STDOUT,
        start_new_session=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    with open(PIDFILE, 'w') as f:
        f.write(str(proc.pid))
    print(f"Started (PID {proc.pid}). Log: {LOG_FILE}")

def stop_daemon():
    """停止"""
    if not os.path.exists(PIDFILE):
        print("Daemon not running")
        return
    
    with open(PIDFILE) as f:
        pid = int(f.read().strip())
    
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Daemon stopped (PID {pid})")
    except ProcessLookupError:
        print("Daemon not running")
    finally:
        if os.path.exists(PIDFILE):
            os.remove(PIDFILE)

def get_status():
    """获取状态"""
    if os.path.exists(PIDFILE):
        with open(PIDFILE) as f:
            pid = f.read().strip()
        print(f"Daemon PID: {pid}")
    else:
        print("Daemon: not running")
    
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
        print(f"State file: {STATE_FILE}")
        print(f"  Time: {state['datetime']}")
        print(f"  System state: {state['system_state']}")
        print(f"  Emotion: {state['emotion']} (valence={state['emotion_valence']:+.2f})")
        print(f"  Hot: {state['hot_count']} chunks")
        print(f"  Warm: {state['warm_count']} episodes")
        print(f"  Cold: {state['cold_beliefs']} beliefs, {state['cold_dreams']} dreams")
        print(f"  Dreams generated: {state['dream_count']}")
    else:
        print("State file: not found")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: brain_daemon.py [start|stop|status|_run]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "start":
        start_daemon()
    elif cmd == "stop":
        stop_daemon()
    elif cmd == "status":
        get_status()
    elif cmd == "_run":
        run_daemon()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
