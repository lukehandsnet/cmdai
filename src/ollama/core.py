#!/usr/bin/env python
"""
Ollama Chat Client Using Direct API Requests

This module provides the core implementation for interacting with Ollama models
via direct HTTP requests to the Ollama API.
"""

import sys
import json
import requests
import os
import configparser
from typing import Dict, List, Any, Optional, Generator

# Read configuration
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../../config.ini'))


class ChatModel:
    """
    A class for managing chat interactions with Ollama models using direct API requests.
    This class handles sending prompts to Ollama models, receiving
    and streaming responses, and maintaining conversation history.
    """

    def __init__(
        self,
        model_name: str = None,
        log_file: Optional[str] = None,
        ollama_host: str = None,
    ) -> None:
        self.model_name = model_name or config.get('Defaults', 'model_name')
        self.ollama_host = ollama_host or config.get('Defaults', 'ollama_host')

        # Ensure proper URL format
        if not self.ollama_host.startswith(("http://", "https://")):
            self.ollama_host = f"http://{self.ollama_host}"

        # Ensure port is specified
        if ":11434" not in self.ollama_host and "//" in self.ollama_host:
            base_url = (
                self.ollama_host.split("//")[0]
                + "//"
                + self.ollama_host.split("//")[1].split("/")[0]
            )
            path = self.ollama_host[len(base_url):]
            if ":" not in base_url.split("//")[1]:
                self.ollama_host = f"{base_url}:11434{path}"

        # Set up log file path
        if log_file is None:
            log_dir = os.path.expanduser(config.get('Defaults', 'log_dir'))
            os.makedirs(log_dir, exist_ok=True)
            self.log_file = os.path.join(
                log_dir,
                f"{self.model_name.replace('/','_').replace(':','_')}_conversation_log.json"
            )
        else:
            self.log_file = log_file

        self.messages = self.load_messages()
        self.api_chat = f"{self.ollama_host}/api/chat"
        self.api_list = f"{self.ollama_host}/api/tags"

    def test_connection(self) -> bool:
        """Test connection to Ollama API"""
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

    def load_messages(self) -> List[Dict[str, str]]:
        """Load conversation history from log file"""
        try:
            with open(self.log_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []  # Return empty list if file doesn't exist or is corrupt

    def log_messages(self) -> None:
        """Save current conversation history to log file"""
        with open(self.log_file, "w") as file:
            json.dump(self.messages, file, indent=4)

    def list_models(self) -> Dict[str, Any]:
        """List available Ollama models"""
        try:
            response = requests.get(self.api_list)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error retrieving models: {response.status_code}")
                return {"models": []}
        except requests.exceptions.RequestException as e:
            print(f"Request error while listing models: {e}")
            return {"models": []}

    def stream_chat(self, payload: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """Stream chat responses from Ollama API"""
        try:
            with requests.post(self.api_chat, json=payload, stream=True) as response:
                if response.status_code != 200:
                    print(f"Error: Server returned status code {response.status_code}")
                    return

                for line in response.iter_lines():
                    if line:
                        try:
                            yield json.loads(line.decode("utf-8"))
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON: {line}")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

    def chat(self, prompt: str) -> str:
        """Send prompt to model and return response"""
        user_message = {"role": "user", "content": prompt}
        self.messages.append(user_message)

        payload = {
            "model": self.model_name,
            "messages": self.messages,
            "stream": True
        }

        full_response = ""
        for chunk in self.stream_chat(payload):
            if "message" in chunk and "content" in chunk["message"]:
                content = chunk["message"]["content"]
                print(content, end="", flush=True)
                full_response += content

        model_message = {"role": "assistant", "content": full_response}
        self.messages.append(model_message)
        self.log_messages()
        return full_response


def format_model_size(size_bytes: int) -> str:
    """Format bytes to GB string"""
    return f"{size_bytes/1024/1024/1024:.3f} Gb"


def format_date(date_str: str) -> str:
    """Format ISO date to YYYY-MM-DD"""
    if "T" in date_str:
        return date_str.partition("T")[0]
    return date_str


def main():
    """Command line entry point"""
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        chat_model = ChatModel(ollama_host=ollama_host)
        chat_model.chat(prompt)
        return

    temp_model = ChatModel(ollama_host=ollama_host)
    models_data = temp_model.list_models()

    if "models" in models_data and models_data["models"]:
        print("\nAvailable models:")
        for model in models_data["models"]:
            name = model.get("name", "Unknown").partition(":")[0]
            size = format_model_size(model.get("size", 0)) if "size" in model else "Unknown"
            modified = format_date(model.get("modified_at", "Unknown"))
            print(f"Name: {name}, Size: {size}, Last Updated: {modified}")
    else:
        print("No models found")

    model_name = input("\nWhich model would you like to use? ")
    prompt = input("Enter your prompt: ")
    ChatModel(model_name=model_name, ollama_host=ollama_host).chat(prompt)


if __name__ == "__main__":
    main()