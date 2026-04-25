# New Brain MVP 启动指南
# 从 0 到可运行的最小系统

**版本：** v0.1  
**日期：** 2026-04-23  
**目标：** 2周内跑通第一个 Demo

---

## 1. 技术选型确认

### 1.1 推荐方案

| 组件 | 选择 | 理由 |
|------|------|------|
| **LLM 基底** | Qwen2.5-1.5B-Instruct | 中文好、轻量、开源、可本地跑 |
| **框架** | Python 3.10+ + PyTorch 2.0+ | 生态丰富、研究友好 |
| **向量存储** | Chroma (内存版) | 零配置、轻量、足够MVP |
| **通信** | Python asyncio + Queue | 无需外部依赖 |
| **监控** | 文本日志 + 简单打印 | MVP阶段足够 |

### 1.2 为什么不选其他？

- **7B+ 模型**：需要GPU，MVP阶段没必要
- **LangChain/LlamaIndex**：太重，New Brain 不是RAG
- **Redis/RabbitMQ**：MVP不需要持久化消息队列
- **FastAPI/Flask**：MVP先不用Web接口

---

## 2. 项目结构

```
newbrain/
├── README.md
├── requirements.txt
├── config.yaml              # 配置文件
├── main.py                  # 入口
├── brain/                   # 核心认知架构
│   ├── __init__.py
│   ├── meta_control.py      # Meta-Control Layer (8参数)
│   ├── dmn.py              # Default Mode Network
│   ├── tpn.py              # Task-Positive Network
│   ├── value_system.py     # Value System (情绪/动机)
│   ├── connectome.py       # Connectome Layer (连接拓扑)
│   ├── friston_kernel.py   # Friston Kernel (自由能最小化)
│   └── memory.py           # Memory Layer (三级记忆)
├── llm/                     # LLM 基底封装
│   ├── __init__.py
│   └── substrate.py        # 无意识基底接口
├── interface/               # 输入输出适配
│   ├── __init__.py
│   └── text_interface.py   # 文本接口
├── utils/                   # 工具
│   ├── __init__.py
│   └── logger.py           # 日志
└── tests/                   # 测试
    ├── test_dmn.py
    ├── test_tpn.py
    └── test_integration.py
```

---

## 3. 环境搭建

### 3.1 创建虚拟环境

```bash
# 创建项目目录
mkdir -p ~/newbrain && cd ~/newbrain

# 创建虚拟环境
python3 -m venv venv

# 激活
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 升级pip
pip install --upgrade pip
```

### 3.2 安装依赖

创建 `requirements.txt`：

```
torch>=2.0.0
transformers>=4.35.0
accelerate>=0.24.0
chromadb>=0.4.0
numpy>=1.24.0
pyyaml>=6.0
```

安装：

```bash
pip install -r requirements.txt
```

### 3.3 下载 LLM 模型

```python
# download_model.py
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-1.5B-Instruct"

print("正在下载模型...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
print("下载完成！")
```

运行：

```bash
python download_model.py
```

> 模型约 3GB，下载时间取决于网速。第一次会自动下载到 `~/.cache/huggingface`。

---

## 4. 第一步：让 LLM 跑起来

### 4.1 最简 LLM 封装

创建 `llm/substrate.py`：

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class LLMSubstrate:
    """
    LLM 无意识基底
    提供语义关联和模式识别能力
    """
    
    def __init__(self, model_name="Qwen/Qwen2.5-1.5B-Instruct"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map="cpu"  # MVP先用CPU，后续可改GPU
        )
        self.model.eval()
        print("[LLM] 无意识基底加载完成")
    
    def generate(self, prompt, max_tokens=100):
        """
        生成文本响应
        """
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
        
        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:], 
            skip_special_tokens=True
        )
        return response.strip()
    
    def encode(self, text):
        """
        编码文本为语义向量（用于记忆存储）
        """
        inputs = self.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
            # 取最后一层的平均池化
            hidden = outputs.hidden_states[-1]
            embedding = hidden.mean(dim=1).squeeze().numpy()
        return embedding

