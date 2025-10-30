"""
Enhanced RAG Dependencies Installation Script for Chunker_v2
Installs all required packages for RAG functionality
"""

import subprocess
import sys
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def install_package(package: str, description: str = "") -> bool:
    """
    Install a Python package using pip.
    
    Args:
        package: Package name and version
        description: Description of the package
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Installing {package}...")
        if description:
            print(f"  {description}")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], capture_output=True, text=True, check=True)
        
        print(f"✓ Successfully installed {package}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}")
        print(f"  Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error installing {package}: {e}")
        return False

def check_package_installed(package_name: str) -> bool:
    """
    Check if a package is already installed.
    
    Args:
        package_name: Name of the package to check
        
    Returns:
        True if installed, False otherwise
    """
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_core_dependencies() -> Dict[str, bool]:
    """
    Install core dependencies.
    
    Returns:
        Dictionary of installation results
    """
    core_packages = [
        ("nltk>=3.9.1", "Natural Language Toolkit"),
        ("psutil>=5.9.0", "System and process utilities"),
        ("numpy>=1.22.5", "Numerical computing"),
        ("pandas>=2.2.3", "Data manipulation and analysis"),
        ("scikit-learn>=1.7.2", "Machine learning library"),
    ]
    
    results = {}
    for package, description in core_packages:
        results[package] = install_package(package, description)
    
    return results

def install_rag_dependencies() -> Dict[str, bool]:
    """
    Install RAG-specific dependencies.
    
    Returns:
        Dictionary of installation results
    """
    rag_packages = [
        ("ollama>=0.3.3", "Ollama for local embeddings"),
        ("faiss-cpu>=1.8.0", "FAISS for vector similarity search"),
        ("sentence-transformers>=3.1.1", "Sentence transformers for embeddings"),
        ("langchain>=0.3.1", "LangChain framework"),
        ("langchain-community>=0.3.1", "LangChain community packages"),
        ("langsmith>=0.1.129", "LangSmith for tracing and evaluation"),
    ]
    
    results = {}
    for package, description in rag_packages:
        results[package] = install_package(package, description)
    
    return results

def install_file_processing_dependencies() -> Dict[str, bool]:
    """
    Install file processing dependencies.
    
    Returns:
        Dictionary of installation results
    """
    file_packages = [
        ("openpyxl>=3.1.5", "Excel file processing"),
        ("pypdf2>=3.0.1", "PDF file processing"),
        ("python-docx>=1.2.0", "Word document processing"),
        ("pyyaml>=6.0.2", "YAML file processing"),
        ("lxml>=4.9.0", "XML file processing"),
    ]
    
    results = {}
    for package, description in file_packages:
        results[package] = install_package(package, description)
    
    return results

def install_evaluation_dependencies() -> Dict[str, bool]:
    """
    Install evaluation and metrics dependencies.
    
    Returns:
        Dictionary of installation results
    """
    eval_packages = [
        ("rouge-score>=0.1.2", "ROUGE metrics for text evaluation"),
        ("bert-score>=0.3.13", "BERTScore for semantic similarity"),
    ]
    
    results = {}
    for package, description in eval_packages:
        results[package] = install_package(package, description)
    
    return results

def install_monitoring_dependencies() -> Dict[str, bool]:
    """
    Install monitoring and scheduling dependencies.
    
    Returns:
        Dictionary of installation results
    """
    monitoring_packages = [
        ("watchdog>=3.0.0", "File system monitoring"),
        ("schedule>=1.2.0", "Task scheduling"),
    ]
    
    results = {}
    for package, description in monitoring_packages:
        results[package] = install_package(package, description)
    
    return results

def install_optional_dependencies() -> Dict[str, bool]:
    """
    Install optional dependencies.
    
    Returns:
        Dictionary of installation results
    """
    optional_packages = [
        ("pdfminer.six>=20221105", "Alternative PDF processor"),
        ("pymupdf>=1.23.0", "Another PDF processing option"),
        ("chromadb>=0.5.11", "ChromaDB vector database (may fail on Windows)"),
    ]
    
    results = {}
    for package, description in optional_packages:
        results[package] = install_package(package, description)
    
    return results

def install_development_dependencies() -> Dict[str, bool]:
    """
    Install development and testing dependencies.
    
    Returns:
        Dictionary of installation results
    """
    dev_packages = [
        ("pytest>=7.0.0", "Testing framework"),
        ("pytest-cov>=4.0.0", "Test coverage"),
        ("black>=23.0.0", "Code formatting"),
        ("flake8>=6.0.0", "Code linting"),
        ("mypy>=1.0.0", "Type checking"),
    ]
    
    results = {}
    for package, description in dev_packages:
        results[package] = install_package(package, description)
    
    return results

def check_ollama_availability() -> bool:
    """
    Check if Ollama is available and the model is installed.
    
    Returns:
        True if Ollama is available, False otherwise
    """
    try:
        import ollama
        # Try to list models
        models = ollama.list()
        print(f"✓ Ollama is available with {len(models.get('models', []))} models")
        
        # Check for nomic-embed-text model
        model_names = [model['name'] for model in models.get('models', [])]
        if any('nomic-embed-text' in name for name in model_names):
            print("✓ nomic-embed-text model is available")
            return True
        else:
            print("⚠ nomic-embed-text model not found. Run: ollama pull nomic-embed-text")
            return False
            
    except ImportError:
        print("✗ Ollama package not available")
        return False
    except Exception as e:
        print(f"✗ Error checking Ollama: {e}")
        return False

def create_requirements_file() -> None:
    """
    Create requirements.txt file with all dependencies.
    """
    requirements = [
        "# Core dependencies",
        "nltk>=3.9.1",
        "psutil>=5.9.0",
        "numpy>=1.22.5",
        "pandas>=2.2.3",
        "scikit-learn>=1.7.2",
        "",
        "# RAG and Vector Database",
        "ollama>=0.3.3",
        "faiss-cpu>=1.8.0",
        "sentence-transformers>=3.1.1",
        "langchain>=0.3.1",
        "langchain-community>=0.3.1",
        "langsmith>=0.1.129",
        "",
        "# File Processing",
        "openpyxl>=3.1.5",
        "pypdf2>=3.0.1",
        "python-docx>=1.2.0",
        "pyyaml>=6.0.2",
        "lxml>=4.9.0",
        "",
        "# Evaluation Metrics",
        "rouge-score>=0.1.2",
        "bert-score>=0.3.13",
        "",
        "# Monitoring and Scheduling",
        "watchdog>=3.0.0",
        "schedule>=1.2.0",
        "",
        "# Optional Dependencies",
        "pdfminer.six>=20221105",
        "pymupdf>=1.23.0",
        "# chromadb>=0.5.11  # May fail on Windows",
        "",
        "# Development and Testing",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
    ]
    
    try:
        with open("requirements_rag.txt", "w") as f:
            f.write("\n".join(requirements))
        print("✓ Created requirements_rag.txt file")
    except Exception as e:
        print(f"✗ Failed to create requirements file: {e}")

def main():
    """
    Main installation function.
    """
    print("Chunker_v2 RAG Dependencies Installation")
    print("=" * 50)
    
    # Track installation results
    all_results = {}
    
    # Install dependencies in order
    print("\n1. Installing core dependencies...")
    all_results["core"] = install_core_dependencies()
    
    print("\n2. Installing RAG dependencies...")
    all_results["rag"] = install_rag_dependencies()
    
    print("\n3. Installing file processing dependencies...")
    all_results["file_processing"] = install_file_processing_dependencies()
    
    print("\n4. Installing evaluation dependencies...")
    all_results["evaluation"] = install_evaluation_dependencies()
    
    print("\n5. Installing monitoring dependencies...")
    all_results["monitoring"] = install_monitoring_dependencies()
    
    print("\n6. Installing optional dependencies...")
    all_results["optional"] = install_optional_dependencies()
    
    print("\n7. Installing development dependencies...")
    all_results["development"] = install_development_dependencies()
    
    # Check Ollama availability
    print("\n8. Checking Ollama availability...")
    ollama_available = check_ollama_availability()
    
    # Create requirements file
    print("\n9. Creating requirements file...")
    create_requirements_file()
    
    # Summary
    print("\n" + "=" * 50)
    print("Installation Summary:")
    print("=" * 50)
    
    total_packages = 0
    successful_packages = 0
    
    for category, results in all_results.items():
        category_total = len(results)
        category_successful = sum(1 for success in results.values() if success)
        
        total_packages += category_total
        successful_packages += category_successful
        
        print(f"{category}: {category_successful}/{category_total} packages installed")
    
    print(f"\nOverall: {successful_packages}/{total_packages} packages installed")
    
    if ollama_available:
        print("✓ Ollama is ready for use")
    else:
        print("⚠ Ollama setup required:")
        print("  1. Install Ollama: https://ollama.ai/")
        print("  2. Pull model: ollama pull nomic-embed-text")
    
    # Next steps
    print("\nNext Steps:")
    print("1. Run: python watcher_splitter.py (to build knowledge base)")
    print("2. Run: python rag_search.py (to search knowledge base)")
    print("3. Run: python automated_eval.py (for evaluation)")
    
    if successful_packages == total_packages:
        print("\n🎉 All dependencies installed successfully!")
    else:
        print(f"\n⚠ {total_packages - successful_packages} packages failed to install")
        print("Check the error messages above for details")

if __name__ == "__main__":
    main()