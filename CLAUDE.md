# CLAUDE.md

## Project Overview

**Ark-Tools** is a Python-based toolkit for extracting and processing game resources from the mobile game "Arknights" (明日方舟). The project provides utilities to download updated game assets and export character artwork variations.

- **License**: MIT
- **Author**: MetalCrab
- **Python Version**: >=3.12
- **Package Manager**: PDM

## Repository Structure

```
Ark-Tools/
├── src/                        # Source code directory
│   ├── config.py              # Configuration constants and API endpoints
│   ├── download_res.py        # Resource downloading and version checking
│   ├── avg_export.py          # Character artwork variation export
│   ├── avg_gen_face.py        # Character face variation generation
│   ├── unpacker.py            # Unity asset unpacking utilities
│   ├── util.py                # Utility functions (HTTP, file operations)
│   ├── img_util.py            # Image processing utilities
│   └── audio.py               # Audio visualization creation
├── data/                      # Data storage directory
│   └── game_data/
│       ├── hot_update_list/   # Game version update lists (JSON)
│       └── resVersion.yaml    # Current local resource version
├── download/                  # Downloaded game resources (created at runtime)
├── resources/                 # Static resources
│   ├── logo.jpeg             # Application logo
│   └── fonts/                # Font files (MiSans family)
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # User-facing documentation (Chinese)
└── LICENSE                   # MIT License
```

## Key Components

### 1. Configuration (`config.py`)

Defines critical constants and API endpoints:
- `DATAPATH`: Path to local game data storage
- `DOWNLOADPATH`: Path for downloaded resources
- API endpoints for different game platforms (Android/iOS, official/bilibili)
- Version checking and hot update list URLs

### 2. Resource Downloader (`download_res.py`)

Main functionality:
- Compares local vs remote game versions
- Downloads updated game assets (character art, backgrounds, UI, etc.)
- Supports differential updates (new vs updated files)
- Asset categories tracked:
  - `avg/imgs` - Story backgrounds and CGs
  - `avg/bg` - Backgrounds
  - `avg/items` - Story items
  - `chararts` - Character artwork
  - `skinpack` - Character skins
  - `avg/characters` - Character variations
  - `ui/activity` - Activity UI resources
  - `gamedata/excel` - Game data tables

### 3. Character Art Exporter (`avg_export.py`)

Processes character artwork variations:
- Extracts ZIP packages
- Unpacks Unity asset bundles
- Generates composite images from face variations
- Handles alpha masks for layering
- Output: Complete character artwork with all variations

### 4. Unity Unpacker (`unpacker.py`)

Core unpacking logic using UnityPy:
- Extracts Texture2D, Sprite, and MonoBehaviour objects
- Retrieves positioning data for face compositing
- Manages alpha masks and layering information
- Organizes extracted assets by type (full/face)

### 5. Utilities (`util.py`)

Helper functions:
- Async HTTP requests with custom headers
- File downloading with progress
- ZIP extraction
- Timestamp utilities

### 6. Image Processing (`img_util.py`)

Advanced image manipulation:
- Upscaling support (via realcugan external tool)
- Gaussian blur card effects
- Rounded rectangle masks
- Image composition with shadows
- MiSans font support for text rendering

### 7. Audio Visualization (`audio.py`)

Creates audio visualizer videos:
- FFT-based frequency spectrum visualization
- Combines multiple audio files
- Generates videos with background images
- Custom branding with logo and titles

## Development Setup

### Prerequisites

1. Python 3.12 or higher
2. PDM (Python Development Master) package manager
3. Git

### Installation Steps

```bash
# Clone the repository
git clone <repository-url>
cd Ark-Tools

# Install dependencies using PDM
pdm install

# (Optional) External tools for image upscaling
# Place realcugan-ncnn-vulkan.exe in ./tools/realcugan/
```

### Dependencies

Core dependencies (from `pyproject.toml`):
- `Pillow>=10.2.0` - Image processing
- `httpx>=0.26.0` - Async HTTP client
- `ruamel-yaml>=0.18.6` - YAML parsing
- `aiofiles>=23.2.1` - Async file operations
- `UnityPy` (custom fork from MetalCrab) - Unity asset unpacking
- `natsort>=8.4.0` - Natural sorting
- `librosa>=0.11.0` - Audio analysis
- `numpy>=2.2.5` - Numerical operations
- `moviepy>=2.1.2` - Video generation

## Workflows

### 1. Downloading Updated Resources

```bash
# Run the download script
python src/download_res.py
```

Process:
1. Checks local version in `data/game_data/resVersion.yaml`
2. Fetches latest version from Arknights API
3. Downloads hot_update_list for both versions
4. Compares asset lists to identify new/updated files
5. Downloads only changed assets to `download/<version>/`
6. Updates local version file

### 2. Exporting Character Artwork

```bash
# Run the export script
python src/avg_export.py
```

Process:
1. Scans `download/<version>/new/avg/characters/` for new ZIP files
2. For each ZIP:
   - Extracts Unity asset bundle
   - Unpacks textures and metadata
   - Generates face variations on base artwork
   - Applies alpha masks for proper layering
   - Saves final composited images
3. Outputs to `out/` directory

### 3. Creating Audio Visualizations

```bash
# Run the audio visualization script
python src/audio.py
```