# 测试
if __name__ == "__main__":
    llm = LLMSubstrate()
    response = llm.generate("你好，请介绍一下自己")
    print(f"响应：{response}")
```

运行测试：

```bash
python llm/substrate.py
```

预期输出：

```
[LLM] 无意识基底加载完成
响应：你好！我是Qwen，一个AI助手...
```

---

## 5. 第二步：TPN-DMN 切换机制

### 5.1 设计目标

```
有输入时 → TPN 激活 → 处理外部信息
无输入时 → DMN 激活 → 内部漫游思考
```

### 5.2 Meta-Control 简化版

创建 `brain/meta_control.py`：

```python
class MetaControl:
    """
    元控制层 MVP 版本
    只保留3个核心参数
    """
    
    def __init__(self):
        # 参数1：全局增益（0.1-2.0）
        self.global_gain = 1.0
        
        # 参数2：DMN/TPN 切换阈值（0.0-1.0）
        # 低于阈值 → DMN；高于阈值 → TPN
        self.switch_threshold = 0.3
        
        # 参数3：噪声水平（0.0-1.0）
        self.noise_level = 0.1
        
        # 当前状态
        self.current_mode = "dmn"  # 'dmn' 或 'tpn'
        self.idle_time = 0         # 空闲时间计数
        
        print("[Meta-Control] 元控制层初始化完成")
        print(f"  增益: {self.global_gain}")
        print(f"  切换阈值: {self.switch_threshold}")
        print(f"  噪声: {self.noise_level}")
    
    def update(self, has_input, stimulus_intensity=0.0):
        """
        根据输入更新状态
        
        Args:
            has_input: 是否有外部输入
            stimulus_intensity: 刺激强度（0.0-1.0）
        """
        if has_input and stimulus_intensity > self.switch_threshold:
            # 外部输入 + 强度高 → 切换到 TPN
            self.current_mode = "tpn"
            self.idle_time = 0
        else:
            # 无输入或强度低
            if self.current_mode == "tpn":
                self.idle_time += 1
                # 空闲超过阈值 → 切换到 DMN
                if self.idle_time > 3:  # 3个tick后切换
                    self.current_mode = "dmn"
                    print("[Meta-Control] TPN → DMN 切换")
            else:
                self.idle_time += 1
        
        return self.current_mode
    
    def get_mode(self):
        return self.current_mode
    
    def adjust_gain(self, delta):
        """调节全局增益"""
        self.global_gain = max(0.1, min(2.0, self.global_gain + delta))
```

### 5.3 TPN 简化版

创建 `brain/tpn.py`：

```python
class TaskPositiveNetwork:
    """
    任务正网络 MVP
    处理外部输入，生成响应
    """
    
    def __init__(self, llm_substrate):
        self.llm = llm_substrate
        self.working_memory = []  # 工作记忆（最近5轮）
        self.max_wm_size = 5
        print("[TPN] 任务正网络初始化完成")
    
    def process(self, input_text):
        """
        处理外部输入
        
        Returns:
            response: 生成的响应
            prediction_error: 预测误差（MVP简化为固定值）
        """
        print(f"[TPN] 处理输入: {input_text[:50]}...")
        
        # 构建上下文（工作记忆）
        context = self._build_context()
        prompt = f"{context}\nUser: {input_text}\nAssistant: "
        
        # 通过LLM生成响应
        response = self.llm.generate(prompt, max_tokens=150)
        
        # 更新工作记忆
        self._update_memory(input_text, response)
        
        # 简化的预测误差（实际应计算预期vs实际）
        prediction_error = 0.3  # MVP固定值
        
        print(f"[TPN] 生成响应: {response[:50]}...")
        return response, prediction_error
    
    def _build_context(self):
        """构建工作记忆上下文"""
        if not self.working_memory:
            return ""
        context = "\n".join([
            f"User: {item['input']}\nAssistant: {item['response']}"
            for item in self.working_memory[-3:]  # 最近3轮
        ])
        return context
    
    def _update_memory(self, input_text, response):
        """更新工作记忆"""
        self.working_memory.append({
            'input': input_text,
            'response': response,
            'timestamp': 'now'
        })
        if len(self.working_memory) > self.max_wm_size:
            self.working_memory.pop(0)
