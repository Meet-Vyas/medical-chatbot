"""
Vector Search Module
Queries Neo4j vector index to find similar Section nodes
"""

import logging
from typing import List, Dict
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from . import config

logger = logging.getLogger(__name__)


class VectorSearcher:
    """Performs vector similarity search on Section nodes"""
    
    def __init__(self):
        """Initialize vector searcher"""
        logger.info("Initializing Vector Searcher...")
        
        # Connect to Neo4j
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        
        # Load embedding model (same as used for generation)
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        logger.info("✓ Vector searcher ready")
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for user query
        
        Args:
            query: User's question
            
        Returns:
            Query embedding as list
        """
        # Generate embedding (same model as sections)
        embedding = self.embedding_model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True  # Important for cosine similarity
        )
        
        return embedding.tolist()
    
    def vector_search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Perform vector similarity search
        
        Args:
            query: User's question
            top_k: Number of results to return (default from config)
            
        Returns:
            List of section results with similarity scores
        """
        if top_k is None:
            top_k = config.TOP_K_VECTOR_SEARCH
        
        logger.info(f"Vector search for: '{query}' (top {top_k})")
        
        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)
        
        # Perform vector search in Neo4j
        with self.driver.session() as session:
            search_query = f"""
            CALL db.index.vector.queryNodes(
                $index_name,
                $top_k,
                $query_embedding
            )
            YIELD node, score
            
            RETURN node.substance_name as substance_name,
                   node.name as section_name,
                   node.text as section_text,
                   node.word_count as word_count,
                   node.entity_count as entity_count,
                   score,
                   elementId(node) as node_id
            ORDER BY score DESC
            """
            
            result = session.run(
                search_query,
                index_name=config.VECTOR_INDEX_NAME,
                top_k=top_k,
                query_embedding=query_embedding
            )
            
            sections = []
            for record in result:
                sections.append({
                    'node_id': record['node_id'],
                    'substance_name': record['substance_name'],
                    'section_name': record['section_name'],
                    'section_text': record['section_text'],
                    'word_count': record['word_count'],
                    'entity_count': record['entity_count'],
                    'similarity_score': record['score']
                })
            
            logger.info(f"✓ Found {len(sections)} sections")
            
            return sections
    
    def get_section_entities(self, substance_name: str, section_name: str) -> List[str]:
        """
        Get entities mentioned in a section
        
        Args:
            substance_name: Name of substance
            section_name: Name of section
            
        Returns:
            List of entity names
        """
        with self.driver.session() as session:
            query = """
            MATCH (sec:Section {substance_name: $substance_name, name: $section_name})
                  -[:MENTIONS]->(e:Entity)
            RETURN e.name as entity_name,
                   e.entity_type as entity_type
            ORDER BY e.name
            """
            result = session.run(
                query,
                substance_name=substance_name,
                section_name=section_name
            )
            
            entities = [record['entity_name'] for record in result]
            return entities
    
    def build_subgraph_context(self, section: Dict) -> Dict:
        """
        Build enhanced subgraph context for a section
        
        Includes:
        - Section metadata
        - Section text
        - Related entities
        
        Args:
            section: Section dictionary from vector search
            
        Returns:
            Enhanced subgraph context
        """
        # Get entities for this section
        entities = self.get_section_entities(
            section['substance_name'],
            section['section_name']
        )
        
        # Build enhanced context
        subgraph = {
            'substance_name': section['substance_name'],
            'section_name': section['section_name'],
            'section_text': section['section_text'],
            'word_count': section['word_count'],
            'entity_count': section['entity_count'],
            'entities': entities,
            'similarity_score': section['similarity_score'],
            'node_id': section['node_id']
        }
        
        return subgraph
    
    def search_with_subgraphs(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Perform vector search and build subgraph contexts
        
        This is the main method to use for the query pipeline
        
        Args:
            query: User's question
            top_k: Number of results (default from config)
            
        Returns:
            List of subgraph contexts with full information
        """
        # Perform vector search
        sections = self.vector_search(query, top_k)
        
        # Filter by minimum similarity threshold
        sections = [s for s in sections if s['similarity_score'] >= config.MIN_SIMILARITY_THRESHOLD]
        
        if not sections:
            logger.warning(f"No sections found above similarity threshold {config.MIN_SIMILARITY_THRESHOLD}")
            return []
        
        # Build subgraph context for each section
        logger.info("Building subgraph contexts...")
        subgraphs = []
        
        for section in sections:
            subgraph = self.build_subgraph_context(section)
            subgraphs.append(subgraph)
        
        logger.info(f"✓ Built {len(subgraphs)} subgraph contexts")
        
        return subgraphs
    
    def format_subgraph_for_display(self, subgraph: Dict) -> str:
        """
        Format subgraph for human-readable display
        
        Args:
            subgraph: Subgraph context
            
        Returns:
            Formatted string
        """
        entities_str = ', '.join(subgraph['entities'][:10])  # Limit to 10 entities
        if len(subgraph['entities']) > 10:
            entities_str += f" (and {len(subgraph['entities']) - 10} more)"
        
        formatted = f"""
Substance: {subgraph['substance_name']}
Section: {subgraph['section_name']}
Similarity Score: {subgraph['similarity_score']:.3f}
Word Count: {subgraph['word_count']}
Entities ({subgraph['entity_count']}): {entities_str}

Content:
{subgraph['section_text'][:500]}...
        """
        
        return formatted.strip()


def test_vector_search():
    """Test vector search functionality"""
    logging.basicConfig(level=logging.INFO)
    
    searcher = VectorSearcher()
    
    print("\n" + "="*80)
    print("VECTOR SEARCH TEST")
    print("="*80)
    
    # Test queries
    test_queries = [
        "What are the side effects?",
        "Can pregnant women take this?",
        "What are drug interactions?",
        "Is it safe for people with liver problems?"
    ]
    
    for query in test_queries:
        print(f"\n{'─'*80}")
        print(f"Query: {query}")
        print('─'*80)
        
        # Search with subgraphs
        subgraphs = searcher.search_with_subgraphs(query, top_k=3)
        
        if not subgraphs:
            print("No results found")
            continue
        
        # Display results
        for i, subgraph in enumerate(subgraphs, 1):
            print(f"\n[Result {i}]")
            print(searcher.format_subgraph_for_display(subgraph))
    
    searcher.close()
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_vector_search()
