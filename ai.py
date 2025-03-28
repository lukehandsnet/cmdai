#!/usr/bin/env python3
"""Command-line interface for Ollama chat client"""

import sys
from ollama.core import ChatModel

def main():
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        chat_model = ChatModel()
        chat_model.chat(prompt)
    else:
        print("Usage: ai [prompt]")
        print("Example: ai why is the sky blue?")

if __name__ == "__main__":
    main()