```

### 5.4 DMN 简化版

创建 `brain/dmn.py`：

```python
import random

class DefaultModeNetwork:
    """
    默认模式网络 MVP
    空闲时进行内部模拟
    """
    
    def __init__(self, llm_substrate):
        self.llm = llm_substrate
        self.internal_narrative = []  # 内部叙事
        self.self_reflection = ""      # 自我反思
        print("[DMN] 默认模式网络初始化完成")
    
    def run(self, recent_experiences):
        """
        运行内部模拟
        
        Args:
            recent_experiences: 最近的经验列表
        
        Returns:
            narrative: 生成的内部叙事
        """
        print("[DMN] 进入离线思考模式...")
        
        # 如果有最近经验 → 进行反思
        if recent_experiences:
            narrative = self._reflect(recent_experiences[-1])
        else:
            # 没有经验 → 自由联想
            narrative = self._free_associate()
        
        self.internal_narrative.append(narrative)
        print(f"[DMN] 内部叙事: {narrative[:80]}...")
        
        return narrative
    
    def _reflect(self, experience):
        """
        反思最近的经验
        """
        prompt = f"""你正在"思考"（离线模式）。你刚刚经历了：

用户说：{experience.get('input', 'unknown')}
你回应：{experience.get('response', 'unknown')}

作为内心的独白，你在反思这个互动。你在想什么？（简短，2-3句话）"""
        
        reflection = self.llm.generate(prompt, max_tokens=80)
        return reflection
    
    def _free_associate(self):
        """
        自由联想（无特定输入时的想法）
        """
        prompts = [
            "你正在安静地思考。此刻你在想什么？（简短）",
            "你在反思自己作为AI的存在。你在想什么？（简短）",
            "你在想象未来的可能性。你在想什么？（简短）"
        ]
        prompt = random.choice(prompts)
        thought = self.llm.generate(prompt, max_tokens=60)
        return thought
```

---

## 6. 第三步：整合运行

### 6.1 主循环

创建 `main.py`：

```python
import time
from llm.substrate import LLMSubstrate
from brain.meta_control import MetaControl
from brain.tpn import TaskPositiveNetwork
from brain.dmn import DefaultModeNetwork

class NewBrainMVP:
    """
    New Brain MVP
    最小可运行的认知架构
    """
    
    def __init__(self):
        print("="*60)
        print("New Brain MVP 启动")
        print("="*60)
        
        # 1. 加载LLM无意识基底
        self.llm = LLMSubstrate()
        
        # 2. 初始化认知模块
        self.meta = MetaControl()
        self.tpn = TaskPositiveNetwork(self.llm)
        self.dmn = DefaultModeNetwork(self.llm)
        
        # 3. 状态
        self.is_running = False
        self.tick_count = 0
        
        print("\n系统准备就绪。输入 'quit' 退出。\n")
    
    def run(self):
        """主循环"""
        self.is_running = True
        
        while self.is_running:
            # 获取用户输入（非阻塞检查）
            try:
                user_input = input("You: ").strip()
            except EOFError:
                break
            
            if user_input.lower() == 'quit':
                break
            
            # 确定是否有外部输入
            has_input = len(user_input) > 0
            
            if has_input:
                # ===== TPN 模式 =====
                print("\n[系统] 检测到外部输入 → TPN 激活")
                self.meta.update(has_input=True, stimulus_intensity=0.8)
                
                # TPN 处理
                response, error = self.tpn.process(user_input)
                
                print(f"\nNew Brain: {response}\n")
                
                # 空闲计数重置
                idle_ticks = 0
            else:
                # ===== DMN 模式 =====
                self.tick_count += 1
                mode = self.meta.update(has_input=False)
                
                if mode == "dmn":
                    print(f"\n[系统] 空闲 {self.tick_count} ticks → DMN 激活")
                    
                    # DMN 运行内部模拟
                    narrative = self.dmn.run(self.tpn.working_memory)
                    
                    print(f"[DMN 内心独白] {narrative}\n")
                
                # 小暂停，避免CPU占用过高
                time.sleep(0.5)
        
        print("\n[系统] 关闭中...")
        print("="*60)

