#!/usr/bin/env python3
"""Test script with mock responses"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ollama.core import ChatModel

class MockChatModel(ChatModel):
    """Mock implementation for testing"""
    def __init__(self) -> None:
        super().__init__()
        self.api_chat = "http://mock-server/api/chat"
        self.test_responses = {
            "success": {"message": {"content": "Mock response"}},
            "error": {"error": "Test error"}
        }
        
    def load_messages(self) -> List[Dict[str, str]]:
        return []
        
    def chat(self, prompt: str) -> str:
        """Mock chat implementation for testing"""
        print(f"Mock response to: {prompt}")
        return f"I'm a mock response to '{prompt}'"

if __name__ == "__main__":
    mock = MockChatModel()
    print(mock.chat("why is the sky blue?"))
