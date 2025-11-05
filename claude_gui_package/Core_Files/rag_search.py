"""
RAG Search Script for Chunker_v2
Interactive search interface for the knowledge base
"""

import os
import json
import logging
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class RAGSearchInterface:
    """
    Interactive search interface for RAG knowledge base.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize RAG search interface.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.rag_system = None
        self.langsmith = None
        
        # Initialize components
        self._initialize_components()
        
        logger.info("Initialized RAG Search Interface")
    
    def _initialize_components(self) -> None:
        """
        Initialize RAG system and LangSmith integration.
        """
        try:
            # Initialize Ollama RAG system
            from ollama_integration import initialize_ollama_rag
            self.rag_system = initialize_ollama_rag(
                model_name=self.config.get("ollama_model", "nomic-embed-text"),
                persist_dir=self.config.get("faiss_persist_dir", "./faiss_index")
            )
            
            # Load existing index
            if not self.rag_system.load_index():
                logger.warning("No existing FAISS index found. Run watcher_splitter.py first to build knowledge base.")
            
            # Initialize LangSmith (optional)
            if self.config.get("langsmith_enabled", False):
                from langsmith_integration import initialize_langsmith
                self.langsmith = initialize_langsmith(
                    api_key=self.config.get("langsmith_api_key"),
                    project=self.config.get("langsmith_project", "chunker-rag-eval")
                )
            
            logger.info("Components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def search(self, query: str, search_type: str = "hybrid", top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            search_type: Type of search (hybrid, semantic, keyword)
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            if not self.rag_system:
                return []
            
            # Perform search based on type
            if search_type == "hybrid":
                results = self.rag_system.hybrid_search(query, top_k=top_k)
            elif search_type == "semantic":
                results = self.rag_system.search_similar(query, top_k=top_k)
            elif search_type == "keyword":
                keywords = query.split()
                results = self.rag_system.search_by_keywords(keywords, top_k=top_k)
            else:
                logger.error(f"Unknown search type: {search_type}")
                return []
            
            # Add LangSmith tracing if enabled
            if self.langsmith:
                traced_results = self.langsmith.traced_rag_query(query, self.rag_system)
                logger.info("Query traced with LangSmith")
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def format_results(self, results: List[Dict[str, Any]], query: str) -> str:
        """
        Format search results for display.
        
        Args:
            results: Search results
            query: Original query
            
        Returns:
            Formatted results string
        """
        if not results:
            return f"No results found for query: '{query}'"
        
        output = [f"Search Results for: '{query}'", "=" * 50]
        
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            score = result.get("score", 0.0)
            search_type = result.get("type", "unknown")
            
            # Truncate content for display
            display_content = content[:200] + "..." if len(content) > 200 else content
            
            output.extend([
                f"\n{i}. Score: {score:.3f} ({search_type})",
                f"   Source: {metadata.get('source_file', 'Unknown')}",
                f"   Type: {metadata.get('file_type', 'Unknown')}",
                f"   Content: {display_content}",
                f"   Keywords: {', '.join(metadata.get('keywords', []))}"
            ])
        
        return "\n".join(output)
    
    def interactive_search(self) -> None:
        """
        Start interactive search session.
        """
        print("RAG Search Interface")
        print("=" * 50)
        print("Commands:")
        print("  search <query> - Search the knowledge base")
        print("  semantic <query> - Semantic similarity search")
        print("  keyword <query> - Keyword-based search")
        print("  stats - Show knowledge base statistics")
        print("  quit - Exit the interface")
        print()
        
        while True:
            try:
                command = input("RAG> ").strip()
                
                if not command:
                    continue
                
                if command.lower() == "quit":
                    print("Goodbye!")
                    break
                
                elif command.lower() == "stats":
                    self._show_stats()
                
                elif command.startswith("search "):
                    query = command[7:].strip()
                    if query:
                        self._perform_search(query, "hybrid")
                
                elif command.startswith("semantic "):
                    query = command[9:].strip()
                    if query:
                        self._perform_search(query, "semantic")
                
                elif command.startswith("keyword "):
                    query = command[8:].strip()
                    if query:
                        self._perform_search(query, "keyword")
                
                else:
                    print("Unknown command. Type 'help' for available commands.")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive search: {e}")
                print(f"Error: {e}")
    
    def _perform_search(self, query: str, search_type: str) -> None:
        """
        Perform search and display results.
        
        Args:
            query: Search query
            search_type: Type of search
        """
        start_time = datetime.now()
        results = self.search(query, search_type)
        end_time = datetime.now()
        
        # Display results
        formatted_results = self.format_results(results, query)
        print(formatted_results)
        
        # Show timing
        duration = (end_time - start_time).total_seconds()
        print(f"\nSearch completed in {duration:.3f} seconds")
        print(f"Found {len(results)} results")
    
    def _show_stats(self) -> None:
        """
        Show knowledge base statistics.
        """
        if not self.rag_system:
            print("RAG system not available")
            return
        
        stats = self.rag_system.get_stats()
        print("Knowledge Base Statistics:")
        print("=" * 30)
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    def batch_search(self, queries: List[str], output_file: str = None) -> List[Dict[str, Any]]:
        """
        Perform batch search on multiple queries.
        
        Args:
            queries: List of search queries
            output_file: Optional output file for results
            
        Returns:
            List of search results
        """
        results = []
        
        for query in queries:
            try:
                query_results = self.search(query)
                results.append({
                    "query": query,
                    "results": query_results,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Batch search failed for query '{query}': {e}")
                results.append({
                    "query": query,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        # Save results if output file specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved batch search results to {output_file}")
            except Exception as e:
                logger.error(f"Failed to save results: {e}")
        
        return results

def load_config(config_file: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def main():
    """
    Main function for RAG search script.
    """
    parser = argparse.ArgumentParser(description="RAG Search Interface for Chunker_v2")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--query", help="Single query to search")
    parser.add_argument("--batch", help="File containing batch queries (one per line)")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--search-type", choices=["hybrid", "semantic", "keyword"], 
                       default="hybrid", help="Type of search to perform")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Initialize search interface
    try:
        search_interface = RAGSearchInterface(config)
    except Exception as e:
        logger.error(f"Failed to initialize search interface: {e}")
        return
    
    # Handle different modes
    if args.interactive:
        search_interface.interactive_search()
    
    elif args.query:
        results = search_interface.search(args.query, args.search_type, args.top_k)
        formatted_results = search_interface.format_results(results, args.query)
        print(formatted_results)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(formatted_results)
    
    elif args.batch:
        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                queries = [line.strip() for line in f if line.strip()]
            
            results = search_interface.batch_search(queries, args.output)
            print(f"Processed {len(queries)} queries")
            
        except Exception as e:
            logger.error(f"Batch search failed: {e}")
    
    else:
        # Default to interactive mode
        search_interface.interactive_search()

# Example usage
if __name__ == "__main__":
    # Example configuration
    example_config = {
        "ollama_model": "nomic-embed-text",
        "faiss_persist_dir": "./faiss_index",
        "langsmith_enabled": False,
        "langsmith_api_key": None,
        "langsmith_project": "chunker-rag-eval"
    }
    
    # Example queries
    example_queries = [
        "How do I fix vlookup errors in Excel?",
        "What is Power BI query syntax?",
        "How do I use pandas for data analysis?"
    ]
    
    print("RAG Search Interface Example")
    print("=" * 40)
    
    # Initialize interface
    try:
        interface = RAGSearchInterface(example_config)
        
        # Perform example searches
        for query in example_queries:
            print(f"\nSearching: {query}")
            results = interface.search(query, top_k=3)
            formatted = interface.format_results(results, query)
            print(formatted)
            print("-" * 50)
        
        print("RAG search example completed successfully!")
        
    except Exception as e:
        print(f"Example failed: {e}")