#!/usr/bin/env python3
from typing import Dict, List, Any, Optional, Generator
import json
import requests
import os

class ChatModel:
    """Core Ollama chat client implementation"""
    
    def __init__(
        self,
        model_name: str = "deepseek-r1",
        log_file: str = "c:\\code\\ai_stuff\\conversation_log.json",
        ollama_host: str = "http://localhost:11434",
    ) -> None:
        self.model_name = model_name
        self.ollama_host = "http://localhost:11434"

        if not self.ollama_host.startswith(("http://", "https://")):
            self.ollama_host = f"http://{self.ollama_host}"

        if ":11434" not in self.ollama_host and "//" in self.ollama_host:
            base_url = (
                self.ollama_host.split("//")[0]
                + "//"
                + self.ollama_host.split("//")[1].split("/")[0]
            )
            path = self.ollama_host[len(base_url):]
            if ":" not in base_url.split("//")[1]:
                self.ollama_host = f"{base_url}:11434{path}"

        self.log_file = (
            f"c:\\code\\ai_stuff\\"
            f"{self.model_name.replace('/','_').replace(':','_')}"
            "_conversation_log.json"
        )
        self.messages = self.load_messages()
        self.api_chat = f"{self.ollama_host}/api/chat"
        self.api_list = f"{self.ollama_host}/api/tags"

    # [All other methods from ChatModel would go here...]

def format_model_size(size_bytes: int) -> str:
    return f"{size_bytes/1024/1024/1024:.3f} Gb"

def format_date(date_str: str) -> str:
    if "T" in date_str:
        return date_str.partition("T")[0]
    return date_str