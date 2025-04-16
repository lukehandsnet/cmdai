#!/usr/bin/env python3
"""Test suite for Ollama chat client using mock responses.

Contains MockChatModel class that simulates API responses for testing.
Allows testing of core functionality without requiring a live Ollama server.

Test Cases:
- Basic chat response simulation
- Error case simulation
- Message history handling
"""

import sys
import os
from typing import Dict, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ollama.core import ChatModel

class MockChatModel(ChatModel):
    """Simulates ChatModel for testing purposes.

    Overrides actual API calls with predefined responses.
    Allows isolated testing of chat logic without network dependencies.

    Attributes:
        test_responses (Dict[str, Any]): Dictionary of response templates
            - success: Normal chat response
            - error: Error case response
    """
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
