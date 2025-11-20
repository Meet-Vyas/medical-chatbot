"""
Embedding Manager
Generates embeddings for Section nodes and creates Neo4j vector index
ONE-TIME SETUP: Run this after graph generation completes
"""

import logging
from typing import List, Dict
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm
from . import config

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages embedding generation and storage for Section nodes"""
    
    def __init__(self):
        """Initialize embedding manager"""
        logger.info("Initializing Embedding Manager...")
        
        # Connect to Neo4j
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        
        # Load embedding model
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        logger.info(f"✓ Model loaded (dimension: {config.EMBEDDING_DIMENSION})")
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
    
    def get_all_sections(self) -> List[Dict]:
        """
        Retrieve all Section nodes from Neo4j
        
        Returns:
            List of section dictionaries with text and metadata
        """
        with self.driver.session() as session:
            query = """
            MATCH (sec:Section)
            RETURN sec.substance_name as substance_name,
                   sec.name as section_name,
                   sec.text as text,
                   sec.entity_count as entity_count,
                   elementId(sec) as node_id
            """
            result = session.run(query)
            sections = []
            
            for record in result:
                sections.append({
                    'node_id': record['node_id'],
                    'substance_name': record['substance_name'],
                    'section_name': record['section_name'],
                    'text': record['text'],
                    'entity_count': record['entity_count'] or 0
                })
            
            return sections
    
    def get_section_entities(self, substance_name: str, section_name: str) -> List[str]:
        """
        Get entities mentioned in a specific section
        
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
            RETURN e.name as entity_name
            """
            result = session.run(
                query,
                substance_name=substance_name,
                section_name=section_name
            )
            
            entities = [record['entity_name'] for record in result]
            return entities
    
    def prepare_text_for_embedding(self, section: Dict) -> str:
        """
        Prepare text for embedding (Option C: section text + entities)
        
        Args:
            section: Section dictionary
            
        Returns:
            Text to embed
        """
        text = section['text']
        
        if config.INCLUDE_ENTITIES_IN_EMBEDDING and section['entity_count'] > 0:
            # Get entities for this section
            entities = self.get_section_entities(
                section['substance_name'],
                section['section_name']
            )
            
            if entities:
                # Append entities to text
                entity_text = ', '.join(entities)
                text = f"{text}\n\nKey medical terms: {entity_text}"
        
        return text
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a batch of texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Array of embeddings
        """
        embeddings = self.embedding_model.encode(
            texts,
            batch_size=config.EMBEDDING_BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True  # Important for cosine similarity
        )
        return embeddings
    
    def store_embedding(self, node_id: str, embedding: np.ndarray):
        """
        Store embedding in Section node
        
        Args:
            node_id: Neo4j node element ID
            embedding: Embedding vector
        """
        with self.driver.session() as session:
            # Convert numpy array to list for Neo4j
            embedding_list = embedding.tolist()
            
            query = """
            MATCH (sec:Section)
            WHERE elementId(sec) = $node_id
            SET sec.embedding = $embedding
            """
            session.run(query, node_id=node_id, embedding=embedding_list)
    
    def create_vector_index(self):
        """
        Create Neo4j vector index on Section.embedding
        
        NOTE: Requires Neo4j 5.x with vector index support
        """
        with self.driver.session() as session:
            logger.info("Creating vector index...")
            
            # Check if index already exists
            check_query = "SHOW INDEXES YIELD name WHERE name = $index_name RETURN count(*) as count"
            result = session.run(check_query, index_name=config.VECTOR_INDEX_NAME)
            exists = result.single()['count'] > 0
            
            if exists:
                logger.info(f"Vector index '{config.VECTOR_INDEX_NAME}' already exists")
                return
            
            # Create vector index
            create_query = f"""
            CREATE VECTOR INDEX {config.VECTOR_INDEX_NAME} IF NOT EXISTS
            FOR (s:Section)
            ON s.embedding
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: {config.EMBEDDING_DIMENSION},
                    `vector.similarity_function`: '{config.SIMILARITY_METRIC}'
                }}
            }}
            """
            
            try:
                session.run(create_query)
                logger.info(f"✓ Created vector index: {config.VECTOR_INDEX_NAME}")
            except Exception as e:
                logger.error(f"Failed to create vector index: {e}")
                logger.error("Make sure you're using Neo4j 5.x with vector index support")
                raise
    
    def add_embeddings_to_graph(self):
        """
        Main method: Add embeddings to all Section nodes
        
        This is the ONE-TIME SETUP that should be run after graph generation
        """
        logger.info("\n" + "="*80)
        logger.info("ADDING EMBEDDINGS TO SECTION NODES")
        logger.info("="*80)
        
        # Step 1: Get all sections
        logger.info("\n[Step 1] Retrieving Section nodes from Neo4j...")
        sections = self.get_all_sections()
        logger.info(f"✓ Found {len(sections)} sections")
        
        if not sections:
            logger.error("No Section nodes found in database!")
            logger.error("Make sure you've run the graph generation pipeline first.")
            return
        
        # Step 2: Prepare texts for embedding
        logger.info("\n[Step 2] Preparing texts for embedding...")
        texts_to_embed = []
        
        for section in tqdm(sections, desc="Preparing texts"):
            text = self.prepare_text_for_embedding(section)
            texts_to_embed.append(text)
        
        logger.info(f"✓ Prepared {len(texts_to_embed)} texts")
        
        # Step 3: Generate embeddings in batches
        logger.info(f"\n[Step 3] Generating embeddings (batch size: {config.EMBEDDING_BATCH_SIZE})...")
        
        all_embeddings = []
        for i in tqdm(range(0, len(texts_to_embed), config.EMBEDDING_BATCH_SIZE), desc="Generating embeddings"):
            batch_texts = texts_to_embed[i:i + config.EMBEDDING_BATCH_SIZE]
            batch_embeddings = self.generate_embeddings_batch(batch_texts)
            all_embeddings.append(batch_embeddings)
        
        # Concatenate all batches
        all_embeddings = np.vstack(all_embeddings)
        logger.info(f"✓ Generated {len(all_embeddings)} embeddings")
        logger.info(f"  Embedding shape: {all_embeddings.shape}")
        
        # Step 4: Store embeddings in Neo4j
        logger.info("\n[Step 4] Storing embeddings in Neo4j...")
        
        for section, embedding in tqdm(zip(sections, all_embeddings), 
                                       total=len(sections), 
                                       desc="Storing embeddings"):
            self.store_embedding(section['node_id'], embedding)
        
        logger.info("✓ All embeddings stored")
        
        # Step 5: Create vector index
        logger.info("\n[Step 5] Creating vector index...")
        self.create_vector_index()
        
        # Final statistics
        logger.info("\n" + "="*80)
        logger.info("EMBEDDING SETUP COMPLETE")
        logger.info("="*80)
        logger.info(f"Sections processed: {len(sections)}")
        logger.info(f"Embedding dimension: {config.EMBEDDING_DIMENSION}")
        logger.info(f"Vector index: {config.VECTOR_INDEX_NAME}")
        logger.info(f"Model: {config.EMBEDDING_MODEL}")
        logger.info("\n✓ Your knowledge graph is now ready for vector search!")
    
    def verify_embeddings(self) -> Dict:
        """
        Verify that embeddings were added correctly
        
        Returns:
            Statistics about embeddings
        """
        with self.driver.session() as session:
            # Check how many sections have embeddings
            query = """
            MATCH (sec:Section)
            RETURN count(sec) as total_sections,
                   count(sec.embedding) as sections_with_embeddings
            """
            result = session.run(query)
            record = result.single()
            
            stats = {
                'total_sections': record['total_sections'],
                'sections_with_embeddings': record['sections_with_embeddings'],
                'missing_embeddings': record['total_sections'] - record['sections_with_embeddings']
            }
            
            return stats


def main():
    """Main entry point for embedding generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add embeddings to Section nodes')
    parser.add_argument('--verify', action='store_true', help='Only verify embeddings, don\'t generate')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    manager = EmbeddingManager()
    
    try:
        if args.verify:
            # Just verify
            logger.info("Verifying embeddings...")
            stats = manager.verify_embeddings()
            
            print("\n" + "="*60)
            print("EMBEDDING VERIFICATION")
            print("="*60)
            print(f"Total sections: {stats['total_sections']}")
            print(f"Sections with embeddings: {stats['sections_with_embeddings']}")
            print(f"Missing embeddings: {stats['missing_embeddings']}")
            
            if stats['missing_embeddings'] == 0:
                print("\n✓ All sections have embeddings!")
            else:
                print(f"\n⚠ {stats['missing_embeddings']} sections are missing embeddings")
                print("Run without --verify flag to generate embeddings")
        else:
            # Generate embeddings
            manager.add_embeddings_to_graph()
            
            # Verify
            stats = manager.verify_embeddings()
            if stats['missing_embeddings'] > 0:
                logger.warning(f"⚠ {stats['missing_embeddings']} sections still missing embeddings")
    
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
    finally:
        manager.close()


if __name__ == "__main__":
    main()
