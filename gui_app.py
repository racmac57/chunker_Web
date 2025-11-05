"""
Streamlit GUI Application for ChromaDB Knowledge Base
Modern web interface for searching and managing the knowledge base

Version: 2.1.6
Author: R. A. Carucci
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Chunker Knowledge Base",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .result-card {
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize RAG system with caching
@st.cache_resource
def init_rag():
    """Initialize ChromaRAG system"""
    try:
        from rag_integration import ChromaRAG
        rag = ChromaRAG(persist_directory="./chroma_db")
        return rag, None
    except Exception as e:
        return None, str(e)

# Initialize
rag, init_error = init_rag()

# Sidebar navigation
st.sidebar.title("📚 Chunker Knowledge Base")
st.sidebar.markdown("**Version 2.1.6**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["Search", "Statistics", "Browse Chunks", "System Status"],
    index=0
)

# Show initialization status
if init_error:
    st.sidebar.error(f"⚠️ Initialization Error: {init_error}")
    st.sidebar.info("Make sure ChromaDB is initialized and rag_integration.py is available")
elif rag:
    try:
        stats = rag.get_collection_stats()
        st.sidebar.success(f"✅ Connected")
        st.sidebar.metric("Total Chunks", f"{stats['total_chunks']:,}")
    except Exception as e:
        st.sidebar.error(f"❌ Connection Error: {e}")

# Search Page
if page == "Search":
    st.title("🔍 Knowledge Base Search")
    st.markdown("Search the ChromaDB knowledge base using semantic similarity")
    
    if not rag:
        st.error("RAG system not initialized. Please check the System Status page.")
        st.stop()
    
    # Search input
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(
            "Enter search query",
            placeholder="e.g., How do I fix Excel vlookup errors?",
            key="search_query"
        )
    with col2:
        search_type = st.selectbox(
            "Search Type",
            ["Semantic", "Keyword"],
            help="Semantic: Vector similarity search\nKeyword: Keyword-based search"
        )
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            file_type_options = ["All", ".txt", ".md", ".xlsx", ".pdf", ".py", ".docx", ".json"]
            file_type = st.selectbox("File Type", file_type_options)
        with col2:
            department_options = ["All", "admin", "police", "legal"]
            department = st.selectbox("Department", department_options)
        with col3:
            n_results = st.slider("Number of Results", 1, 20, 5)
        
        ef_search = st.slider(
            "Search Accuracy (ef_search)",
            min_value=100,
            max_value=500,
            value=200,
            step=50,
            help="Higher values = more accurate but slower (HNSW parameter)"
        )
    
    # Search button
    if st.button("🔍 Search", type="primary", use_container_width=True) or query:
        if query:
            with st.spinner("Searching knowledge base..."):
                try:
                    start_time = datetime.now()
                    
                    if search_type == "Semantic":
                        results = rag.search_similar(
                            query=query,
                            n_results=n_results,
                            file_type=None if file_type == "All" else file_type,
                            department=None if department == "All" else department,
                            ef_search=ef_search
                        )
                    else:  # Keyword
                        keywords = query.split()
                        results = rag.search_by_keywords(keywords, n_results=n_results)
                    
                    search_time = (datetime.now() - start_time).total_seconds()
                    
                    if results:
                        st.success(f"✅ Found {len(results)} results in {search_time:.3f} seconds")
                        
                        # Display results
                        for i, result in enumerate(results, 1):
                            with st.container():
                                # Calculate similarity score
                                distance = result.get("distance", 1.0)
                                score = max(0.0, min(1.0, 1.0 - distance))
                                
                                # Metadata
                                metadata = result.get("metadata", {})
                                file_name = metadata.get("file_name", "Unknown")
                                file_type = metadata.get("file_type", "unknown")
                                dept = metadata.get("department", "unknown")
                                chunk_idx = metadata.get("chunk_index", "?")
                                
                                # Result card
                                col1, col2 = st.columns([4, 1])
                                
                                with col1:
                                    st.markdown(f"### {i}. {file_name}")
                                    st.caption(
                                        f"Type: {file_type} | Department: {dept} | "
                                        f"Chunk: {chunk_idx} | ID: {result['id'][:50]}..."
                                    )
                                    
                                    with st.expander("📄 View Full Content", expanded=False):
                                        st.text_area(
                                            "Chunk Content",
                                            result["document"],
                                            height=200,
                                            key=f"content_{i}",
                                            label_visibility="collapsed"
                                        )
                                    
                                    # Keywords if available
                                    keywords_str = metadata.get("keywords", "")
                                    if keywords_str:
                                        try:
                                            keywords = json.loads(keywords_str) if isinstance(keywords_str, str) else keywords_str
                                            if keywords:
                                                st.caption(f"Keywords: {', '.join(keywords[:5])}")
                                        except:
                                            pass
                                
                                with col2:
                                    st.metric("Relevance", f"{score:.1%}")
                                    if st.button("📋 Copy ID", key=f"copy_id_{i}"):
                                        st.code(result["id"], language=None)
                                
                                st.divider()
                        
                        # Export results
                        with st.expander("💾 Export Results"):
                            export_format = st.radio("Export Format", ["JSON", "CSV"])
                            
                            if export_format == "JSON":
                                export_data = {
                                    "query": query,
                                    "timestamp": datetime.now().isoformat(),
                                    "results": [
                                        {
                                            "id": r["id"],
                                            "content": r["document"],
                                            "score": 1.0 - r.get("distance", 0.0),
                                            "metadata": r["metadata"]
                                        }
                                        for r in results
                                    ]
                                }
                                st.download_button(
                                    "Download JSON",
                                    json.dumps(export_data, indent=2),
                                    file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                    mime="application/json"
                                )
                            else:  # CSV
                                csv_data = []
                                for r in results:
                                    metadata = r.get("metadata", {})
                                    csv_data.append({
                                        "ID": r["id"],
                                        "File Name": metadata.get("file_name", ""),
                                        "File Type": metadata.get("file_type", ""),
                                        "Department": metadata.get("department", ""),
                                        "Chunk Index": metadata.get("chunk_index", ""),
                                        "Score": 1.0 - r.get("distance", 0.0),
                                        "Content Preview": r["document"][:100] + "..."
                                    })
                                
                                df = pd.DataFrame(csv_data)
                                csv = df.to_csv(index=False)
                                st.download_button(
                                    "Download CSV",
                                    csv,
                                    file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
                    else:
                        st.warning("No results found. Try a different query or adjust filters.")
                        
                except Exception as e:
                    st.error(f"Search failed: {e}")
                    st.exception(e)
        else:
            st.info("Enter a search query to begin")

# Statistics Page
elif page == "Statistics":
    st.title("📊 Knowledge Base Statistics")
    
    if not rag:
        st.error("RAG system not initialized.")
        st.stop()
    
    try:
        stats = rag.get_collection_stats()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Chunks", f"{stats['total_chunks']:,}")
        with col2:
            st.metric("Collection", stats['collection_name'])
        with col3:
            last_updated = stats.get('last_updated', '')
            if last_updated:
                date_str = last_updated[:10] if len(last_updated) >= 10 else last_updated
                st.metric("Last Updated", date_str)
            else:
                st.metric("Last Updated", "N/A")
        with col4:
            # Get sample chunk to show metadata structure
            try:
                sample = rag.collection.get(limit=1)
                if sample["ids"]:
                    st.metric("Status", "✅ Active")
                else:
                    st.metric("Status", "⚠️ Empty")
            except:
                st.metric("Status", "❓ Unknown")
        
        st.markdown("---")
        
        # Detailed statistics
        st.subheader("Collection Information")
        
        # Get all chunks for analysis
        try:
            all_data = rag.collection.get()
            total_chunks = len(all_data["ids"])
            
            if total_chunks > 0:
                # Analyze by department
                dept_counts = {}
                file_type_counts = {}
                
                for metadata in all_data.get("metadatas", []):
                    dept = metadata.get("department", "unknown")
                    file_type = metadata.get("file_type", "unknown")
                    
                    dept_counts[dept] = dept_counts.get(dept, 0) + 1
                    file_type_counts[file_type] = file_type_counts.get(file_type, 0) + 1
                
                # Display charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("By Department")
                    if dept_counts:
                        dept_df = pd.DataFrame(list(dept_counts.items()), columns=["Department", "Count"])
                        st.bar_chart(dept_df.set_index("Department"))
                        st.dataframe(dept_df, use_container_width=True)
                    else:
                        st.info("No department data available")
                
                with col2:
                    st.subheader("By File Type")
                    if file_type_counts:
                        type_df = pd.DataFrame(list(file_type_counts.items()), columns=["File Type", "Count"])
                        st.bar_chart(type_df.set_index("File Type"))
                        st.dataframe(type_df, use_container_width=True)
                    else:
                        st.info("No file type data available")
                
                # Metadata summary
                st.subheader("Metadata Summary")
                st.json({
                    "total_chunks": total_chunks,
                    "departments": list(dept_counts.keys()),
                    "file_types": list(file_type_counts.keys()),
                    "sample_metadata_keys": list(all_data["metadatas"][0].keys()) if all_data.get("metadatas") else []
                })
            else:
                st.warning("Knowledge base is empty")
                
        except Exception as e:
            st.error(f"Failed to analyze statistics: {e}")
            st.exception(e)
    except Exception as e:
        st.error(f"Failed to load statistics: {e}")
        st.exception(e)

# Browse Chunks Page
elif page == "Browse Chunks":
    st.title("📁 Browse Chunks")
    
    if not rag:
        st.error("RAG system not initialized.")
        st.stop()
    
    try:
        # Get all chunks with pagination
        all_data = rag.collection.get()
        total_chunks = len(all_data["ids"])
        
        if total_chunks == 0:
            st.warning("Knowledge base is empty")
            st.stop()
        
        st.info(f"Total chunks: {total_chunks}")
        
        # Pagination
        chunks_per_page = st.slider("Chunks per page", 10, 100, 20, step=10)
        total_pages = (total_chunks + chunks_per_page - 1) // chunks_per_page
        
        page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        
        start_idx = (page_num - 1) * chunks_per_page
        end_idx = min(start_idx + chunks_per_page, total_chunks)
        
        st.caption(f"Showing chunks {start_idx + 1} to {end_idx} of {total_chunks}")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_dept = st.selectbox("Filter by Department", ["All"] + list(set(
                m.get("department", "unknown") for m in all_data.get("metadatas", [])
            )))
        with col2:
            filter_type = st.selectbox("Filter by File Type", ["All"] + list(set(
                m.get("file_type", "unknown") for m in all_data.get("metadatas", [])
            )))
        
        # Display chunks
        displayed = 0
        for i in range(start_idx, end_idx):
            if i >= len(all_data["ids"]):
                break
            
            chunk_id = all_data["ids"][i]
            metadata = all_data["metadatas"][i] if i < len(all_data.get("metadatas", [])) else {}
            document = all_data["documents"][i] if i < len(all_data.get("documents", [])) else ""
            
            # Apply filters
            if filter_dept != "All" and metadata.get("department") != filter_dept:
                continue
            if filter_type != "All" and metadata.get("file_type") != filter_type:
                continue
            
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    file_name = metadata.get("file_name", "Unknown")
                    st.markdown(f"**{file_name}**")
                    st.caption(
                        f"Type: {metadata.get('file_type', '?')} | "
                        f"Dept: {metadata.get('department', '?')} | "
                        f"Chunk: {metadata.get('chunk_index', '?')}"
                    )
                    
                    with st.expander("View Content"):
                        st.text_area(
                            "Content",
                            document,
                            height=150,
                            key=f"browse_{i}",
                            label_visibility="collapsed"
                        )
                
                with col2:
                    st.code(chunk_id[:30] + "...", language=None)
                    if st.button("📋 Copy ID", key=f"browse_copy_{i}"):
                        st.code(chunk_id, language=None)
                
                st.divider()
                displayed += 1
        
        if displayed == 0:
            st.info("No chunks match the selected filters")
            
    except Exception as e:
        st.error(f"Failed to browse chunks: {e}")
        st.exception(e)

# System Status Page
elif page == "System Status":
    st.title("⚙️ System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ChromaDB Connection")
        if rag:
            try:
                stats = rag.get_collection_stats()
                st.success("✅ Connected")
                
                st.json(stats)
                
                # Test query
                if st.button("Test Query", key="test_query"):
                    with st.spinner("Testing query..."):
                        try:
                            test_results = rag.search_similar("test", n_results=1)
                            st.success(f"✅ Query successful! Found {len(test_results)} result(s)")
                        except Exception as e:
                            st.error(f"❌ Query failed: {e}")
            except Exception as e:
                st.error(f"❌ Connection Error: {e}")
                st.exception(e)
        else:
            st.error("❌ RAG system not initialized")
            if init_error:
                st.code(init_error)
    
    with col2:
        st.subheader("HNSW Index Configuration")
        st.info("""
        **Current Settings:**
        - M (connections): 32
        - ef_construction: 512
        - ef_search: 200 (default)
        
        **Optimized for:** 3,200+ chunks
        """)
        
        st.subheader("System Information")
        st.code(f"""
Python Version: {st.sys.version}
ChromaDB: 1.3.2+
Collection: chunker_knowledge_base
Persist Directory: ./chroma_db
        """)
        
        # Configuration file
        if Path("config.json").exists():
            with st.expander("View Configuration"):
                try:
                    with open("config.json", "r") as f:
                        config = json.load(f)
                    st.json(config)
                except Exception as e:
                    st.error(f"Failed to load config: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Enterprise Chunker v2.1.6**")
st.sidebar.markdown("RAG-powered knowledge base")

# Run instructions in sidebar
with st.sidebar.expander("ℹ️ Usage Tips"):
    st.markdown("""
    **Search Tips:**
    - Use natural language queries
    - Try different search types (Semantic vs Keyword)
    - Adjust ef_search for accuracy/speed tradeoff
    
    **Keyboard Shortcuts:**
    - Press Enter in search box to search
    - Use filters to narrow results
    
    **Export:**
    - Export search results as JSON or CSV
    - Copy chunk IDs for programmatic access
    """)

