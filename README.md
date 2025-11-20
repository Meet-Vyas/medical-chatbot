# Medical Knowledge Graph Chatbot

A zero-hallucination medical Q&A chatbot using vector search, cross-encoder re-ranking, and LLM generation. This system queries a Neo4j knowledge graph to provide accurate, source-attributed answers about medical substances, their effects, interactions, and safety information.

## 🎯 Overview

This chatbot implements a complete RAG (Retrieval-Augmented Generation) pipeline that:

1. **Vector Search** - Uses BGE embeddings for semantic similarity search
2. **Cross-Encoder Re-ranking** - Uses ms-marco model for relevance scoring
3. **LLM Generation** - Uses Ollama (Mistral 7B) for natural language answers

**Key Feature:** Strict mode prevents hallucination - answers only from retrieved context.

## 📊 Architecture

```
User Query
    ↓
[1] Generate Query Embedding (BGE)
    ↓
[2] Vector Search Neo4j (Top 10 sections)
    ↓
[3] Build Sub-graph Contexts (Section + Entities)
    ↓
[4] Cross-Encoder Re-ranking (Top 3 sections)
    ↓
[5] LLM Answer Generation (Ollama Mistral 7B)
    ↓
Natural Language Answer + Sources
```

## 📁 Project Structure

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
│   └── PHASE2_SUMMARY.md
│
├── jsons/                     # Medical data files
│   └── *.json                # Substance data files
│
├── logs/                      # Log files (gitignored)
│
├── terminal_interface.py      # CLI chatbot interface
├── start_backend.sh          # Backend startup script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Neo4j 5.x** running with graph from Phase 1
2. **Ollama** installed and running
3. **Python 3.8+**
4. **Node.js 16+** (for frontend)

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install backend API dependencies:**
   ```bash
   pip install -r backend/requirements_api.txt
   ```

3. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

4. **Install and start Ollama:**
   ```bash
   # Download from: https://ollama.ai
   ollama serve
   
   # In another terminal:
   ollama pull mistral:7b
   ```

5. **Update configuration:**
   Edit `core/config.py` and set your Neo4j password:
   ```python
   NEO4J_PASSWORD = "your_actual_password"
   ```

### One-Time Setup: Add Embeddings

**IMPORTANT:** Run this once after graph generation (Phase 1) completes:

```bash
python -m core.embedding_manager
```

This will:
- Load all Section nodes from Neo4j
- Generate BGE embeddings for each section (with entities)
- Store embeddings in Section.embedding property
- Create Neo4j vector index

**Expected time:**
- 150 sections (15 JSONs): ~2-3 minutes
- 14,000 sections (1421 JSONs): ~30-40 minutes

### Verify Embeddings

```bash
python -m core.embedding_manager --verify
```

Should show:
```
Total sections: 150
Sections with embeddings: 150
Missing embeddings: 0
✓ All sections have embeddings!
```

## 💻 Usage

### Option 1: Terminal Interface (CLI)

```bash
python terminal_interface.py
```

Interactive commands:
- Type your question and press Enter
- `help` - Show commands
- `verbose on/off` - Toggle detailed progress
- `quit` or `exit` - Exit chatbot

### Option 2: Web Interface

**Terminal 1 - Start Backend:**
```bash
cd backend
python app.py
```

Or use the startup script:
```bash
./start_backend.sh
```

The API will be available at: `http://localhost:8000`

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm start
```

The UI will open automatically at: `http://localhost:3000`

### Option 3: API Only

The backend provides a REST API:

```bash
# Health check
curl http://localhost:8000/api/health

# Query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the side effects of ginger?", "verbose": false}'
```

API documentation available at: `http://localhost:8000/docs`

## 📝 Example Queries

### Adverse Effects
- "What are the side effects of asparagus?"
- "Can X cause allergic reactions?"
- "Is X safe?"

### Safety & Contraindications
- "Can pregnant women take X?"
- "Is X safe for people with liver disease?"
- "Who should avoid X?"

### Drug Interactions
- "Does X interact with Y?"
- "Can I take X with diuretics?"

### Effectiveness
- "Is X effective for treating Y?"
- "Does X help with Z?"

### Dosing
- "What is the recommended dosage?"
- "How much X should I take?"

## 🔧 Configuration

Edit `core/config.py` to customize:

### Models
```python
# Embedding model
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # 384 dimensions
EMBEDDING_DIMENSION = 384

# Cross-encoder model
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# LLM model
OLLAMA_MODEL = "mistral:7b"
```

### Search Parameters
```python
# Vector search
TOP_K_VECTOR_SEARCH = 10  # Sections retrieved from vector search
MIN_SIMILARITY_THRESHOLD = 0.3  # Minimum similarity score

# Re-ranking
TOP_N_RERANKED = 3  # Sections sent to LLM after re-ranking
```

