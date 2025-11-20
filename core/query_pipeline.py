"""
Query Pipeline
Orchestrates the complete query flow: Vector Search → Re-ranking → LLM Generation
"""

import logging
import time
from typing import Dict
from .vector_search import VectorSearcher
from .cross_encoder_ranker import CrossEncoderRanker
from .llm_generator import LLMGenerator
from . import config

logger = logging.getLogger(__name__)


class QueryPipeline:
    """Complete RAG pipeline for answering queries"""
    
    def __init__(self):
        """Initialize query pipeline"""
        logger.info("="*80)
        logger.info("INITIALIZING QUERY PIPELINE")
        logger.info("="*80)
        
        # Initialize components
        self.vector_searcher = VectorSearcher()
        self.reranker = CrossEncoderRanker()
        self.llm_generator = LLMGenerator()
        
        logger.info("="*80)
        logger.info("✓ QUERY PIPELINE READY")
        logger.info("="*80)
    
    def close(self):
        """Close connections"""
        self.vector_searcher.close()
    
    def process_query(self, query: str, verbose: bool = False) -> Dict:
        """
        Process a user query through the complete pipeline
        
        Args:
            query: User's question
            verbose: If True, print detailed progress
            
        Returns:
            Dictionary with answer and metadata
        """
        start_time = time.time()
        
        if verbose:
            print("\n" + "="*80)
            print("PROCESSING QUERY")
            print("="*80)
            print(f"Query: {query}\n")
        
        result = {
            'query': query,
            'answer': None,
            'sources': [],
            'error': None,
            'timing': {}
        }
        
        try:
            # Step 1: Vector Search
            if verbose:
                print("[Step 1] Vector Search...")
            
            step1_start = time.time()
            subgraphs = self.vector_searcher.search_with_subgraphs(
                query,
                top_k=config.TOP_K_VECTOR_SEARCH
            )
            result['timing']['vector_search'] = time.time() - step1_start
            
            if not subgraphs:
                result['answer'] = "I couldn't find any relevant information in my knowledge base for this question."
                result['timing']['total'] = time.time() - start_time
                return result
            
            if verbose:
                print(f"  ✓ Found {len(subgraphs)} sections")
                for i, sg in enumerate(subgraphs[:3], 1):
                    print(f"    [{i}] {sg['substance_name']}.{sg['section_name']} (score: {sg['similarity_score']:.3f})")
            
            # Step 2: Re-ranking
            if verbose:
                print("\n[Step 2] Cross-Encoder Re-ranking...")
            
            step2_start = time.time()
            reranked_subgraphs = self.reranker.rerank(
                query,
                subgraphs,
                top_n=config.TOP_N_RERANKED
            )
            result['timing']['reranking'] = time.time() - step2_start
            
            if verbose:
                print(f"  ✓ Re-ranked to top {len(reranked_subgraphs)}")
                for i, sg in enumerate(reranked_subgraphs, 1):
                    print(f"    [{i}] {sg['substance_name']}.{sg['section_name']} (cross-encoder: {sg['cross_encoder_score']:.3f})")
            
            # Step 3: Generate Answer with LLM
            if verbose:
                print("\n[Step 3] Generating Answer with Ollama...")
            
            step3_start = time.time()
            llm_result = self.llm_generator.generate_answer(query, reranked_subgraphs)
            result['timing']['llm_generation'] = time.time() - step3_start
            
            # Merge results
            result['answer'] = llm_result['answer']
            result['sources'] = llm_result['sources']
            result['error'] = llm_result['error']
            
            if verbose:
                if llm_result['error']:
                    print(f"  ✗ Error: {llm_result['error']}")
                else:
                    print("  ✓ Answer generated")
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            result['error'] = str(e)
            result['answer'] = "An error occurred while processing your question. Please try again."
        
        # Total time
        result['timing']['total'] = time.time() - start_time
        
        if verbose:
            print("\n" + "─"*80)
            print("TIMING:")
            print(f"  Vector Search: {result['timing'].get('vector_search', 0):.2f}s")
            print(f"  Re-ranking: {result['timing'].get('reranking', 0):.2f}s")
            print(f"  LLM Generation: {result['timing'].get('llm_generation', 0):.2f}s")
            print(f"  TOTAL: {result['timing']['total']:.2f}s")
        
        return result
    
    def format_result_for_display(self, result: Dict) -> str:
        """
        Format query result for display
        
        Args:
            result: Result from process_query()
            
        Returns:
            Formatted string
        """
        output = []
        
        # Answer
        output.append("ANSWER:")
        output.append("─" * 60)
        output.append(result['answer'])
        
        # Sources
        if result['sources'] and config.INCLUDE_SOURCE_ATTRIBUTION:
            output.append("\n" + "─" * 60)
            output.append("SOURCES:")
            for i, source in enumerate(result['sources'], 1):
                output.append(f"{i}. {source['substance_name']} - {source['section_name']}")
        
        # Timing
        if result['timing']:
            output.append("\n" + "─" * 60)
            output.append(f"Response time: {result['timing']['total']:.2f}s")
        
        return '\n'.join(output)


def test_pipeline():
    """Test the complete query pipeline"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    pipeline = QueryPipeline()
    
    print("\n" + "="*80)
    print("QUERY PIPELINE TEST")
    print("="*80)
    
    # Test queries
    test_queries = [
        "What are the side effects of asparagus?",
        "Can pregnant women take asparagus?",
        "Does asparagus interact with any drugs?",
        "Is asparagus effective for treating acne?"
    ]
    
    for query in test_queries:
        print("\n" + "="*80)
        result = pipeline.process_query(query, verbose=True)
        
        print("\n" + "="*80)
        print("RESULT:")
        print("="*80)
        print(pipeline.format_result_for_display(result))
        
        # Pause between queries
        input("\nPress Enter for next query...")
    
    pipeline.close()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_pipeline()
