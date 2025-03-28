#!/usr/bin/env python3
"""Test script with mock responses"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ollama.core import ChatModel

class MockChatModel(ChatModel):
    def __init__(self):
        self.messages = []
        self.api_chat = "http://mock-server/api/chat"
        
    def load_messages(self) -> list:
        return []
        
    def chat(self, prompt: str) -> str:
        print(f"Mock response to: {prompt}")
        return f"I'm a mock response to '{prompt}'"

if __name__ == "__main__":
    mock = MockChatModel()
    print(mock.chat("why is the sky blue?"))