#!/usr/bin/env python
"""
Ollama Chat Client Using Direct API Requests

This module provides a command-line interface for interacting with Ollama models
via direct HTTP requests to the Ollama API instead of using the ollama Python package.
It allows users to send prompts to various LLM models and maintains a conversation history.
"""

import sys
import json
import requests
import os
from typing import Dict, List, Any, Optional, Generator


class ChatModel:
    """
    A class for managing chat interactions with Ollama models using direct API requests.

    This class handles sending prompts to Ollama models, receiving
    and streaming responses, and maintaining conversation history.
    """

    def __init__(
        self,
        model_name: str = "deepseek-r1",
        log_file: Optional[str] = None,
        ollama_host: str = "http://localhost:11434",
    ) -> None:
        """
        Initialize the ChatModel with a specific model, log file, and API host.

        Args:
            model_name (str): Name of the Ollama model to use (default: "deepseek-r1")
            log_file (str): Path to store conversation history (default: None - uses ~/.ollama_logs)
            ollama_host (str): URL of the Ollama API server (default: "http://localhost:11434")
        """
        self.model_name = model_name
        self.ollama_host = os.environ.get("OLLAMA_HOST", ollama_host)

        # Ensure the host URL has a proper scheme and port
        if not self.ollama_host.startswith(("http://", "https://")):
            self.ollama_host = f"http://{self.ollama_host}"

        # Make sure the port is specified if not already in the URL
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
            log_dir = os.path.expanduser("~/.ollama_logs")
            os.makedirs(log_dir, exist_ok=True)
            self.log_file = os.path.join(
                log_dir,
                f"{self.model_name.replace('/','_').replace(':','_')}_conversation_log.json"
            )
        else:
            self.log_file = log_file

        # Load previous conversation history, if available
        self.messages = self.load_messages()

        # API endpoints
        self.api_chat = f"{self.ollama_host}/api/chat"
        self.api_list = f"{self.ollama_host}/api/tags"

    def test_connection(self) -> bool:
        """
        Test the connection to the Ollama API.

        Returns:
            bool: True if connection is successful, False otherwise
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
        """
        Load messages from the JSON log file to rebuild the message history.

        Returns:
            list: List of message dictionaries or an empty list if the file doesn't exist
        """
        try:
            with open(self.log_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return an empty list if the log file does not exist or is corrupt
            return []

    def log_messages(self) -> None:
        """
        Logs all messages to the specified JSON log file.
        """
        with open(self.log_file, "w") as file:
            json.dump(self.messages, file, indent=4)

    def list_models(self) -> Dict[str, Any]:
        """
        Lists available Ollama models.

        Returns:
            dict: Dictionary containing information about available models
        """
        try:
            response = requests.get(self.api_list)
            if response.status_code == 200:
                models_data = response.json()
                # Ollama API returns models in a "models" array
                return models_data
            else:
                print(f"Error retrieving models: {response.status_code}")
                print(f"Response: {response.text}")
                return {"models": []}
        except requests.exceptions.RequestException as e:
            print(f"Request error while listing models: {e}")
            return {"models": []}

    def stream_chat(
        self, payload: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream chat responses from the Ollama API.

        Args:
            payload (dict): Request payload with model and messages

        Yields:
            dict: Each chunk of the streaming response
        """
        try:
            with requests.post(self.api_chat, json=payload, stream=True) as response:
                if response.status_code != 200:
                    print(f"Error: Server returned status code {response.status_code}")
                    print(f"Response: {response.text}")
                    return

                # Process the streaming response
                for line in response.iter_lines():
                    if line:
                        try:
                            # Decode bytes to string
                            line_str = line.decode("utf-8")
                            chunk = json.loads(line_str)
                            yield chunk
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON: {line}")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return

    def chat(self, prompt: str = "Hello, how are you?") -> str:
        """
        Send the prompt to the model, stream responses, and log them.

        Args:
            prompt (str): User's input to send to the model

        Returns:
            str: The full response from the model
        """
        # Append the user's prompt to the message history
        user_message = {"role": "user", "content": prompt}
        self.messages.append(user_message)

        # Prepare the API request payload
        payload = {"model": self.model_name, "messages": self.messages, "stream": True}

        # Stream the response from the API
        full_response = ""
        for chunk in self.stream_chat(payload):
            if "message" in chunk and "content" in chunk["message"]:
                content = chunk["message"]["content"]
                print(content, end="", flush=True)
                full_response += content

        # Append the full model response to the message history
        model_message = {"role": "assistant", "content": full_response}
        self.messages.append(model_message)

        # Update the log file with the new messages
        self.log_messages()

        return full_response


def format_model_size(size_bytes: int) -> str:
    """
    Format model size from bytes to gigabytes.

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted size string in GB
    """
    return f"{size_bytes/1024/1024/1024:.3f} Gb"


def format_date(date_str: str) -> str:
    """
    Format date string to YYYY-MM-DD.

    Args:
        date_str (str): Date string in ISO format

    Returns:
        str: Formatted date string
    """
    if "T" in date_str:
        return date_str.partition("T")[0]
    return date_str


def main():
    """
    Main function that handles command line input and model selection.

    If command line arguments are provided, they are treated as the prompt.
    Otherwise, the user is prompted to select a model and provide input.
    """
    # Create a temporary ChatModel instance to test connection and list models
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    temp_model = ChatModel(ollama_host=ollama_host)
    
    # Check if any command line arguments are provided
    if len(sys.argv) > 1:
        # Use command line arguments as the prompt
        prompt = " ".join(sys.argv[1:])
        chat_model = ChatModel(ollama_host=ollama_host)
        chat_model.chat(prompt)
        return

    # List available models
    models_data = temp_model.list_models()

    # Check if models were retrieved successfully
    if "models" in models_data and models_data["models"]:
        print("\nAvailable models:")
        for model in models_data["models"]:
            model_name = model.get("name", "Unknown")
            # Format the name to just show the base model name without tag
            base_name = model_name.partition(":")[0]
            # Some Ollama API versions might return different fields
            if "size" in model:
                model_size = format_model_size(model.get("size", 0))
            else:
                model_size = "Unknown size"

            modified_date = "Unknown"
            if "modified_at" in model:
                modified_date = format_date(model.get("modified_at", "Unknown"))

            print(
                f"Name: {base_name}, "
                f"Size: {model_size}, "
                f"Last Updated: {modified_date}"
            )
    else:
        print("No models found or error retrieving models list.")
        model_name = input("Enter model name manually: ")
        prompt = input("Please provide a prompt: ")
        chat_model = ChatModel(model_name=model_name, ollama_host=ollama_host)
        chat_model.chat(prompt)
        return

    # Get user inputs for model and prompt
    model_name = input("Which model would you like to use? ")
    prompt = input("Please provide a prompt: ")

    # Create an instance of the ChatModel class with the specified model name
    chat_model = ChatModel(model_name=model_name, ollama_host=ollama_host)

    # Call the chat method with the user's prompt
    chat_model.chat(prompt)


if __name__ == "__main__":
    main()