### LLM Parameters
```python
OLLAMA_TEMPERATURE = 0.1  # Low temp for factual answers
OLLAMA_MAX_TOKENS = 1000
STRICT_MODE = True  # Prevent hallucination
```

## 🧪 Testing

### Test Individual Components

```bash
# Test vector search
python -m core.vector_search

# Test re-ranking
python -m core.cross_encoder_ranker

# Test LLM generation
python -m core.llm_generator

# Test full pipeline
python -m core.query_pipeline
```

## 📊 Performance

### Response Times (M3 Mac, 150 sections)

| Step | Time |
|------|------|
| Vector Search | ~0.1s |
| Re-ranking | ~0.3s |
| LLM Generation | ~2-3s |
| **Total** | **~2.5-3.5s** |

### Scaling (1421 JSONs, 14,000 sections)

- Vector search: ~0.2-0.3s (still fast!)
- Re-ranking: ~0.3-0.5s
- LLM generation: ~2-3s (same)
- **Total:** ~3-4s (minimal degradation)

## 🛠️ Troubleshooting

### Ollama Not Running

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it:
ollama serve
```

### Model Not Downloaded

```bash
ollama pull mistral:7b
```

### Embeddings Not Found

```bash
# Re-run embedding generation
python -m core.embedding_manager

# Verify
python -m core.embedding_manager --verify
```

### Neo4j Connection Failed

Check:
1. Neo4j is running: `http://localhost:7474`
2. Password in `core/config.py` is correct
3. Graph from Phase 1 exists with Section nodes

### Slow Performance

**For M3 Mac:**
- Embedding generation: Uses CPU (Metal acceleration for inference only)
- LLM generation: Ollama uses Metal automatically
- Should be ~3-4s per query

**If slower:**
- Check Ollama is using Metal: `ollama list` should show model loaded
- Reduce `TOP_K_VECTOR_SEARCH` to 5
- Reduce `TOP_N_RERANKED` to 2

### Poor Answer Quality

**If answers are generic or miss information:**
1. Check embeddings are generated: `python -m core.embedding_manager --verify`
2. Try increasing `TOP_K_VECTOR_SEARCH` to 15-20
3. Enable verbose mode to see retrieved sections
4. Check if relevant sections exist in graph (Phase 1)

**If answers hallucinate:**
- Verify `STRICT_MODE = True` in config
- Check system prompt in `core/config.py`
- Reduce `OLLAMA_TEMPERATURE` to 0.05

## 🔍 How It Works

### Vector Search (Step 1-3)

1. User query → Generate embedding using BGE
2. Neo4j vector search finds top 10 similar sections
3. For each section, extract:
   - Section text
   - Substance name
   - Connected entities
   - Similarity score

### Re-ranking (Step 4)

Cross-encoder scores each (query, section_context) pair and re-ranks to keep top 3.

### LLM Generation (Step 5)

Strict prompt prevents hallucination:
- System prompt instructs to answer ONLY from provided context
- Low temperature (0.1) for factual responses
- Source attribution included in answers

## 🚨 Important Notes

### Medical Disclaimer

This chatbot is for educational/research purposes only. Always consult healthcare professionals for medical advice.

### Data Privacy

- All processing is local (Neo4j + Ollama)
- No data sent to external APIs
- Queries logged locally only

### Hallucination Prevention

The system uses:
1. Strict prompts ("answer ONLY from context")
2. Low temperature (0.1)
3. Source attribution
4. Context-only answering

But LLMs can still hallucinate. Always verify critical information!

## 📈 Evaluation Metrics

### Recall@K
Did we retrieve the right section in top-K results?

```python
# From test_queries.py evaluation
Recall@10 (vector search): ~95%
Recall@3 (after re-ranking): ~92%
```

### Response Accuracy
Human evaluation of answer correctness:
- Check against source material
- Flag any hallucinations
- Rate helpfulness (1-5)

### Response Time
Target: < 5 seconds per query

## 🎓 Project Context

This is Phase 2 of a medical knowledge graph project:

**Phase 1 (Graph Generation):**
- Ingest Netmeds JSONs
- Extract entities with BioBERT
- Create Neo4j graph with Section nodes

**Phase 2 (This Repo):**
- Add embeddings to Section nodes
- Vector search + re-ranking
- LLM answer generation
- Zero hallucination via strict prompts

## 📝 Next Steps

**For Production:**
1. Add authentication
2. Multi-turn conversations with context
3. Query result caching
4. User feedback collection
5. A/B testing different models

**For Evaluation:**
1. Expand test dataset to 100+ queries
2. Human evaluation protocol
3. Compare with baseline (no re-ranking)
4. Test different models (llama vs mistral)

## 🤝 Contributing

This is a course project. Suggestions welcome!

## 📄 License

This project is for educational purposes.

---

**Questions?** Check logs in `logs/chatbot.log` for debugging.

**Ready to chat?** Run `python terminal_interface.py` or start the web interface!
