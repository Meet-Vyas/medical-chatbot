# UI Setup Guide

This guide explains how to set up and run the web-based UI for the Medical Knowledge Graph Chatbot.

## Prerequisites

1. **Neo4j** running with the knowledge graph (from Phase 1)
2. **Ollama** installed and running with `mistral:7b` model
3. **Python 3.8+** installed
4. **Node.js 16+** and npm installed
5. All embeddings generated (run `python embedding_manager.py` if not done)

## Setup Instructions

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements_api.txt
```

This installs:
- FastAPI
- Uvicorn
- Pydantic

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

This installs:
- React
- Axios
- Tailwind CSS

### 3. Verify Backend Configuration

Make sure `config.py` in the project root has correct settings:
- Neo4j connection details
- Ollama API URL (default: `http://localhost:11434/api/generate`)

## Running the Application

### Option 1: Run Both Services Manually

**Terminal 1 - Backend API:**
```bash
cd backend
python app.py
```

Or using uvicorn directly:
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

The UI will open automatically at: `http://localhost:3000`

### Option 2: Run from Project Root

You can also run the backend from the project root:

```bash
# From project root
python -m backend.app
```

## Usage

1. Open your browser to `http://localhost:3000`
2. Wait for the connection indicator to show "Connected" (green dot)
3. Type your question in the input box and press Enter or click Send
4. View the answer, sources, and response time

## Troubleshooting

### Backend Not Starting

- Check that Neo4j is running: `http://localhost:7474`
- Verify Neo4j credentials in `config.py`
- Check that embeddings are generated: `python embedding_manager.py --verify`
- Check logs in `chatbot.log`

### Frontend Can't Connect to Backend

- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify `API_BASE_URL` in `frontend/src/services/api.js` is `http://localhost:8000/api`

### Ollama Connection Issues

- Ensure Ollama is running: `ollama serve`
- Verify model is downloaded: `ollama list` (should show `mistral:7b`)
- Check Ollama API: `curl http://localhost:11434/api/tags`

### UI Not Loading

- Check that all npm packages are installed: `cd frontend && npm install`
- Clear browser cache
- Check browser console for errors

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/query` - Process a query
  - Request body: `{ "query": "your question", "verbose": false }`
  - Response: `{ "answer": "...", "sources": [...], "timing": {...} }`

## Development

### Backend Development

- Backend uses FastAPI with auto-reload (when using `--reload` flag)
- API docs available at: `http://localhost:8000/docs`
- Logs are written to `chatbot.log` and console

### Frontend Development

- Frontend uses React with hot-reload
- Changes to components will auto-refresh in browser
- Tailwind CSS is configured for styling

## Production Deployment

### Backend

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

```bash
cd frontend
npm run build
```

This creates a `build/` directory with static files that can be served by any web server (nginx, Apache, etc.) or by FastAPI itself.

## Architecture

```
┌─────────────┐
│   Browser   │
│  (React UI) │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│  FastAPI    │
│  (Backend)  │
└──────┬──────┘
       │
       ├──► QueryPipeline
       │    ├──► VectorSearch
       │    ├──► CrossEncoderRanker
       │    └──► LLMGenerator
       │
       ├──► Neo4j (Graph DB)
       └──► Ollama (LLM)
```

## Notes

- The backend logic remains unchanged - only a REST API wrapper was added
- All existing functionality (vector search, re-ranking, LLM generation) works the same
- The UI is a clean, modern interface built with React and Tailwind CSS
- No data is sent to external services - everything runs locally

