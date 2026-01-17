import os
import json
import httpx
from typing import AsyncGenerator
import asyncio

class LLMAgent:
    def __init__(self, settings: dict):
        self.settings = settings
        self.provider = settings.get("provider", "local")
        self.api_key = settings.get("api_key", "")
        self.base_url = settings.get("base_url", "")
        self.model_name = settings.get("model_name", "llama3")
        self.temperature = settings.get("temperature", 0.7)
        
        # Configure endpoints
        if self.provider == "local":
            if not self.base_url:
                self.base_url = "http://localhost:11434/v1" # Default Ollama
        elif self.provider == "openai":
            if not self.base_url:
                self.base_url = "https://api.openai.com/v1"
        elif self.provider == "anthropic":
             if not self.base_url:
                self.base_url = "https://api.anthropic.com/v1"
        elif self.provider == "gemini":
            if not self.base_url:
                # Use Google's OpenAI-compatible endpoint
                self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
        elif self.provider == "deepseek":
            if not self.base_url:
                self.base_url = "https://api.deepseek.com"
        elif self.provider == "siliconflow":
            if not self.base_url:
                self.base_url = "https://api.siliconflow.cn/v1"
        elif self.provider == "groq":
            if not self.base_url:
                self.base_url = "https://api.groq.com/openai/v1"
        elif self.provider == "custom":
            # For custom, user MUST provide base_url. 
            # If it's a proxy like minimax, they might mimic OpenAI or Anthropic format.
            # Here we assume OpenAI-compatible format for simplicity as it's most common for proxies.
            pass

    async def chat_stream(self, messages: list, context_data: str = "") -> AsyncGenerator[str, None]:
        """
        Streams response from the configured LLM provider.
        """
        
        system_prompt = self._build_system_prompt(context_data)
        
        # Prepend system prompt to messages
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Handle Anthropic specific headers if needed, but for now assuming OpenAI compatible or proxy
        # If the user is using the specific Minimax/Anthropic proxy, it usually mimics OpenAI API format 
        # OR native Anthropic. Given the key format sk-..., it looks like OpenAI compatible or proprietary.
        # But the URL says /anthropic. This is tricky. 
        # SAFEST BET: Use standard OpenAI-compatible chat/completions endpoint structure first.
        
        payload = {
            "model": self.model_name,
            "messages": full_messages,
            "temperature": self.temperature,
            "stream": True
        }

        endpoint = f"{self.base_url}/chat/completions"
        
        # Adjust for Ollama/Local
        if self.provider == "local":
             # Ollama is OpenAI compatible at /v1/chat/completions
             pass

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield f"Error: {response.status_code} - {error_text.decode()}"
                        return

                    has_yielded = False
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                # Check for error in chunk
                                if "error" in chunk:
                                    error_msg = chunk['error']
                                    if isinstance(error_msg, dict):
                                         error_msg = error_msg.get("message", str(error_msg))
                                    yield f"Error: {error_msg}"
                                    has_yielded = True
                                    continue
                                
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                                    has_yielded = True
                            except json.JSONDecodeError:
                                continue
                    
                    if not has_yielded:
                        yield "Error: No response from AI provider. Check your settings (API Key, Base URL, Model) and ensure the service is running."
        except Exception as e:
            yield f"Connection Error: {str(e)}"

    def _build_system_prompt(self, context_data: str) -> str:
        base_prompt = """You are an expert Quantitative Finance AI Assistant for the OmniAlpha platform. 
Your goal is to help users analyze markets, write Python strategy code, and explain financial concepts.
"""
        if context_data:
            base_prompt += f"\n\nMARKET CONTEXT:\n{context_data}\n"
            
        permission = self.settings.get("permission_level", "consultant")
        
        if permission == "coding":
            base_prompt += "\nYou are authorized to generate Python code for strategies. Ensure code is safe and follows best practices."
        elif permission == "copilot":
             base_prompt += "\nYou are a Co-pilot. You can suggest actions and generate full executable configurations."
        else:
            base_prompt += "\nYou are a Consultant. Focus on explaining concepts and analysis. Do not generate executable code unless explicitly asked for educational purposes."

        return base_prompt