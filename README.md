# Code Knowledge Graph System

Universal Programming Language Code Knowledge Graph System based on First Principles

## Features

- **Multi-language Support**: Python, JavaScript, TypeScript, Go, ArkTS, and more
- **Real-time Updates**: File monitoring with debounced incremental updates
- **Knowledge Graph Visualization**: Interactive D3.js-powered graph
- **Architecture Diagrams**: Mermaid-based system diagrams
- **LLM Integration**: Silicon Flow API for code analysis
- **REST API**: Full-featured API for data access
- **WebSocket Support**: Real-time updates to clients

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default settings
python -m src.main --project-path /path/to/your/project

# Run full sync only
python -m src.main --full-sync

# Start web server only
python -m src.main --web-only
```

## Architecture

```
File Change → File Monitor → Debounce Queue → Update Engine → SQLite
                                        ↓
                            Universal Parser Interface
                                        ↑
        Python | JavaScript | TypeScript | Go | ArkTS | ...
```

## Configuration

Environment variables:
- `PROJECT_PATH`: Path to project to analyze
- `DATABASE_PATH`: SQLite database path
- `DEBOUNCE_WINDOW_MS`: Debounce window (default: 1000)
- `API_KEY`: Silicon Flow API key
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Development

```bash
# Run tests
python -m pytest tests/

# Generate evaluation report
python docs/evaluation_report.py
```

## License

MIT License
