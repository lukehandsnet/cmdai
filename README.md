# Ollama Command Line Chat Client

A Python implementation for interacting with Ollama models via direct API requests.

## Features
- Stream chat responses from Ollama models
- Maintain conversation history
- List available models
- Cross-platform support

## Project Structure
```
cmdai/
├── src/
│   └── ollama/
│       ├── __init__.py
│       └── core.py       # Main implementation
├── tests/                # Test files
├── requirements.txt      # Dependencies
└── run_ollama.py         # Example runner
```

## Installation
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Ollama (if not already running):
```bash
ollama serve  # Run in separate terminal
```

## Usage
Run using the command-line interface (recommended):
```bash
python ai.py "Your prompt here"
```

Or interactively:
```bash
python ai.py
```

Advanced usage (direct module execution):
```bash
python -m src.ollama.core "Your prompt"
```

## Examples
List available models:
```bash
python -m src.ollama.core --list
```

Chat with specific model:
```bash
OLLAMA_MODEL=llama2 python -m src.ollama.core
```

## Configuration
Environment variables:
- OLLAMA_HOST: Set custom API host (default: http://localhost:11434)
- OLLAMA_MODEL: Set default model (default: deepseek-r1)