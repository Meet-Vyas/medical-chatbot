"""
Configuration file for Medical Knowledge Graph Chatbot
Phase 2: Vector Search + Re-ranking + LLM Generation
"""

# ============================================
# NEO4J CONFIGURATION
# ============================================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j123"  # UPDATE THIS

# ============================================
# EMBEDDING MODEL CONFIGURATION
# ============================================
# BGE model for generating embeddings
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMENSION = 384  # BGE-small dimension

# Text to embed (Option C: Section text + entities)
INCLUDE_ENTITIES_IN_EMBEDDING = True

# ============================================
# VECTOR SEARCH CONFIGURATION
# ============================================
# Number of sections to retrieve from vector search
TOP_K_VECTOR_SEARCH = 10

# Vector index name in Neo4j
VECTOR_INDEX_NAME = "section_embeddings"

# Similarity metric (cosine is default for BGE)
SIMILARITY_METRIC = "cosine"

# ============================================
# CROSS-ENCODER CONFIGURATION
# ============================================
# Cross-encoder model for re-ranking
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Number of sections to keep after re-ranking
TOP_N_RERANKED = 3

# ============================================
# OLLAMA CONFIGURATION
# ============================================
# Ollama model for answer generation
OLLAMA_MODEL = "mistral:7b"

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Generation parameters
OLLAMA_TEMPERATURE = 0.1  # Low temperature for factual responses
OLLAMA_MAX_TOKENS = 1000

# ============================================
# PROMPT CONFIGURATION
# ============================================
# Strict prompting to prevent hallucination
STRICT_MODE = True

# Include source attribution in answers
INCLUDE_SOURCE_ATTRIBUTION = True

# System prompt for LLM
SYSTEM_PROMPT = """You are a medical information assistant that provides accurate, fact-based answers.

CRITICAL RULES:
1. Answer ONLY using the provided context from the knowledge base
2. If information is not in the context, say "I don't have that information in my knowledge base"
3. Never make up or infer information not explicitly stated in the context
4. Always mention the source (substance name and section) when providing information
5. If the context is insufficient, acknowledge the limitation

You are helpful but cautious. Medical accuracy is your top priority."""

# ============================================
# CONTEXT FORMATTING
# ============================================
# Enhanced context format (includes metadata)
ENHANCED_CONTEXT_FORMAT = True

# ============================================
# LOGGING CONFIGURATION
# ============================================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/chatbot.log"

# Log all queries and responses (for evaluation)
LOG_ALL_INTERACTIONS = True

# ============================================
# PERFORMANCE CONFIGURATION
# ============================================
# Batch size for embedding generation (one-time setup)
EMBEDDING_BATCH_SIZE = 32

# Enable caching (set to False initially)
ENABLE_CACHING = False

# ============================================
# VALIDATION CONFIGURATION
# ============================================
# Minimum similarity score to consider a result relevant
MIN_SIMILARITY_THRESHOLD = 0.3  # Lower = more permissive

# Maximum context length (in characters) to send to LLM
MAX_CONTEXT_LENGTH = 8000  # Ollama can handle much more, but keep it focused
