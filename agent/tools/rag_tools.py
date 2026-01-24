"""
RAG (Retrieval-Augmented Generation) tool for business documents.

This tool allows the agent to search business rules and documentation
stored in a vector database.

The business documents are SEPARATE from the analytics data.
They provide context about:
- ROAS thresholds and scaling decisions
- CPI and eCPM benchmarks
- Alert severity definitions
- Company policies and procedures
"""

import os
from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration
DOCS_DIR = Path(__file__).parent.parent.parent / "docs" / "business_rules"
VECTOR_STORE_PATH = Path(__file__).parent.parent / "vector_store"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Global vector store (lazy loaded)
_vector_store = None


def load_documents() -> list:
    """Load all markdown documents from the business_rules directory."""
    from langchain_core.documents import Document

    documents = []

    if not DOCS_DIR.exists():
        return documents

    for file_path in DOCS_DIR.glob("*.md"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Create document with metadata
        doc = Document(
            page_content=content,
            metadata={"source": file_path.name}
        )
        documents.append(doc)

    return documents


def chunk_documents(documents: list) -> list:
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n---\n", "\n## ", "\n### ", "\n\n", "\n", " "]
    )

    chunks = splitter.split_documents(documents)
    return chunks


def get_vector_store():
    """Get or create the FAISS vector store."""
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

    # Try to load existing vector store
    if VECTOR_STORE_PATH.exists():
        try:
            _vector_store = FAISS.load_local(
                str(VECTOR_STORE_PATH),
                embeddings,
                allow_dangerous_deserialization=True
            )
            return _vector_store
        except Exception:
            pass  # Will rebuild

    # Build new vector store
    documents = load_documents()
    if not documents:
        return None

    chunks = chunk_documents(documents)

    _vector_store = FAISS.from_documents(chunks, embeddings)

    # Save for future use
    VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
    _vector_store.save_local(str(VECTOR_STORE_PATH))

    return _vector_store


@tool
def search_business_documents(
    query: Annotated[str, "The question or topic to search for in business documents"],
    num_results: Annotated[int, "Number of relevant sections to return (default 3)"] = 3
) -> str:
    """
    Search Ameno's business rules and documentation.

    Use this tool when asked about:
    - ROAS thresholds or scaling decisions
    - CPI or eCPM benchmarks
    - Alert severity definitions (what is critical/warning)
    - Company policies or procedures
    - Business rules or guidelines
    - "What should I do if..." questions
    - "What are the thresholds for..."

    This is SEPARATE from actual data queries (use query_snowflake for data).
    This provides the RULES for interpreting data.

    Args:
        query: The question or topic to search for
        num_results: How many relevant sections to return (default 3)

    Returns:
        Relevant sections from business documentation
    """
    try:
        vector_store = get_vector_store()

        if vector_store is None:
            return "No business documents found. Please add documents to docs/business_rules/"

        # Search for relevant documents
        results = vector_store.similarity_search(query, k=num_results)

        if not results:
            return f"No relevant business rules found for: {query}"

        # Format output
        output = f"**Business Rules & Guidelines** (found {len(results)} relevant sections)\n\n"

        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source", "unknown")
            content = doc.page_content.strip()

            output += f"---\n\n**[{i}] From: {source}**\n\n"
            output += f"{content}\n\n"

        return output

    except Exception as e:
        return f"Error searching business documents: {str(e)}"


def rebuild_vector_store():
    """Force rebuild of the vector store from documents."""
    global _vector_store

    # Clear existing
    _vector_store = None
    if VECTOR_STORE_PATH.exists():
        import shutil
        shutil.rmtree(VECTOR_STORE_PATH)

    # Rebuild
    return get_vector_store()


# Test function
if __name__ == "__main__":
    print("Testing RAG tool...\n")

    # Force rebuild to test
    print("Rebuilding vector store...")
    vs = rebuild_vector_store()

    if vs is None:
        print("No documents found!")
    else:
        print(f"Vector store built successfully")
        print(f"Documents directory: {DOCS_DIR}")
        print(f"Vector store path: {VECTOR_STORE_PATH}")

    print("\n" + "=" * 50)
    print("Testing search...")
    print("=" * 50 + "\n")

    # Test queries
    test_queries = [
        "What are the ROAS thresholds for scaling decisions?",
        "What is a critical alert?",
        "What is the target CPI for iOS in the US?",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}\n")
        result = search_business_documents.invoke({"query": query})
        print(result)
        print("\n" + "-" * 50)
