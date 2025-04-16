#!/usr/bin/env python3
"""Main entry point for the Ollama chat client program."""

import sys
import io
from src.ollama_client import main

# Force UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

if __name__ == "__main__":
    main()
