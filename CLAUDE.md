# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Manga Uploader Pro is a modern Python application for uploading manga chapters to various image hosting services (Catbox, Imgur) with a QML-based GUI. The application features async architecture, parallel uploads, and a pluggable host system.

## Common Development Commands

### Running the Application
```bash
# Run from project root
python run.py

# Or run directly from src
cd src && python main.py
```

### Development Dependencies
```bash
# Install all dependencies including dev tools
pip install -e ".[dev]"

# Or install from requirements.txt
pip install -r requirements.txt
```

### Testing
```bash
# Run tests
pytest tests/

# Run specific test file
pytest tests/test_core.py

# Run with async support (configured in pyproject.toml)
pytest tests/ --asyncio-mode=auto
```

### Code Quality
```bash
# Format code with Black
black src/ tests/ --line-length 100

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### Building
```bash
# Create standalone executable
python build.py

# The build will be in dist/ folder
```

## Architecture Overview

### Core Structure
- **src/main.py**: Entry point with Qt application setup and async event loop
- **src/ui/backend.py**: Qt/QML backend bridge with async services
- **src/core/**: Business logic layer
  - **config.py**: Configuration management with Pydantic models
  - **services/**: Core services (uploader, queue, GitHub)
  - **hosts/**: Pluggable upload providers (Catbox, Imgur)
  - **models/**: Data models and enums

### Key Patterns
- **Async Architecture**: Uses `qasync` to bridge Qt event loop with asyncio
- **Service Layer**: Business logic separated from UI concerns
- **Plugin System**: Upload hosts implement `BaseHost` interface
- **Queue System**: Upload jobs processed via async queue with workers
- **Configuration**: Pydantic models with automatic validation

### QML Integration
- Backend exposed to QML via `@QmlElement` decorator
- Models use Qt's MVC pattern for data binding
- Async operations bridged through Qt signals/slots

## Host System

New upload providers should extend `BaseHost` in `src/core/hosts/base.py`. Current implementations:
- **Catbox**: Anonymous and authenticated uploads
- **Imgur**: OAuth2-based uploads (requires client_id)

## Configuration

Configuration uses platform-specific paths:
- **Windows**: `%LOCALAPPDATA%/MangaUploaderPro/config.json`
- **Linux/Mac**: `~/.config/MangaUploaderPro/config.json`

Config structure follows `AppConfig` model in `config.py` with host-specific settings.

## File Structure Requirements

Application expects manga organized as:
```
Root Folder/
└── Manga Title/
    ├── Chapter 1/
    │   └── *.jpg, *.png, *.webp
    └── Chapter 2/
        └── images...
```

## Migration Status

✅ **COMPLETED MIGRATION FROM catbox_uploader_gui.py**

### Migrated Features:
- **QML Interface**: Modern Material Design UI replacing Qt Widgets
- **Async Architecture**: Full async/await implementation replacing threading
- **Host System**: Pluggable Catbox/Imgur hosts with rate limiting
- **GitHub Integration**: Async metadata upload to repositories
- **Configuration**: Pydantic-based config with validation
- **Progress Tracking**: Real-time upload progress and status
- **Error Handling**: Comprehensive error reporting

### Fixed Issues:
- ✅ QML `padding` property error resolved
- ✅ Chapter selection model properly implemented
- ✅ GitHub upload functionality integrated
- ✅ Async image uploading with proper error handling

## Development Notes

- Use `loguru` for logging (configured in `main.py`)
- Qt 6.5+ required for QML features
- Async operations must respect Qt's threading model
- Configuration changes require `_init_hosts()` call to reload providers
- Run `python create_test_structure.py` to create test manga structure