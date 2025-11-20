# Repository Organization

This document describes the organization structure of the Medical Knowledge Graph Chatbot repository.

## Directory Structure

```
chatbot2-ui/
├── core/                      # Core logic modules
│   ├── __init__.py
│   ├── config.py             # Configuration settings
│   ├── embedding_manager.py  # One-time embedding setup
│   ├── vector_search.py      # Vector similarity search
│   ├── cross_encoder_ranker.py  # Re-ranking module
│   ├── llm_generator.py      # Ollama integration
│   └── query_pipeline.py     # Orchestrates full pipeline
│
├── backend/                   # FastAPI backend
│   ├── app.py                # FastAPI application
│   ├── api/
│   │   ├── models.py        # Pydantic models
│   │   └── routes.py         # API routes
│   └── requirements_api.txt  # Backend dependencies
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   └── services/         # API service
│   └── package.json
│
├── docs/                      # Documentation
│   ├── SETUP_GUIDE.md
│   ├── UI_SETUP.md
│   ├── PHASE2_SUMMARY.md
│   └── ORGANIZATION.md       # This file
│
├── jsons/                     # Medical data files
│   └── *.json                # Substance data files
│
├── logs/                      # Log files (gitignored)
│   └── .gitkeep
│
├── terminal_interface.py      # CLI chatbot interface
├── start_backend.sh          # Backend startup script
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # Main documentation
```

## Changes Made

### 1. Core Logic Organization
- **Before:** Core modules were in the root directory
- **After:** All core modules moved to `core/` folder
  - `config.py` → `core/config.py`
  - `vector_search.py` → `core/vector_search.py`
  - `cross_encoder_ranker.py` → `core/cross_encoder_ranker.py`
  - `llm_generator.py` → `core/llm_generator.py`
  - `query_pipeline.py` → `core/query_pipeline.py`
  - `embedding_manager.py` → `core/embedding_manager.py`

### 2. Documentation Organization
- **Before:** Documentation files were in root
- **After:** All documentation moved to `docs/` folder
  - `SETUP_GUIDE.md` → `docs/SETUP_GUIDE.md`
  - `UI_SETUP.md` → `docs/UI_SETUP.md`
  - `PHASE2_SUMMARY.md` → `docs/PHASE2_SUMMARY.md`

### 3. Log Files Organization
- **Before:** Log files were in root and backend directories
- **After:** All logs moved to `logs/` folder
  - Log file path updated in `core/config.py` to `logs/chatbot.log`

### 4. Import Updates
All imports have been updated to reflect the new structure:
- Core modules use relative imports within the `core` package
- External imports (terminal_interface.py, backend) use `from core import ...`
- All imports tested and verified

### 5. Cleanup
- Removed `my_query.txt` (test file)
- Removed `__pycache__/` directories
- Added `.gitignore` to prevent committing:
  - Python cache files
  - Log files
  - Node modules
  - IDE files
  - Environment files

## Usage After Reorganization

### Running Core Modules

All core modules should be run as Python modules:

```bash
# Embedding manager
python -m core.embedding_manager

# Test components
python -m core.vector_search
python -m core.cross_encoder_ranker
python -m core.llm_generator
python -m core.query_pipeline
```

### Running Terminal Interface

```bash
# From project root
python terminal_interface.py
```

### Running Backend

```bash
# Option 1: Use startup script
./start_backend.sh

# Option 2: Manual
cd backend
python app.py
```

## Import Patterns

### Within Core Package
```python
from . import config
from .vector_search import VectorSearcher
```

### From Outside Core Package
```python
from core import config
from core.query_pipeline import QueryPipeline
from core.vector_search import VectorSearcher
```

## Benefits of This Organization

1. **Clear Separation:** Core logic, backend, frontend, and docs are clearly separated
2. **Better Maintainability:** Easier to find and modify code
3. **Scalability:** Easy to add new modules or features
4. **Professional Structure:** Follows Python best practices
5. **Clean Repository:** Unwanted files are gitignored

## Migration Notes

If you have existing code that imports from the old structure, update imports:

**Old:**
```python
from query_pipeline import QueryPipeline
import config
```

**New:**
```python
from core.query_pipeline import QueryPipeline
from core import config
```

## Future Improvements

Potential future organization improvements:
- Add `tests/` directory for unit tests
- Add `scripts/` directory for utility scripts
- Add `data/` directory if more data files are added
- Consider splitting `core/` into sub-packages if it grows

