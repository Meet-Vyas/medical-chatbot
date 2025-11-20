"""
Terminal Interface
Interactive command-line chatbot for testing
"""

import logging
from core.query_pipeline import QueryPipeline
from core import config


class TerminalChatbot:
    """Interactive terminal chatbot"""
    
    def __init__(self):
        """Initialize chatbot"""
        print("\n" + "="*80)
        print("MEDICAL KNOWLEDGE GRAPH CHATBOT")
        print("="*80)
        print("\nInitializing...")
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        
        # Initialize pipeline
        self.pipeline = QueryPipeline()
        self.query_count = 0
        
        print("\n✓ Chatbot ready!")
        self.print_help()
    
    def print_help(self):
        """Print help message"""
        print("\n" + "─"*80)
        print("COMMANDS:")
        print("  - Type your question and press Enter")
        print("  - 'help' - Show this message")
        print("  - 'verbose on/off' - Toggle verbose mode")
        print("  - 'quit' or 'exit' - Exit chatbot")
        print("─"*80)
    
    def run(self):
        """Run interactive chatbot loop"""
        verbose = False
        
        print("\nYou can ask me about:")
        print("  • Side effects and adverse reactions")
        print("  • Safety information and contraindications")
        print("  • Drug interactions")
        print("  • Effectiveness for various conditions")
        print("  • Dosing and administration")
        print("\nType your question below:\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self.print_help()
                    continue
                
                if user_input.lower() == 'verbose on':
                    verbose = True
                    print("✓ Verbose mode enabled")
                    continue
                
                if user_input.lower() == 'verbose off':
                    verbose = False
                    print("✓ Verbose mode disabled")
                    continue
                
                # Process query
                self.query_count += 1
                print()  # Blank line
                
                result = self.pipeline.process_query(user_input, verbose=verbose)
                
                # Display result
                if not verbose:
                    print("\n" + "─"*80)
                
                print(f"Bot: {result['answer']}")
                
                # Show sources if enabled
                if config.INCLUDE_SOURCE_ATTRIBUTION and result['sources']:
                    print("\n" + "─"*60)
                    print("Sources:")
                    for i, source in enumerate(result['sources'], 1):
                        print(f"  {i}. {source['substance_name']} - {source['section_name']}")
                
                # Show timing
                if result['timing']:
                    print(f"\n⏱️  Response time: {result['timing']['total']:.2f}s")
                
                print("─"*80 + "\n")
                
                # Log interaction if enabled
                if config.LOG_ALL_INTERACTIONS:
                    logging.info(f"Query #{self.query_count}: {user_input}")
                    logging.info(f"Answer: {result['answer'][:200]}...")
                    logging.info(f"Sources: {len(result['sources'])}, Time: {result['timing']['total']:.2f}s")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'quit' to exit or continue asking questions.")
            
            except Exception as e:
                print(f"\n✗ Error: {e}")
                logging.error(f"Chatbot error: {e}", exc_info=True)
    
    def close(self):
        """Close chatbot"""
        self.pipeline.close()
        print(f"\nTotal queries processed: {self.query_count}")


def main():
    """Main entry point"""
    chatbot = TerminalChatbot()
    
    try:
        chatbot.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    finally:
        chatbot.close()


if __name__ == "__main__":
    main()
