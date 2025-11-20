# Setup Guide - Medical Knowledge Graph Chatbot
**Complete step-by-step instructions for Phase 2**

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- ✅ Completed Phase 1 (Graph generation with Section nodes)
- ✅ Neo4j 5.x running with populated graph
- ✅ Python 3.8 or higher
- ✅ Mac M3 (or any computer, but instructions optimized for M3)
- ✅ At least 10GB free disk space (for models)
- ✅ Good internet connection (for model downloads)

---

## 🚀 Step-by-Step Setup

### Step 1: Verify Phase 1 Graph

Open Neo4j Browser: `http://localhost:7474`

Run this query:
```cypher
MATCH (s:Substance)
MATCH (sec:Section)
MATCH (e:Entity)
RETURN count(s) as substances, 
       count(sec) as sections, 
       count(e) as entities
```

**Expected (15 JSONs):**
```
substances: 15
sections: ~150
entities: ~500-1000
```

**If you see 0 sections:** Phase 1 is not complete! Go back and run:
```bash
python main_pipeline.py --clear-db
```

---

### Step 2: Create Chatbot Repo Directory

```bash
# Create new directory for chatbot repo
mkdir medical-kg-chatbot
cd medical-kg-chatbot

# Copy all files from the outputs I provided:
# - config.py
# - embedding_manager.py
# - vector_search.py
# - cross_encoder_ranker.py
# - llm_generator.py
# - query_pipeline.py
# - terminal_interface.py
# - test_queries.py
# - requirements.txt
# - README.md
```

---

### Step 3: Update Configuration

Edit `config.py`:

```python
# REQUIRED: Update your Neo4j password
NEO4J_PASSWORD = "your_password_here"  # Change neo4j123 to your password

# OPTIONAL: Adjust these if needed
NEO4J_URI = "bolt://localhost:7687"  # Change if Neo4j on different host
NEO4J_USER = "neo4j"                 # Change if different username
```

Save the file.

---

### Step 4: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows

# Install requirements
pip install -r requirements.txt
```

**Expected output:**
```
Installing neo4j...
Installing sentence-transformers...
Installing torch...
... (lots of packages)
Successfully installed ...
```

**This will take 5-10 minutes** (downloading PyTorch, transformers, etc.)

**If you get errors:**
- Make sure Python 3.8+: `python --version`
- Update pip: `pip install --upgrade pip`
- On M3 Mac: PyTorch with Metal should install automatically

---

### Step 5: Install and Setup Ollama

**Download Ollama:**
1. Go to: https://ollama.ai
2. Download for Mac
3. Install the .dmg file
4. Open Ollama app (should show in menu bar)

**Start Ollama:**
```bash
# Should start automatically, but if not:
ollama serve
```

**Download Mistral 7B model:**
```bash
# This will download ~4GB
ollama pull mistral:7b
```

**Expected output:**
```
pulling manifest 
pulling 8934d96d3f08... 100%
pulling 8c17c2ebb0ea... 100%
... 
verifying sha256 digest 
success
```

**Verify Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

Should return JSON with model info.

---

### Step 6: Generate Embeddings (ONE-TIME SETUP)

**This is the crucial step!**

```bash
python embedding_manager.py
```

**What this does:**
1. Connects to Neo4j
2. Retrieves all Section nodes (~150 for 15 JSONs)
3. Prepares text (section text + entities)
4. Downloads BGE model (~400MB) on first run
5. Generates embeddings for all sections
6. Stores embeddings in Neo4j
7. Creates vector index

**Expected output:**
```
================================================================================
ADDING EMBEDDINGS TO SECTION NODES
================================================================================

[Step 1] Retrieving Section nodes from Neo4j...
✓ Found 150 sections

[Step 2] Preparing texts for embedding...
Preparing texts: 100%|██████████| 150/150 [00:05<00:00, 28.15it/s]
✓ Prepared 150 texts

[Step 3] Generating embeddings (batch size: 32)...
Generating embeddings: 100%|██████████| 5/5 [00:23<00:00,  4.76s/it]
✓ Generated 150 embeddings
  Embedding shape: (150, 384)

[Step 4] Storing embeddings in Neo4j...
Storing embeddings: 100%|██████████| 150/150 [00:08<00:00, 17.82it/s]
✓ All embeddings stored

[Step 5] Creating vector index...
✓ Created vector index: section_embeddings

================================================================================
EMBEDDING SETUP COMPLETE
================================================================================
Sections processed: 150
Embedding dimension: 384
Vector index: section_embeddings
Model: BAAI/bge-small-en-v1.5

✓ Your knowledge graph is now ready for vector search!
```

**Time estimate:**
- 15 JSONs (150 sections): ~2-3 minutes
- 1421 JSONs (14,000 sections): ~30-40 minutes

**If it fails:**
- Check Neo4j is running
- Check password in config.py
- Check you have Section nodes (Step 1)

---

### Step 7: Verify Embeddings

```bash
python embedding_manager.py --verify
```

**Expected output:**
```
================================================================================
EMBEDDING VERIFICATION
================================================================================
Total sections: 150
Sections with embeddings: 150
Missing embeddings: 0

