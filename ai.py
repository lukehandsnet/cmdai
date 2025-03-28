#!/usr/bin/env python3
"""Command-line interface for Ollama chat client"""

import sys
from src.ollama.core import ChatModel

def main():
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        chat_model = ChatModel()
        chat_model.chat(prompt)
    else:
        # If no args provided, run the interactive version from core.py
        from ollama.core import main as core_main
        core_main()

if __name__ == "__main__":
    main()