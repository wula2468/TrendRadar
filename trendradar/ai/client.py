# coding=utf-8
"""
AI 客户端模块

基于 LiteLLM 的统一 AI 模型接口
支持 100+ AI 提供商（OpenAI、DeepSeek、Gemini、Claude、国内模型等）
"""

import os
from typing import Any, Dict, List, Optional

from litellm import completion


class AIClient:
    """统一的 AI 客户端（基于 LiteLLM）"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 AI 客户端

        Args:
            config: AI 配置字典
                - MODEL: 模型标识（格式: provider/model_name）
                - API_KEY: API 密钥
                - API_BASE: API 基础 URL（可选）
                - TEMPERATURE: 采样温度
                - MAX_TOKENS: 最大生成 token 数
                - TIMEOUT: 请求超时时间（秒）
                - NUM_RETRIES: 重试次数（可选）
                - FALLBACK_MODELS: 备用模型列表（可选）
        """
        self.model = config.get("MODEL", "deepseek/deepseek-chat")
        self.api_key = config.get("API_KEY") or os.environ.get("AI_API_KEY", "")
        self.api_base = config.get("API_BASE", "")
        self.temperature = config.get("TEMPERATURE", 1.0)
        self.max_tokens = config.get("MAX_TOKENS", 5000)
        self.timeout = config.get("TIMEOUT", 120)
        self.num_retries = config.get("NUM_RETRIES", 2)
        self.fallback_models = config.get("FALLBACK_MODELS", [])

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        调用 AI 模型进行对话

        Args:
            messages: 消息列表，格式: [{"role": "system/user/assistant", "content": "..."}]
            **kwargs: 额外参数，会覆盖默认配置

        Returns:
            str: AI 响应内容

        Raises:
            Exception: API 调用失败时抛出异常
        """
        # 如果有自定义 API Base，使用 requests 直接调用
        if self.api_base:
            return self._chat_with_requests(messages, **kwargs)
        
        # 否则使用 LiteLLM
        return self._chat_with_litellm(messages, **kwargs)
    
    def _chat_with_requests(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """使用 requests 直接调用 OpenAI 兼容 API"""
        import requests
        
        # 构建请求参数
        payload = {
            "model": self.model.replace("openai/", ""),  # 移除 openai/ 前缀
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
        }
        
        # 添加 max_tokens（如果配置了且不为 0）
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        if max_tokens and max_tokens > 0:
            payload["max_tokens"] = max_tokens
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 调用 API
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                json=payload,
                headers=headers,
                timeout=kwargs.get("timeout", self.timeout)
            )
            
            if response.status_code != 200:
                raise Exception(f"API 返回错误 (状态码 {response.status_code}): {response.text}")
            
            result = response.json()
            
            # 提取内容
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    content = choice["message"]["content"]
                    return content if content else ""
            
            raise Exception("响应格式异常，无法提取内容")
            
        except requests.exceptions.Timeout:
            raise Exception(f"API 请求超时 (timeout={self.timeout}s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {type(e).__name__}: {str(e)}")
    
    def _chat_with_litellm(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """使用 LiteLLM 调用（保留作为备用）"""
    def _chat_with_litellm(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """使用 LiteLLM 调用（保留作为备用）"""
        # 构建请求参数
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "timeout": kwargs.get("timeout", self.timeout),
            "num_retries": kwargs.get("num_retries", self.num_retries),
            # 禁用 LiteLLM 缓存和远程调用
            "cache": None,
            "no_log": True,
        }

        # 添加 API Key
        if self.api_key:
            params["api_key"] = self.api_key

        # 添加 API Base（如果配置了）
        if self.api_base:
            params["api_base"] = self.api_base

        # 添加 max_tokens（如果配置了且不为 0）
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        if max_tokens and max_tokens > 0:
            params["max_tokens"] = max_tokens

        # 添加 fallback 模型（如果配置了）
        if self.fallback_models:
            params["fallbacks"] = self.fallback_models

        # 合并其他额外参数
        for key, value in kwargs.items():
            if key not in params:
                params[key] = value

        # 调用 LiteLLM
        try:
            print(f"[LiteLLM 调试] 开始调用 API...")
            print(f"[LiteLLM 调试] Model: {params['model']}")
            print(f"[LiteLLM 调试] Messages 数量: {len(messages)}")
            
            response = completion(**params)
            
            print(f"[LiteLLM 调试] API 调用成功")
            print(f"[LiteLLM 调试] Response 类型: {type(response)}")
            print(f"[LiteLLM 调试] Response: {response}")
            
            # 提取响应内容
            if response is None:
                print(f"[LiteLLM 调试] Response 为 None！")
                return ""
            
            if not hasattr(response, 'choices') or not response.choices:
                print(f"[LiteLLM 调试] Response 没有 choices 属性或为空")
                return ""
            
            if not response.choices[0].message:
                print(f"[LiteLLM 调试] Response.choices[0].message 为空")
                return ""
            
            content = response.choices[0].message.content
            print(f"[LiteLLM 调试] 提取到的内容长度: {len(content) if content else 0}")
            
            return content if content else ""
            
        except Exception as e:
            print(f"[LiteLLM 错误] API 调用失败: {type(e).__name__}: {str(e)}")
            import traceback
            print("[LiteLLM 错误] 完整堆栈:")
            traceback.print_exc()
            
            # 如果是 NoneType 错误，打印更多调试信息
            if "'NoneType'" in str(e):
                print("[LiteLLM 错误] 可能是 API 响应格式问题")
                print(f"[LiteLLM 错误] Params: model={params.get('model')}, api_base={params.get('api_base')}")
                print(f"[LiteLLM 错误] API Key 长度: {len(params.get('api_key', '')) if params.get('api_key') else 0}")
            
            raise

    def validate_config(self) -> tuple[bool, str]:
        """
        验证配置是否有效

        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not self.model:
            return False, "未配置 AI 模型（model）"

        if not self.api_key:
            return False, "未配置 AI API Key，请在 config.yaml 或环境变量 AI_API_KEY 中设置"

        # 验证模型格式（应该包含 provider/model）
        if "/" not in self.model:
            return False, f"模型格式错误: {self.model}，应为 'provider/model' 格式（如 'deepseek/deepseek-chat'）"

        return True, ""
