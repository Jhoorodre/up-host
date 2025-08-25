# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Manga Uploader Pro is a modern Python application for uploading manga chapters to 10+ image hosting services with a QML-based GUI. The application features async architecture, parallel uploads, pluggable host system, and automatic JSON metadata generation for scanlation groups.

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
# Create standalone executable with PyInstaller
python build.py

# Windows launcher script
start_app.bat

# Debug QML loading issues
python tests/debug_qml.py
```

## Architecture Overview

### Core Structure
- **src/main.py**: Entry point with Qt application setup and async event loop
- **src/ui/backend.py**: Qt/QML backend bridge with async services
- **src/ui/handlers/**: Specialized UI handlers for different concerns
  - **config_handler.py**: Configuration management UI bridge
  - **host_manager.py**: Upload provider management
  - **github_manager.py**: GitHub integration handler
  - **manga_manager.py**: Manga/chapter selection logic
- **src/core/**: Business logic layer
  - **config.py**: Configuration management with Pydantic models
  - **services/**: Core services (uploader, queue, GitHub)
  - **hosts/**: Pluggable upload providers (Catbox, Imgur)
  - **models/**: Data models and enums

### Key Patterns
- **Async Architecture**: Uses `qasync` to bridge Qt event loop with asyncio
- **Service Layer**: Business logic separated from UI concerns
- **Handler Pattern**: UI logic split into specialized handlers for different concerns
- **Plugin System**: Upload hosts implement `BaseHost` interface
- **Queue System**: Upload jobs processed via async queue with workers
- **Configuration**: Pydantic models with automatic validation

### QML Integration
- Backend exposed to QML via `@QmlElement` decorator
- Models use Qt's MVC pattern for data binding
- Async operations bridged through Qt signals/slots
- Handler classes provide specialized property access and methods to QML
- Logging configured in `main.py` with loguru (stored in `~/.manga_uploader/logs/`)
- Event loop integration via `qasync.QEventLoop`

## Host System

New upload providers should extend `BaseHost` in `src/core/hosts/base.py`. Current implementations:
- **Catbox**: Anonymous and authenticated uploads
- **Imgur**: OAuth2-based uploads (requires client_id)
- **ImgBB**: API key-based uploads
- **Gofile**: Anonymous uploads with direct links
- **Pixeldrain**: Anonymous uploads
- **Lensdump**: API key-based uploads
- **ImageChest**: Anonymous uploads
- **Imgbox**: Anonymous uploads with session cookie support
- **ImgHippo**: API v1 uploads with API key authentication
- **ImgPile**: REST API uploads with optional API key

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
- ✅ Added support for 10 image hosting providers
- ✅ Implemented session cookie support for Imgbox
- ✅ Added direct link optimization for Gofile
- ✅ Added ImgHippo with official API v1 support
- ✅ Added ImgPile with REST API and base64 fallback
- ✅ Host selection persistence (saves active host as default)
- ✅ Fuzzy JSON search for locating existing metadata
- ✅ Precise Unix timestamps (exact upload time)
- ✅ Named groups instead of "default" in JSON structure
- ✅ Consistent visual layout across all host configurations
- ✅ ImgBox optimized to use only async generator method

## Development Notes

- Use `loguru` for logging (configured in `main.py`)
- Qt 6.5+ required for QML features  
- Async operations must respect Qt's threading model
- Configuration changes require `_init_hosts()` call to reload providers
- Environment variables can be loaded via `.env` file (optional)
- Main application entry uses `qasync` to bridge Qt and asyncio event loops
- Upload queue workers auto-start when backend initializes
- Host selection in QML requires initialization flags to prevent unwanted changes
- JSON metadata uses fuzzy search to match sanitized filenames
- Timestamps use `int(time.time())` for exact upload time (not rounded to day)
- Group names in JSON should come from existing metadata or custom config
- UI handlers manage specific aspects: ConfigHandler, HostManager, GitHubManager, MangaManager
### Host-Specific Implementation Details
- All hosts extend `BaseHost` with required methods: `upload_image()` and `create_album()`
- Rate limiting configured per host via `rate_limit` and `max_workers` settings
- Upload results use standardized `UploadResult` and `ChapterUploadResult` models
- Session management handled individually (e.g., Imgbox cookie testing)
- Direct link optimization available for compatible hosts (Gofile)
- Automatic WebP to JPG conversion for compatibility (Imgbox)
- ImgBox uses single async generator method for reliability
- Selected host persists across application restarts

### Adding New Hosts
1. Create new file in `src/core/hosts/`
2. Extend `BaseHost` class
3. Implement `upload_image()` and `create_album()` methods
4. Add host configuration to `src/core/config.py` (HostConfig in AppConfig.hosts dict)
5. Register host in `src/core/hosts/__init__.py`
6. Update QML components if new configuration fields are needed

## Indexador System

The application includes an advanced JSON indexing system for scanlation groups:

### Key Features
- **GitHub Integration**: Automatic metadata upload via `src/core/services/github.py`
- **JSON Management**: Smart merge via `src/utils/json_updater.py`
- **Index Generation**: `src/core/models/indexador.py` contains data models
- **CDN URLs**: Automatic JSDelivr raw.githubusercontent.com URL generation

### Configuration
- Indexador settings in `AppConfig.indexador` (Pydantic model)
- GitHub service requires personal access token with repo permissions
- Supports custom branch and folder structure for metadata storage
- JSON structure excludes duplicate "group" field at root level
- Groups are specified within individual chapters, not at document level
- Metadata merging via `JSONUpdater.merge_metadata()` supports add/replace/smart modes