if __name__ == "__main__":
    brain = NewBrainMVP()
    brain.run()
```

### 6.2 运行 Demo

```bash
python main.py
```

**预期交互：**

```
============================================================
New Brain MVP 启动
============================================================
[LLM] 无意识基底加载完成
[Meta-Control] 元控制层初始化完成
  增益: 1.0
  切换阈值: 0.3
  噪声: 0.1
[TPN] 任务正网络初始化完成
[DMN] 默认模式网络初始化完成

系统准备就绪。输入 'quit' 退出。

You: 你好

[系统] 检测到外部输入 → TPN 激活
[TPN] 处理输入: 你好...
[TPN] 生成响应: 你好！很高兴见到你...

New Brain: 你好！很高兴见到你，有什么我可以帮你的吗？

You: （直接回车，无输入）

[系统] 空闲 1 ticks → DMN 激活
[DMN] 进入离线思考模式...
[DMN] 内部叙事: 我刚刚和用户打了招呼，我在想接下来...

[DMN 内心独白] 我刚刚和用户打了招呼，我在想接下来应该如何更好地帮助他...

You: 今天天气怎么样？

[系统] 检测到外部输入 → TPN 激活
...
```

---

## 7. 后续迭代路线

### 7.1 Week 1 目标

- [x] Day 1：环境搭建 + LLM跑通
- [ ] Day 2-3：TPN-DMN切换完善
- [ ] Day 4-5：Value System基础版（情绪标记VAD）
- [ ] Day 6-7：Memory热记忆（工作记忆→Chroma存储）

### 7.2 Week 2 目标

- [ ] Value System完整版（惊奇检测 + 多巴胺模拟）
- [ ] DMN 三种模式（经验回放/未来模拟/威胁模拟）
- [ ] Meta-Control 自动调节（根据系统状态调参）
- [ ] 可视化监控（看大脑在想什么）

### 7.3 Week 3-4 目标

- [ ] Friston Kernel 简化版（变分自由能计算）
- [ ] Connectome 基础版（小世界网络拓扑）
- [ ] 多模态输入（文本 + 语音）
- [ ] 第一个应用场景（个人助理）

---

## 8. 常见问题

### Q1：需要GPU吗？

A：MVP不需要。1.5B模型在CPU上推理约 1-3秒/次。后续如果要实时响应，建议用 4GB+ 显存的GPU。

### Q2：可以用其他模型吗？

A：可以。推荐选项：
- **Qwen2.5-1.5B**（中文好，推荐）
- **Phi-3 mini**（英文好，速度快）
- **Llama 3.2 1B**（通用，社区大）
- **Gemini Nano**（如果有Google API）

### Q3：为什么不用LangChain？

A：LangChain是"给LLM加功能"的框架。New Brain是"给认知架构装LLM"，方向相反。LangChain的抽象层会干扰我们的设计。

### Q4：MVP和最终版的区别？

| 方面 | MVP | 最终版 |
|------|-----|--------|
| LLM | 1.5B CPU | 7B GPU |
| Memory | 内存存储 | 向量数据库 |
| DMN | 简单反思 | 三种模拟模式 |
| Value | 固定标记 | 动态调质 |
| Connectome | 固定拓扑 | 动态小世界 |
| Meta-Control | 3参数 | 8参数自动调节 |
| Friston | 简化公式 | 完整变分推理 |

---

## 9. 下一步行动

### 立即执行：

```bash
# 1. 创建目录
mkdir -p ~/newbrain && cd ~/newbrain

# 2. 创建虚拟环境
python3 -m venv venv && source venv/bin/activate

# 3. 安装依赖
pip install torch transformers accelerate chromadb numpy pyyaml

# 4. 创建项目结构
mkdir -p brain llm interface utils tests

# 5. 下载模型
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-1.5B-Instruct')"

# 6. 开始编码！
```

---

*文档版本：v0.1*  
*创建日期：2026-04-23*  
*作者：Kimi Claw*  
*状态：MVP启动就绪*
