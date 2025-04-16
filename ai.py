#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Command-line interface for Ollama chat client.

Features:
- Interactive chat mode
- Single-command execution
- Model selection
- Connection testing

Usage Examples:
  $ python ai.py "Explain quantum computing"
  $ python ai.py (interactive mode)
  $ OLLAMA_MODEL=llama2 python ai.py (custom model)

Environment Variables:
  OLLAMA_HOST: API server URL (default: http://localhost:11434)
  OLLAMA_MODEL: Default model name (default: deepseek-r1)
"""

import sys
import io
import locale
from src.ollama.core import ChatModel, list_models_interactive

# Configure system for UTF-8
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set locale to UTF-8
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    pass  # Fall back to system default if UTF-8 locale not available


def main() -> None:
    """Main entry point for the Ollama CLI.

    Handles both interactive and single-command modes.
    Manages model selection and connection testing.

    Command-line Arguments:
        Optional prompt string to execute in single-command mode

    Exit Codes:
        0: Success
        1: Error (connection failed or other exception)
    """
    try:
        if len(sys.argv) > 1:
            prompt = " ".join(sys.argv[1:])
            chat_model = ChatModel()
            if not chat_model.test_connection():
                sys.exit(1)
            chat_model.chat(prompt)
        else:
            chat_model = ChatModel()
            if not chat_model.test_connection():
                sys.exit(1)
            
            # Allow model selection
            selected_model = list_models_interactive()
            if selected_model:
                chat_model.model_name = selected_model
            
            print(f"\nOllama Chat - Interactive Mode (Model: {chat_model.model_name})")
            print("Enter your prompt (or 'quit' to exit):")
            while True:
                prompt = input("\n> ")
                if prompt.lower() in ('quit', 'exit'):
                    break
                if prompt.strip():
                    chat_model.chat(prompt)
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
