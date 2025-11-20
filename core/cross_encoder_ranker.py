"""
Cross-Encoder Re-ranking Module
Re-ranks vector search results using cross-encoder for better relevance
"""

import logging
from typing import List, Dict, Tuple
from sentence_transformers import CrossEncoder
from . import config

logger = logging.getLogger(__name__)


class CrossEncoderRanker:
    """Re-ranks search results using cross-encoder model"""
    
    def __init__(self):
        """Initialize cross-encoder ranker"""
        logger.info("Initializing Cross-Encoder Ranker...")
        logger.info(f"Loading model: {config.CROSS_ENCODER_MODEL}")
        
        # Load cross-encoder model
        self.cross_encoder = CrossEncoder(config.CROSS_ENCODER_MODEL)
        
        logger.info("✓ Cross-encoder ready")
    
    def prepare_pair(self, query: str, subgraph: Dict) -> str:
        """
        Prepare (query, context) pair for cross-encoder
        
        Uses enhanced context format (Option: Enhanced)
        
        Args:
            query: User's question
            subgraph: Subgraph context dictionary
            
        Returns:
            Formatted context string
        """
        if config.ENHANCED_CONTEXT_FORMAT:
            # Enhanced format with metadata
            entities_str = ', '.join(subgraph['entities'][:20])  # Limit entities
            
            context = f"""Substance: {subgraph['substance_name']}
Section: {subgraph['section_name']}
Content: {subgraph['section_text']}
Related Medical Terms: {entities_str}"""
        else:
            # Simple format (just text)
            context = subgraph['section_text']
        
        return context
    
    def rerank(self, query: str, subgraphs: List[Dict], top_n: int = None) -> List[Dict]:
        """
        Re-rank subgraphs using cross-encoder
        
        Args:
            query: User's question
            subgraphs: List of subgraph contexts from vector search
            top_n: Number of top results to return (default from config)
            
        Returns:
            Re-ranked subgraphs (top N)
        """
        if top_n is None:
            top_n = config.TOP_N_RERANKED
        
        if not subgraphs:
            logger.warning("No subgraphs to rerank")
            return []
        
        logger.info(f"Re-ranking {len(subgraphs)} results with cross-encoder...")
        
        # Prepare query-context pairs
        pairs = []
        for subgraph in subgraphs:
            context = self.prepare_pair(query, subgraph)
            pairs.append([query, context])
        
        # Get cross-encoder scores
        scores = self.cross_encoder.predict(pairs)
        
        # Add cross-encoder scores to subgraphs
        for subgraph, score in zip(subgraphs, scores):
            subgraph['cross_encoder_score'] = float(score)
        
        # Sort by cross-encoder score (descending)
        reranked = sorted(subgraphs, key=lambda x: x['cross_encoder_score'], reverse=True)
        
        # Keep top N
        top_reranked = reranked[:top_n]
        
        logger.info(f"✓ Re-ranked and selected top {len(top_reranked)} results")
        
        # Log score changes
        if logger.isEnabledFor(logging.DEBUG):
            for i, subgraph in enumerate(top_reranked, 1):
                logger.debug(
                    f"  [{i}] {subgraph['substance_name']}.{subgraph['section_name']} - "
                    f"Vector: {subgraph['similarity_score']:.3f}, "
                    f"Cross-encoder: {subgraph['cross_encoder_score']:.3f}"
                )
        
        return top_reranked
    
    def get_score_comparison(self, subgraphs_before: List[Dict], subgraphs_after: List[Dict]) -> Dict:
        """
        Compare rankings before and after re-ranking
        
        Useful for debugging and evaluation
        
        Args:
            subgraphs_before: Subgraphs before re-ranking (sorted by vector score)
            subgraphs_after: Subgraphs after re-ranking (sorted by cross-encoder score)
            
        Returns:
            Comparison statistics
        """
        # Check if top result changed
        top_changed = (
            subgraphs_before[0]['node_id'] != subgraphs_after[0]['node_id']
            if subgraphs_before and subgraphs_after
            else False
        )
        
        # Count how many results changed position
        before_ids = [s['node_id'] for s in subgraphs_before[:config.TOP_N_RERANKED]]
        after_ids = [s['node_id'] for s in subgraphs_after]
        
        position_changes = sum(1 for i, node_id in enumerate(after_ids) 
                              if i >= len(before_ids) or node_id != before_ids[i])
        
        return {
            'top_result_changed': top_changed,
            'position_changes': position_changes,
            'total_results': len(subgraphs_after)
        }


def test_reranker():
    """Test re-ranking functionality"""
    logging.basicConfig(level=logging.DEBUG)
    
    # Mock subgraphs for testing
    mock_subgraphs = [
        {
            'node_id': '1',
            'substance_name': 'Asparagus',
            'section_name': 'AdverseEffects',
            'section_text': 'May cause allergic reactions in sensitive individuals.',
            'entities': ['Allergic Reactions'],
            'similarity_score': 0.75,
            'word_count': 100,
            'entity_count': 1
        },
        {
            'node_id': '2',
            'substance_name': 'Asparagus',
            'section_name': 'Safety',
            'section_text': 'Likely safe when used in food amounts during pregnancy.',
            'entities': ['Pregnancy'],
            'similarity_score': 0.70,
            'word_count': 150,
            'entity_count': 1
        },
        {
            'node_id': '3',
            'substance_name': 'Asparagus',
            'section_name': 'Effectiveness',
            'section_text': 'Insufficient reliable evidence for effectiveness.',
            'entities': [],
            'similarity_score': 0.65,
            'word_count': 80,
            'entity_count': 0
        }
    ]
    
    print("\n" + "="*80)
    print("CROSS-ENCODER RE-RANKING TEST")
    print("="*80)
    
    ranker = CrossEncoderRanker()
    
    # Test query
    query = "Is asparagus safe during pregnancy?"
    
    print(f"\nQuery: {query}")
    print("\n" + "─"*80)
    print("BEFORE RE-RANKING (Vector Search Order):")
    print("─"*80)
    
    for i, subgraph in enumerate(mock_subgraphs, 1):
        print(f"\n[{i}] {subgraph['substance_name']}.{subgraph['section_name']}")
        print(f"    Vector Score: {subgraph['similarity_score']:.3f}")
        print(f"    Text: {subgraph['section_text'][:100]}...")
    
    # Re-rank
    reranked = ranker.rerank(query, mock_subgraphs, top_n=2)
    
    print("\n" + "─"*80)
    print("AFTER RE-RANKING (Cross-Encoder Order):")
    print("─"*80)
    
    for i, subgraph in enumerate(reranked, 1):
        print(f"\n[{i}] {subgraph['substance_name']}.{subgraph['section_name']}")
        print(f"    Vector Score: {subgraph['similarity_score']:.3f}")
        print(f"    Cross-Encoder Score: {subgraph['cross_encoder_score']:.3f}")
        print(f"    Text: {subgraph['section_text'][:100]}...")
    
    # Compare
    comparison = ranker.get_score_comparison(mock_subgraphs, reranked)
    
    print("\n" + "─"*80)
    print("COMPARISON:")
    print("─"*80)
    print(f"Top result changed: {comparison['top_result_changed']}")
    print(f"Position changes: {comparison['position_changes']}/{comparison['total_results']}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_reranker()