Process:
1. Loads audio files and background image
2. Performs FFT analysis on audio
3. Generates frequency spectrum bars
4. Composites with branded UI elements
5. Exports as MP4 video

## Code Conventions

### Python Style

The project uses Ruff for linting with the following rules enabled:
- `E`, `W` - pycodestyle errors and warnings
- `ASYNC` - flake8-async
- `B` - flake8-bugbear
- `C4` - flake8-comprehensions
- `SIM` - flake8-simplify
- `T10`, `T20` - flake8-debugger, flake8-print
- `F` - Pyflakes
- `I` - isort (import sorting)
- `UP` - pyupgrade

### Code Patterns

1. **Async/Await**: Heavy use of asyncio for concurrent downloads
2. **Type Hints**: Moderate use of type annotations (not comprehensive)
3. **Path Objects**: Uses `pathlib.Path` for file operations
4. **Context Managers**: Uses `with` statements for file operations

### Naming Conventions

- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: Leading underscore (not strictly enforced)
- Chinese comments and docstrings are common

## Important Notes for AI Assistants

### When Working on This Codebase

1. **Language Context**:
   - README and comments are primarily in Chinese
   - Variable names and code are in English
   - The game assets are from a Chinese mobile game

2. **External Dependencies**:
   - Uses a custom fork of UnityPy: `git+https://github.com/MetalCrab/UnityPy`
   - Some features require external executables (realcugan for upscaling)
   - Font files expected in `resources/fonts/` (MiSans family)

3. **Runtime Directories**:
   - `download/` directory is created at runtime
   - `out/` directory is created for exports
   - `data/game_data/` should exist before running

4. **API Endpoints**:
   - All game resource URLs are hardcoded in `config.py`
   - Using Hypergryph's official CDN (`ak.hycdn.cn`)
   - Version API uses `ak-conf.hypergryph.com`

5. **Error Handling**:
   - Some scripts have commented-out try/except blocks
   - Error lists are tracked but not always acted upon
   - Print statements used extensively for logging

6. **Asset Processing**:
   - Assets are downloaded as `.dat` files, renamed to `.zip`
   - ZIP files contain Unity asset bundles
   - Complex image compositing with multiple layers and masks

### Modification Guidelines

1. **Preserve Chinese Content**: Keep Chinese strings in comments/docs unless specifically asked to translate
2. **Maintain Async Patterns**: Use async/await for I/O operations
3. **Follow Path Conventions**: Use `pathlib.Path` instead of string concatenation
4. **Respect API Structure**: Don't change API endpoints without verification
5. **Test with Real Assets**: Many features depend on specific Unity asset structures

### Testing

- No formal test suite currently exists
- Manual testing required with real game assets
- Asset structure changes in game updates may break functionality

### Common Tasks

**Adding a new resource type**:
1. Add to `res_type_list` in `download_res.py:175-186`
2. Update download logic if special handling needed
3. May need new unpacker logic in `unpacker.py`

**Updating version checking**:
1. Modify `get_res_version()` in `download_res.py`
2. Update `resVersion.yaml` format if needed

**Adding new image effects**:
1. Add functions to `img_util.py`
2. Use PIL's Image, ImageDraw, ImageFilter modules
3. Follow existing pattern of returning modified images

### Debugging Tips

- Check `data/game_data/resVersion.yaml` for version issues
- Verify `hot_update_list` JSON files are valid
- Ensure downloaded ZIP files aren't corrupted
- Check Unity asset bundle structure with UnityPy
- Verify alpha mask alignment for character artwork

## Git Workflow

### Branch Conventions

- Main development on `main` branch
- Feature branches follow pattern: `claude/claude-md-<session-id>`
- Always develop on designated feature branches
- Push with `-u origin <branch-name>` for new branches

### Commit Style

The project uses emoji-prefixed commit messages:
- ✨ `:sparkles:` - New features
- 📝 `:pencil:` - Documentation
- 🎉 `:tada:` - Initial commit
- 🐛 `:bug:` - Bug fixes

### Current State

- Latest commit: `d9a846c` - Added character variation and BGM processing scripts
- No CI/CD pipeline configured
- No automated tests

## Additional Context

### Game Resource Structure

Arknights uses Unity as its game engine. Assets are:
- Bundled in asset bundles
- Compressed and encrypted (`.dat` files)
- Versioned through hot update system
- Organized by category (avg, chararts, gamedata, etc.)

### Character Artwork System

Character variations consist of:
- **Full body** (`avg$N.png`): Base character artwork
- **Face variations** (`N$M.png`): Different expressions/poses
- **Alpha masks** (`[alpha].png`): Transparency data
- **Position data**: From MonoBehaviour objects in Unity

The system composites face variations onto the base artwork using positioning metadata and alpha masks to create the final images.

### Version Management

- Game versions follow format: `YY-MM-DD-HH-MM-SS-hash`
- Each version has a `hot_update_list.json` with all asset metadata
- Local version tracked in `resVersion.yaml`
- Downloads only delta between versions

## Future Considerations

When extending this codebase:
- Consider adding proper logging instead of print statements
- Add comprehensive error handling
- Create automated tests for core functionality
- Add support for more resource types
- Consider adding a CLI with argparse
- Document expected directory structure better
- Add type hints comprehensively
- Consider async context managers for resource cleanup