✓ All sections have embeddings!
```

**If some are missing:**
Re-run: `python embedding_manager.py`

---

### Step 8: Test Components

Test each component individually:

**Test 1: Vector Search**
```bash
python vector_search.py
```

Expected: Should show vector search results for test queries

**Test 2: Re-ranking**
```bash
python cross_encoder_ranker.py
```

Expected: Should show before/after re-ranking comparison

**Test 3: LLM Generation**
```bash
python llm_generator.py
```

Expected: Should generate an answer using Ollama

**Test 4: Full Pipeline**
```bash
python query_pipeline.py
```

Expected: Should process test queries end-to-end

**If any test fails:** Check the error message and logs

---

### Step 9: Run Interactive Chatbot

```bash
python terminal_interface.py
```

**Expected output:**
```
================================================================================
MEDICAL KNOWLEDGE GRAPH CHATBOT
================================================================================

Initializing...
Initializing Vector Searcher...
Loading embedding model: BAAI/bge-small-en-v1.5
✓ Model loaded (dimension: 384)
✓ Vector searcher ready
Initializing Cross-Encoder Ranker...
Loading model: cross-encoder/ms-marco-MiniLM-L-6-v2
✓ Cross-encoder ready
Initializing LLM Generator...
Ollama model: mistral:7b
Ollama API: http://localhost:11434/api/generate
✓ Ollama is running
================================================================================
✓ QUERY PIPELINE READY
================================================================================

✓ Chatbot ready!

────────────────────────────────────────────────────────────────────────────────
COMMANDS:
  - Type your question and press Enter
  - 'help' - Show this message
  - 'verbose on/off' - Toggle verbose mode
  - 'quit' or 'exit' - Exit chatbot
────────────────────────────────────────────────────────────────────────────────

You can ask me about:
  • Side effects and adverse reactions
  • Safety information and contraindications
  • Drug interactions
  • Effectiveness for various conditions
  • Dosing and administration

Type your question below:

You: 
```

**Try these test queries:**
1. "What are the side effects of asparagus?"
2. "Is asparagus safe for pregnant women?"
3. "Does asparagus interact with lithium?"

---

### Step 10: Run Evaluation (Optional)

```bash
# List all test queries
python test_queries.py --list

# Run evaluation
python test_queries.py --eval
```

This runs 30+ test queries and shows accuracy metrics.

---

## ✅ Success Criteria

You're successfully set up if:

1. ✅ Embeddings verification shows 0 missing
2. ✅ All component tests pass
3. ✅ Interactive chatbot starts without errors
4. ✅ Test queries return relevant answers
5. ✅ Response time < 5 seconds
6. ✅ Answers cite sources correctly

---

## 🎯 Quick Reference

### Daily Usage

```bash
# Make sure Ollama is running
ollama serve  # (or just open Ollama app)

# Start chatbot
cd medical-kg-chatbot
source venv/bin/activate
python terminal_interface.py
```

### If You Update the Graph (Phase 1)

```bash
# Regenerate embeddings
python embedding_manager.py

# Verify
python embedding_manager.py --verify
```

### Useful Commands

```bash
# Check Neo4j
curl http://localhost:7474

# Check Ollama
curl http://localhost:11434/api/tags

# View logs
tail -f chatbot.log

# Test queries
python test_queries.py --eval
```

---

## 🐛 Common Issues

### Issue 1: "Cannot connect to Neo4j"

**Solution:**
- Check Neo4j is running: `http://localhost:7474`
- Verify password in config.py
- Check URI is correct

### Issue 2: "Cannot connect to Ollama"

**Solution:**
```bash
# Check if running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# Make sure model is downloaded
ollama list
# Should show mistral:7b
```

### Issue 3: "No sections found"

**Solution:**
- Phase 1 not complete
- Run graph generation pipeline first
- Verify with: `MATCH (sec:Section) RETURN count(sec)`

### Issue 4: "Vector index not found"

**Solution:**
```bash
# Re-run embedding generation
python embedding_manager.py
```

### Issue 5: Slow response (>10 seconds)

**Possible causes:**
- Ollama not using Metal acceleration (M3)
- Too many sections being re-ranked
- Network issues

**Solutions:**
- Check Ollama is using Metal: `ollama list`
- Reduce TOP_K_VECTOR_SEARCH to 5 in config.py
- Reduce TOP_N_RERANKED to 2 in config.py

### Issue 6: Model download fails

**Solution:**
```bash
# Download models manually

# BGE (embedding model)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

# Cross-encoder
python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

# Mistral (Ollama)
ollama pull mistral:7b
```

---

## 📊 Expected Performance

### M3 Mac Air (15 JSONs, 150 sections)

| Metric | Value |
|--------|-------|
| Setup time | ~15 minutes |
| Embedding generation | ~2-3 minutes |
| Query response time | ~2.5-3.5s |
| Memory usage | ~2-3GB |

### M3 Mac Air (1421 JSONs, 14,000 sections)

| Metric | Value |
|--------|-------|
| Embedding generation | ~30-40 minutes |
| Query response time | ~3-4s |
| Memory usage | ~3-4GB |

---

## 🎓 What's Next?

Once setup is complete:

1. **Test with your 15 JSONs** - Verify answers are correct
2. **Run evaluation** - Check accuracy metrics
3. **Try different queries** - Explore capabilities
4. **Scale to full dataset** - Process all 1421 JSONs
5. **Evaluate at scale** - Compare performance

---

## 💡 Pro Tips

1. **Use verbose mode** to debug: `verbose on` in terminal
2. **Check logs** for detailed errors: `tail -f chatbot.log`
3. **Test components individually** before full pipeline
4. **Keep Ollama app open** for faster startup
5. **Use virtual environment** to avoid dependency conflicts

---

**Setup complete? Start chatting!**

```bash
python terminal_interface.py
```

**Questions during setup?** Check the README.md or logs!
