"""
LLM Generator Module
Uses Ollama to generate natural language answers from retrieved context
"""

import logging
import requests
import json
from typing import List, Dict
from . import config

logger = logging.getLogger(__name__)


class LLMGenerator:
    """Generates answers using Ollama LLM"""
    
    def __init__(self):
        """Initialize LLM generator"""
        logger.info("Initializing LLM Generator...")
        logger.info(f"Ollama model: {config.OLLAMA_MODEL}")
        logger.info(f"Ollama API: {config.OLLAMA_API_URL}")
        
        # Verify Ollama is running
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✓ Ollama is running")
            else:
                logger.warning("⚠ Ollama may not be running properly")
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Cannot connect to Ollama: {e}")
            logger.error("Make sure Ollama is running: 'ollama serve'")
    
    def format_context(self, subgraphs: List[Dict]) -> str:
        """
        Format subgraph contexts for LLM prompt
        
        Uses enhanced format (Option: Enhanced)
        
        Args:
            subgraphs: List of re-ranked subgraph contexts
            
        Returns:
            Formatted context string
        """
        formatted_contexts = []
        
        for i, subgraph in enumerate(subgraphs, 1):
            # Enhanced format with metadata
            entities_str = ', '.join(subgraph['entities'][:15])  # Limit entities
            
            context_block = f"""[Source {i}]
Substance: {subgraph['substance_name']}
Section: {subgraph['section_name']}

Content:
{subgraph['section_text']}

Related Medical Terms: {entities_str}
"""
            formatted_contexts.append(context_block)
        
        # Join all contexts
        full_context = '\n' + ('─' * 80) + '\n'.join(formatted_contexts)
        
        # Truncate if too long
        if len(full_context) > config.MAX_CONTEXT_LENGTH:
            logger.warning(f"Context truncated from {len(full_context)} to {config.MAX_CONTEXT_LENGTH} chars")
            full_context = full_context[:config.MAX_CONTEXT_LENGTH] + "\n...(truncated)"
        
        return full_context
    
    def build_prompt(self, query: str, subgraphs: List[Dict]) -> str:
        """
        Build complete prompt for LLM
        
        Uses strict mode (Option A) to prevent hallucination
        
        Args:
            query: User's question
            subgraphs: Re-ranked subgraph contexts
            
        Returns:
            Complete prompt
        """
        # Format context
        context = self.format_context(subgraphs)
        
        # Build prompt (strict mode)
        prompt = f"""{config.SYSTEM_PROMPT}

{context}

{'='*80}

User Question: {query}

Instructions:
- Answer using ONLY the information provided in the sources above
- Mention which substance and section your answer comes from
- If the information is not in the sources, clearly state this
- Be helpful but never make up information

Answer:"""
        
        return prompt
    
    def generate_answer(self, query: str, subgraphs: List[Dict]) -> Dict:
        """
        Generate answer using Ollama
        
        Args:
            query: User's question
            subgraphs: Re-ranked subgraph contexts
            
        Returns:
            Dictionary with answer and metadata
        """
        if not subgraphs:
            return {
                'answer': "I don't have any relevant information in my knowledge base to answer this question.",
                'sources': [],
                'error': None
            }
        
        logger.info("Generating answer with Ollama...")
        
        # Build prompt
        prompt = self.build_prompt(query, subgraphs)
        
        # Log prompt in debug mode
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Prompt:\n{prompt}")
        
        # Call Ollama API
        try:
            payload = {
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": config.OLLAMA_TEMPERATURE,
                    "num_predict": config.OLLAMA_MAX_TOKENS
                }
            }
            
            response = requests.post(
                config.OLLAMA_API_URL,
                json=payload,
                timeout=120  # 2 minute timeout
            )
            
            if response.status_code != 200:
                error_msg = f"Ollama API error: {response.status_code}"
                logger.error(error_msg)
                return {
                    'answer': "Error generating answer. Please try again.",
                    'sources': [],
                    'error': error_msg
                }
            
            # Parse response
            result = response.json()
            answer = result.get('response', '').strip()
            
            # Extract sources
            sources = [
                {
                    'substance_name': sg['substance_name'],
                    'section_name': sg['section_name'],
                    'similarity_score': sg['similarity_score'],
                    'cross_encoder_score': sg.get('cross_encoder_score', 0.0)
                }
                for sg in subgraphs
            ]
            
            logger.info("✓ Answer generated")
            
            return {
                'answer': answer,
                'sources': sources,
                'error': None,
                'model': config.OLLAMA_MODEL,
                'temperature': config.OLLAMA_TEMPERATURE
            }
        
        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out"
            logger.error(error_msg)
            return {
                'answer': "Answer generation timed out. Please try again with a simpler question.",
                'sources': [],
                'error': error_msg
            }
        
        except Exception as e:
            error_msg = f"Error calling Ollama: {e}"
            logger.error(error_msg)
            return {
                'answer': "Error generating answer. Please try again.",
                'sources': [],
                'error': error_msg
            }
    
    def format_answer_with_sources(self, result: Dict) -> str:
        """
        Format answer with source attribution for display
        
        Args:
            result: Result from generate_answer()
            
        Returns:
            Formatted answer with sources
        """
        answer = result['answer']
        sources = result['sources']
        
        # Add source attribution if enabled
        if config.INCLUDE_SOURCE_ATTRIBUTION and sources:
            sources_text = "\n\n" + "─" * 60 + "\nSources:\n"
            for i, source in enumerate(sources, 1):
                sources_text += f"{i}. {source['substance_name']} - {source['section_name']}\n"
            
            formatted = answer + sources_text
        else:
            formatted = answer
        
        return formatted


def test_llm_generator():
    """Test LLM generation"""
    logging.basicConfig(level=logging.DEBUG)
    
    # Mock subgraphs
    mock_subgraphs = [
        {
            'substance_name': 'Asparagus',
            'section_name': 'Safety',
            'section_text': 'PREGNANCY: Likely Safe when used in amounts commonly found in foods. PREGNANCY: Possibly Unsafe when used in larger amounts for medicinal purposes. Asparagus extracts may have contraceptive effects; avoid using.',
            'entities': ['Pregnancy', 'Contraceptive Effects'],
            'similarity_score': 0.85,
            'cross_encoder_score': 0.92,
            'word_count': 150,
            'entity_count': 2
        },
        {
            'substance_name': 'Asparagus',
            'section_name': 'AdverseEffects',
            'section_text': 'Asparagus is usually well tolerated when used in food amounts. Orally and topically, asparagus can cause allergic reactions in individuals sensitive to other members of the Liliaceae family.',
            'entities': ['Allergic Reactions', 'Liliaceae'],
            'similarity_score': 0.72,
            'cross_encoder_score': 0.68,
            'word_count': 100,
            'entity_count': 2
        }
    ]
    
    print("\n" + "="*80)
    print("LLM GENERATION TEST")
    print("="*80)
    
    generator = LLMGenerator()
    
    # Test query
    query = "Is asparagus safe for pregnant women?"
    
    print(f"\nQuery: {query}")
    print("\n" + "─"*80)
    print("Generating answer...")
    print("─"*80)
    
    # Generate answer
    result = generator.generate_answer(query, mock_subgraphs)
    
    if result['error']:
        print(f"\n✗ Error: {result['error']}")
    else:
        print(f"\nAnswer:\n{result['answer']}")
        
        if result['sources']:
            print("\n" + "─"*60)
            print("Sources:")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['substance_name']} - {source['section_name']}")
                print(f"   Similarity: {source['similarity_score']:.3f}, Cross-encoder: {source['cross_encoder_score']:.3f}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_llm_generator()
