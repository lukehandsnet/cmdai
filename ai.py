#!/usr/bin/env python3

# ceate a readme.md for this project .AI!
"""Command-line interface for Ollama chat client"""

import sys
from src.ollama.core import ChatModel, list_models_interactive


def main() -> None:
    """Main entry point for the CLI"""
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
