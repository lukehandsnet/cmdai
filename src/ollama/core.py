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
from typing import Dict, List, Any, Optional, Generator


class ChatModel:
    """Manages chat interactions with Ollama models via direct API requests.

    This class provides a complete interface for:
    - Streaming chat responses
    - Maintaining conversation history
    - Model management
    - Connection testing

    Attributes:
        model_name (str): Name of the currently selected model
        ollama_host (str): Base URL for Ollama API
        log_file (str): Path to conversation log file
        messages (List[Dict[str, str]]): Conversation history
        api_chat (str): Full URL for chat API endpoint
        api_list (str): Full URL for model listing endpoint
    """
    
    def __init__(
        self,
        model_name: str = "deepseek-r1",
        log_file: Optional[str] = None,
        ollama_host: str = "http://localhost:11434",
        max_log_size: int = 1_000_000,  # 1MB
        max_log_backups: int = 3,
    ) -> None:
        self.model_name: str = model_name
        self.ollama_host: str = ""
        self.log_file: str = ""
        self.messages: List[Dict[str, str]] = []
        self.api_chat: str = ""
        self.api_list: str = ""
        self.api_show: str = ""  # Added for model details endpoint
        self.model_name = model_name
        
        # Process and validate the host URL
        if not ollama_host.startswith(("http://", "https://")):
            ollama_host = f"http://{ollama_host}"
        
        # Ensure port is specified
        if ":" not in ollama_host.split("//")[1].split("/")[0]:
            base_url = ollama_host.split("//")[0] + "//" + ollama_host.split("//")[1].split("/")[0]
            path = ollama_host[len(base_url):]
            ollama_host = f"{base_url}:11434{path}"
        
        self.ollama_host = ollama_host.rstrip("/")

        # Set up log file path
        if log_file is None:
            log_dir = os.path.expanduser("~/.ollama_logs")
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
        self.api_show = f"{self.ollama_host}/api/show"  # Define the show endpoint URL

    def test_connection(self) -> bool:
        """Tests connection to the Ollama API server.

        Performs a health check by requesting version information from the API.
        Provides troubleshooting guidance if connection fails.

        Returns:
            bool: True if connection succeeds, False otherwise

        Raises:
            requests.exceptions.RequestException: If network issues occur
        """
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
        try:
            with open(self.log_file, "r", encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        except UnicodeDecodeError:
            # Fallback method if UTF-8 fails
            try:
                with open(self.log_file, "r", encoding='latin-1') as file:
                    return json.load(file)
            except:
                return []

    def log_messages(self) -> None:
        """Save current conversation history to log file"""
        with open(self.log_file, "w", encoding='utf-8') as file:
            json.dump(self.messages, file, indent=4, ensure_ascii=False)

    def show_model_details(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves detailed information about a specific model.

        Args:
            model_name: The name of the model to query.

        Returns:
            A dictionary containing the model details, or None if an error occurs.
        """
        payload = {"name": model_name}
        try:
            response = requests.post(self.api_show, json=payload, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (e.g., 404 Not Found)
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Error: Model '{model_name}' not found.")
            else:
                print(f"HTTP error retrieving model details for '{model_name}': {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error retrieving model details for '{model_name}': {e}")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON response for model '{model_name}'.")
            return None

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
        """Stream chat responses from Ollama API
        
        Args:
            payload: Dictionary containing chat parameters including:
                - model: str - Model name
                - messages: List[Dict[str, str]] - Conversation history
                - stream: bool - Whether to stream response
        
        Yields:
            Dict[str, Any]: Response chunks from the API
        """
        """Stream chat responses from Ollama API"""
        try:
            with requests.post(self.api_chat, json=payload, stream=True, timeout=30) as response:
                response.raise_for_status()  # Raises HTTPError for bad responses
                if response.status_code != 200:
                    print(f"Error: {response.json().get('error', 'Unknown error')}")
                    return

                for line in response.iter_lines():
                    if line:
                        try:
                            decoded_line = line.decode('utf-8', errors='replace')
                            yield json.loads(decoded_line)
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON: {line}")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

    def chat(self, prompt: str) -> str:
        """Send prompt to model and return full response
        
        Args:
            prompt: User input message
            
        Returns:
            str: Complete response from model
        """
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
                try:
                    # First try printing with default encoding
                    print(content, end="", flush=True)
                except UnicodeEncodeError:
                    try:
                        # Try Windows-specific encoding
                        if sys.platform == "win32":
                            print(content.encode('utf-8').decode('utf-8', 'backslashreplace'), end="", flush=True)
                        else:
                            print(content.encode('utf-8', errors='replace').decode('utf-8'), end="", flush=True)
                    except Exception:
                        # Ultimate fallback - print raw bytes if all else fails
                        print(str(content.encode('utf-8', errors='replace')), end="", flush=True)
                full_response += content

        model_message = {"role": "assistant", "content": full_response}
        self.messages.append(model_message)
        self.log_messages()
        return full_response


def format_model_size(size_bytes: int) -> str:
    """Format bytes to human-readable GB string
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string with 3 decimal places
    """
    """Format bytes to GB string"""
    return f"{size_bytes/1024/1024/1024:.3f} Gb"


def format_date(date_str: str) -> str:
    """Format ISO date string to YYYY-MM-DD
    
    Args:
        date_str: Date string in ISO format
        
    Returns:
        str: Date in YYYY-MM-DD format
    """
    """Format ISO date to YYYY-MM-DD"""
    if "T" in date_str:
        return date_str.partition("T")[0]
    return date_str

def list_models_interactive() -> Optional[str]:
    """Interactive model selection prompt
    
    Returns:
        Optional[str]: Selected model name or None if cancelled
    """
    """List models and prompt for selection, returns chosen model name"""
    chat_model = ChatModel()
    models_data = chat_model.list_models()

    if not models_data.get("models"):
        print("No models found. Please install models first.")
        return None

    print("\nAvailable models:")
    for i, model in enumerate(models_data["models"], 1):
        name = model.get("name", "Unknown").partition(":")[0]
        size = format_model_size(model.get("size", 0)) if "size" in model else "Unknown"
        print(f"{i}. {name} ({size})")

    while True:
        try:
            choice = input("\nSelect model by number (or 'q' to quit): ")
            if choice.lower() == 'q':
                return None
            index = int(choice) - 1
            if 0 <= index < len(models_data["models"]):
                return models_data["models"][index]["name"]
            print("Invalid selection")
        except ValueError:
            print("Please enter a number")


if __name__ == "__main__":
    print("This module is not meant to be run directly. Use ai.py instead.")
    sys.exit(1)
