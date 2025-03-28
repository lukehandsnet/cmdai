from typing import Dict, List, Any, Optional, Generator
import json
import requests
import os
import sys

class ChatModel:
    """
    A class for managing chat interactions with Ollama models using direct API requests.
    This class handles sending prompts to Ollama models, receiving
    and streaming responses, and maintaining conversation history.
    """

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

    def test_connection(self) -> bool:
        try:
            test_url = f"{self.ollama_host}/api/version"
            print(f"Testing connection to: {test_url}")
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                print(f"Successfully connected to Ollama. Version: {version_info.get('version', 'unknown')}")
                return True
            else:
                print(f"Connection test failed with status code: {response.status_code}")
                print(f"Response text: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Connection test failed: {e}")
            print("\nTroubleshooting tips:")
            print("1. Make sure Ollama is running")
            print("2. Check if the host and port are correct (default: localhost:11434)")
            print("3. If using a custom OLLAMA_HOST, ensure it includes the protocol and port")
            return False

    # [Additional methods would continue here...]

def main():
    """Main entry point for command-line usage"""
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        chat_model = ChatModel(ollama_host=ollama_host)
        chat_model.chat(prompt)
        return

    # [Rest of main() implementation...]