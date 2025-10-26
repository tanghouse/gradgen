# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TangHouse is a graduation portrait generation system that uses Google Gemini models (via Vertex AI or public GenAI API) to transform portrait photos into professional graduation photos with accurate academic regalia. The system supports batch testing across multiple universities, degree levels, and prompt variations.

## Key Commands

### Environment Setup
```bash
# Install dependencies using Poetry
poetry install

# Activate virtual environment
poetry shell
```

### Core Scripts

**Generate design board templates from scraped graduation gown images:**
```bash
python src/build_gown_templates.py --engine vertex --vertex_project YOUR_PROJECT --out_root templates
# or with public Gemini API:
python src/build_gown_templates.py --engine genai --out_root templates
```

**Run batch graduation portrait generation:**
```bash
# Using Vertex AI (recommended):
python src/batch_grad_test.py --engine vertex --vertex_project YOUR_PROJECT --portraits_root data/raw_portraits --boards_glob "templates/*/*/board.png" --out_root experiments

# Using public Gemini API:
GEMINI_API_KEY=your_key python src/batch_grad_test.py --engine genai --portraits_root data/raw_portraits --boards_glob "templates/*/*/board.png" --out_root experiments

# Limit scope for testing:
python src/batch_grad_test.py --engine genai --limit_portraits 2 --limit_prompts 2 --limit_boards 1
```

**Generate evaluation CSV from experiment results:**
```bash
python src/make_marking_csv.py --experiments_root experiments --out_dir eval_sheets
# Use latest run automatically or specify:
python src/make_marking_csv.py --run_dir experiments/run_20251020-025631 --out_dir eval_sheets
```

**Scrape graduation gown images from Churchill Gowns:**
```bash
python src/scrape_churchill_gowns.py --output output --delay 0.5
```

## Architecture

### Directory Structure
- `src/` - Core Python scripts
  - `batch_grad_test.py` - Main batch generation engine
  - `build_gown_templates.py` - Creates design boards from gown photos
  - `make_marking_csv.py` - Generates evaluation spreadsheets
  - `scrape_churchill_gowns.py` - Web scraper for graduation gown images
- `data/raw_portraits/` - Input portrait photos (Unsplash/Pexels/Pixabay)
- `templates/<University>/<Level>/board.png` - Design board templates showing gown, hood, cap
- `experiments/run_YYYYMMDD-HHMMSS/` - Generated outputs organized by run
- `eval_sheets/` - Generated CSV files for human evaluation
- `prompts.json` - Prompt library (P0-P7)
- `prompt_test_plan.csv` - Template for tracking evaluation runs
- `notebooks/` - Jupyter notebooks for experimentation

### Output Structure
Each experimental run creates this hierarchy:
```
experiments/run_YYYYMMDD-HHMMSS/
├── manifest.csv
└── <University>__<Level>/
    └── <portrait_filename>/
        └── <prompt_id>/
            ├── output.png          # Generated result
            ├── <original_photo>    # Copy of input portrait
            ├── board.png           # Copy of design board
            ├── prompt.txt          # Resolved prompt text
            ├── meta.json           # Metadata (engine, model, etc.)
            └── error.txt           # Error log if generation failed
```

### Dual Engine Support

The system supports two generation engines:

1. **Vertex AI** (recommended for production):
   - Requires GCP project and location
   - Uses `vertexai` package
   - Better rate limits and reliability
   - Example: `--engine vertex --vertex_project my-project --vertex_location us-central1`

2. **Public GenAI API** (for development/testing):
   - Requires `GEMINI_API_KEY` environment variable
   - Uses `google-genai` package
   - Simpler setup, lower limits
   - Example: `--engine genai --genai_model gemini-2.5-flash-image`

### Prompt System

Prompts are defined in `prompts.json` with IDs P0-P7:
- **P0**: Apple-style studio portraits
- **P1**: Generic UK graduation
- **P2**: Parametric graduation (university-specific, templated)
- **P3-P7**: Various portrait styles (daylight, passport, editorial, high-key, low-key)

All prompts automatically receive a `CONTROL_SUFFIX` appended by `batch_grad_test.py` to enforce:
- Design board as reference only (not in output)
- Identity preservation
- Photo-realistic textures
- Single image output

### Template Creation Workflow

1. Scrape graduation gown photos using `scrape_churchill_gowns.py`
2. Manually organize into `raw_data/<University>/<Level>/` folders
3. Run `build_gown_templates.py` to generate composite design boards
4. Design boards are saved as `templates/<University>/<Level>/board.png`
5. These boards are referenced during graduation portrait generation

### Evaluation Workflow

1. Run batch generation with `batch_grad_test.py`
2. Generate marking sheet with `make_marking_csv.py`
3. Human reviewers score outputs on 1-5 scale:
   - `face_fidelity_1to5`: Likeness to source face
   - `attire_accuracy_1to5`: Gown/hood/cap correctness
   - `lighting_realism_1to5`: Natural lighting quality
   - `background_quality_1to5`: Clean separation, no artifacts
   - `artifacts_1to5_low_is_good`: Warped features, color bleeding (lower is better)
   - `overall_1to5`: Overall quality judgment

## Dependencies

Core libraries (see `pyproject.toml`):
- `requests` - HTTP requests for scraping
- `bs4` (BeautifulSoup) - HTML parsing
- `google-genai` - Public Gemini API client
- `google-cloud-aiplatform` / `vertexai` - Vertex AI client (optional, recommended)
- `pillow` - Image processing
- `tqdm` - Progress bars

Development:
- `ipykernel` - Jupyter notebook support

## Important Notes

- This is a **research/testing project** (`package-mode = false` in pyproject.toml)
- Requires Python 3.13+
- Input portraits must have appropriate licenses (Unsplash License, Pexels License, CC0, CC BY)
- Avoid using research-only datasets (FFHQ/CelebA/LFW) for commercial purposes
- The system processes images × prompts × boards, so batch sizes can grow quickly
- Use `--limit_*` flags to constrain batch size during development
