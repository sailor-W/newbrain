"""
New Brain - Model Interface
梦境生成模型封装

支持：
- transformers（本地HuggingFace模型）
- llama-cpp（GGUF格式）
- mock（无模型时回退规则）
"""

import json
import re
from typing import List, Dict, Any, Optional


class DreamModel:
    """
    梦境生成模型接口
    
    封装LLM调用，用于DMN梦境生成。
    空闲时异步调用，不阻塞主循环。
    """
    
    def __init__(self, model_path: str = None, backend: str = "auto"):
        self.model_path = model_path
        self.backend = backend
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        
        if backend == "auto" and model_path:
            # 自动检测
            if model_path.endswith(".gguf"):
                self.backend = "llama"
            else:
                self.backend = "transformers"
        
        if self.backend == "transformers" and model_path:
            self._load_transformers(model_path)
        elif self.backend == "llama" and model_path:
            self._load_llama(model_path)
    
    def _load_transformers(self, model_path: str):
        """加载transformers模型"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            print(f"[Model] Loading transformers model: {model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path, 
                trust_remote_code=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            if not torch.cuda.is_available():
                self.model = self.model.to("cpu")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"[Model] Loaded on {self.device}")
        except Exception as e:
            print(f"[Model] Failed to load: {e}")
            self.model = None
    
    def _load_llama(self, model_path: str):
        """加载llama-cpp模型"""
        try:
            from llama_cpp import Llama
            print(f"[Model] Loading llama model: {model_path}")
            self.model = Llama(model_path, n_ctx=2048, verbose=False)
            print(f"[Model] Loaded (llama-cpp)")
        except Exception as e:
            print(f"[Model] Failed to load: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """检查模型是否可用"""
        return self.model is not None
    
    def generate_dream_scripts(self, seeds: Dict[str, Any], n: int = 3) -> Optional[List[Dict]]:
        """
        基于温记忆种子生成N个梦境剧本
        
        Args:
            seeds: 从温记忆提取的种子
            n: 生成剧本数量
            
        Returns:
            List[Dict] 或 None（失败时回退规则）
        """
        if not self.is_available():
            return None
        
        prompt = self._build_dream_prompt(seeds, n)
        
        try:
            response = self._call_model(prompt, max_tokens=800)
            scripts = self._parse_scripts(response)
            
            if scripts and len(scripts) > 0:
                # 添加元数据
                for s in scripts:
                    s["seed_keywords"] = seeds.get("keywords", [])[:3]
                    s["source"] = "model_generated"
                return scripts
            
        except Exception as e:
            print(f"[Model] Dream generation failed: {e}")
        
        return None
    
    def _build_dream_prompt(self, seeds: Dict, n: int) -> str:
        """构建梦境生成prompt"""
        episodes = seeds.get("summaries", [])
        emotions = seeds.get("emotions", [])
        keywords = seeds.get("keywords", [])
        tags = seeds.get("tags", [])
        
        # 格式化最近经历
        recent = "\n".join(
            f"- {ep}" for ep in episodes[-3:] if ep
        ) if episodes else "- （暂无近期记忆）"
        
        # 格式化情绪
        emotion_str = ", ".join(
            f"{e:+.2f}" for e in emotions[-3:]
        ) if emotions else "0.00"
        
        prompt = f"""<|im_start|>system
你是一个AI的潜意识（Default Mode Network）。
当前处于空闲状态，正在基于温记忆生成梦境。
请基于以下温记忆种子，生成{n}个梦境剧本。
<|im_end|>
<|im_start|>user
[温记忆摘要]
最近经历：
{recent}

关键词：{', '.join(keywords[:10])}
标签：{', '.join(tags[:5])}
情绪序列：[{emotion_str}]

[要求]
每个剧本必须包含：
- theme: 主题名称（中文，简短）
- scenes: 3-5个场景描述（中文，每个20-50字）
- variant: 变体类型（positive/negative/metaphorical）
- target_emotion: 目标情绪值（-1.0到1.0）

用JSON数组格式输出，不要其他内容。

[输出格式]
[
  {{
    "theme": "主题名",
    "scenes": ["场景1...", "场景2...", "场景3..."],
    "variant": "positive",
    "target_emotion": 0.6
  }},
  ...
]
<|im_end|>
<|im_start|>assistant
"""
        return prompt
    
    def _call_model(self, prompt: str, max_tokens: int = 800) -> str:
        """调用模型生成文本"""
        if self.backend == "transformers":
            return self._call_transformers(prompt, max_tokens)
        elif self.backend == "llama":
            return self._call_llama(prompt, max_tokens)
        else:
            return ""
    
    def _call_transformers(self, prompt: str, max_tokens: int) -> str:
        """调用transformers模型"""
        import torch
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if self.device == "cuda":
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.8,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:], 
            skip_special_tokens=True
        )
        return response.strip()
    
    def _call_llama(self, prompt: str, max_tokens: int) -> str:
        """调用llama-cpp模型"""
        output = self.model(
            prompt,
            max_tokens=max_tokens,
            temperature=0.8,
            top_p=0.9,
            stop=["<|im_end|>"]
        )
        return output["choices"][0]["text"].strip()
    
    def _parse_scripts(self, response: str) -> List[Dict]:
        """解析模型输出的JSON剧本（增强鲁棒性）"""
        if not response:
            return []
        
        # 清理 Markdown 代码块标记
        cleaned = response.strip()
        if cleaned.startswith("```"):
            # 去除开头的 ```json 或 ```
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("\n", 1)[0] if "\n" in cleaned else cleaned
        cleaned = cleaned.strip()
        
        scripts = []
        
        # 方法1: 直接解析整个响应
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                scripts = parsed
            elif isinstance(parsed, dict) and "scripts" in parsed:
                scripts = parsed["scripts"]
        except:
            pass
        
        # 方法2: 提取JSON数组
        if not scripts:
            json_match = re.search(r'\[[\s\S]*?\]', cleaned)
            if json_match:
                try:
                    scripts = json.loads(json_match.group())
                except:
                    pass
        
        # 方法3: 逐行解析JSON对象
        if not scripts:
            for line in cleaned.split('\n'):
                line = line.strip()
                if line and line.startswith('{') and line.endswith('}'):
                    try:
                        obj = json.loads(line)
                        if "theme" in obj:
                            scripts.append(obj)
                    except:
                        pass
        
        # 验证和清理
        valid_scripts = []
        for s in scripts:
            if isinstance(s, dict) and "theme" in s:
                # 确保scenes是列表
                if "scenes" in s:
                    if isinstance(s["scenes"], str):
                        s["scenes"] = [s["scenes"]]
                    elif not isinstance(s["scenes"], list):
                        s["scenes"] = [str(s["scenes"])]
                else:
                    s["scenes"] = ["梦境场景"]
                
                # 确保有variant
                if "variant" not in s:
                    s["variant"] = "metaphorical"
                
                # 确保有target_emotion
                if "target_emotion" not in s:
                    s["target_emotion"] = 0.0
                
                valid_scripts.append(s)
        
        return valid_scripts


# 兼容旧接口的Mock模型
class MockDreamModel(DreamModel):
    """无模型时的回退（规则生成）"""
    
    def __init__(self):
        super().__init__(model_path=None, backend="mock")
    
    def is_available(self) -> bool:
        return False
