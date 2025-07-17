# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Manga Uploader Pro is a modern Python application for uploading manga chapters to various image hosting services with a QML-based GUI. Features async architecture, parallel uploads, pluggable host system, and automatic JSON indexing for scanlation groups. The application generates standardized JSON catalogs compatible with manga readers like Tachiyomi.

## Common Development Commands

### Running the Application
```bash
# Recommended: Run from project root
python run.py

# Alternative: Run directly from src
cd src && python main.py

# Debug QML issues (tests PySide6 imports and QML engine)
python debug_qml.py

# Windows batch launcher
start_app.bat
```

### Development Dependencies
```bash
# Install all dependencies including dev tools
pip install -e ".[dev]"

# Or install from requirements.txt
pip install -r requirements.txt

# Project script entry point (alternative)
manga-uploader
```

### Testing
```bash
# Run tests (async mode auto-configured in pyproject.toml)
pytest tests/

# Run specific test file
pytest tests/test_core.py

# Run with coverage
pytest tests/ --cov=src --cov-report=html
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
# Create standalone executable (PyInstaller with QML assets)
python build.py

# The build will be in dist/MangaUploaderPro.exe
# Includes: --onefile, --windowed, QML assets, all dependencies
```

## Architecture Overview

### Core Structure
- **src/main.py**: Entry point with Qt application setup and async event loop
- **src/ui/backend.py**: Qt/QML backend bridge with async services
- **src/core/**: Business logic layer
  - **config.py**: Configuration management with Pydantic models
  - **services/**: Core services (uploader, queue, GitHub, indexador)
  - **hosts/**: Pluggable upload providers (10+ supported)
  - **models/**: Data models and enums
    - **indexador.py**: Complex data structures for JSON indexing system

### Key Patterns
- **Async Architecture**: Uses `qasync` to bridge Qt event loop with asyncio
- **Service Layer**: Business logic separated from UI concerns
- **Plugin System**: Upload hosts implement `BaseHost` interface
- **Queue System**: Upload jobs processed via async queue with workers
- **Configuration**: Pydantic models with automatic validation
- **JSON Indexing**: Automatic catalog generation for scanlation groups with GitHub integration

### QML Integration
- Backend exposed to QML via `@QmlElement` decorator
- Models use Qt's MVC pattern for data binding
- Async operations bridged through Qt signals/slots

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

## JSON Indexing System

The application generates standardized JSON catalogs for scanlation groups:
- **index.json**: Main hub catalog with series listings, statistics, and metadata
- **reader.json**: Template for individual manga JSONs with chapter data
- **GitHub Integration**: Automatic commit and hosting via CDN (JSDelivr)
- **Tachiyomi Compatible**: Follows reader app standards for broad compatibility

Key files:
- `src/core/services/indexador.py`: Main indexing service
- `src/core/models/indexador.py`: Complex Pydantic models matching real-world hub structures
- `raw/index.json` and `raw/reader.json`: Templates and examples

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

## Development Notes

- Use `loguru` for logging (configured in `main.py`)
- Qt 6.5+ required for QML features
- Async operations must respect Qt's threading model
- Configuration changes require `_init_hosts()` call to reload providers
- Complex Pydantic models in `indexador.py` require careful validation
- Debug QML issues with `debug_qml.py` script
- State management via `IndexadorState` class for real-time updates
### Host-Specific Implementation Details
- All hosts extend `BaseHost` with required methods: `upload_image()` and `create_album()`
- Rate limiting configured per host via `rate_limit` and `max_workers` settings
- Upload results use standardized `UploadResult` and `ChapterUploadResult` models
- Session management handled individually (e.g., Imgbox cookie testing)
- Direct link optimization available for compatible hosts (Gofile)

### Adding New Hosts
1. Create new file in `src/core/hosts/`
2. Extend `BaseHost` class
3. Implement `upload_image()` and `create_album()` methods
4. Add host configuration to `src/core/config.py`
5. Register host in `src/core/hosts/__init__.py`

## Important Architecture Notes

### Async Event Loop Integration
- Main thread runs Qt event loop via `qasync.QEventLoop`
- All async operations must be compatible with Qt's threading model
- Service layer handles async/await bridging to QML via signals

### IndexadorDialog System
- Complex dialog system in `src/ui/qml/components/IndexadorDialog.qml`
- Manages series selection, metadata editing, and GitHub configuration
- Real-time state updates via `IndexadorState` and Qt property bindings

### Entry Points
- `run.py`: Recommended entry point (handles Python path setup)
- `src/main.py`: Direct entry point
- `debug_qml.py`: For debugging QML-specific issues
- `start_app.bat`: Windows batch launcher