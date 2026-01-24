"""
RAG Demo Script - Shows exactly how chunking and embedding work.

Run this during demo to explain RAG pipeline:
    uv run python agent/rag_demo.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load API key from config (handles .env)
from agent.config import OPENAI_API_KEY

DOCS_DIR = Path(__file__).parent.parent / "docs" / "business_rules"


def demo_step1_load_document():
    """Step 1: Load the raw document."""
    print("\n" + "=" * 60)
    print("STEP 1: LOAD DOCUMENT")
    print("=" * 60)

    doc_path = DOCS_DIR / "ameno_business_rules.md"
    with open(doc_path, "r") as f:
        content = f.read()

    print(f"\nDocument: {doc_path.name}")
    print(f"Total characters: {len(content):,}")
    print(f"Total words: {len(content.split()):,}")

    print("\n--- First 500 characters ---")
    print(content[:500])
    print("...")

    return content


def demo_step2_chunking(content: str):
    """Step 2: Split document into chunks."""
    print("\n" + "=" * 60)
    print("STEP 2: CHUNKING")
    print("=" * 60)

    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # Max ~500 characters per chunk
        chunk_overlap=50,     # 50 char overlap between chunks
        separators=["\n---\n", "\n## ", "\n### ", "\n\n", "\n", " "]
    )

    chunks = splitter.split_text(content)

    print(f"\nChunk settings:")
    print(f"  - chunk_size: 500 characters")
    print(f"  - chunk_overlap: 50 characters")
    print(f"  - separators: headers (##), paragraphs, lines")

    print(f"\nResult: {len(chunks)} chunks created")

    print("\n--- Sample Chunks ---")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n[Chunk {i+1}] ({len(chunk)} chars)")
        print("-" * 40)
        # Show first 200 chars of each chunk
        preview = chunk[:200].replace("\n", " ")
        print(f"{preview}...")

    return chunks


def demo_step3_embedding(chunks: list):
    """Step 3: Convert chunks to vectors (embeddings)."""
    print("\n" + "=" * 60)
    print("STEP 3: EMBEDDING")
    print("=" * 60)

    if not OPENAI_API_KEY:
        print("\n[!] OPENAI_API_KEY not set - showing mock example")
        print("\nHow it works:")
        print('  Input:  "ROAS measures profitability of user acquisition"')
        print('  Output: [0.012, -0.045, 0.078, ..., 0.033]  (1536 dimensions)')
        print("\nSimilar text = Similar vectors (close in vector space)")
        return None

    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

    print("\nEmbedding model: OpenAI text-embedding-ada-002")
    print("Vector dimensions: 1536")

    # Embed first 2 chunks as demo
    sample_chunks = chunks[:2]
    print(f"\nEmbedding {len(sample_chunks)} sample chunks...")

    vectors = embeddings.embed_documents(sample_chunks)

    for i, (chunk, vector) in enumerate(zip(sample_chunks, vectors)):
        preview = chunk[:50].replace("\n", " ")
        print(f"\n[Chunk {i+1}] \"{preview}...\"")
        print(f"  Vector: [{vector[0]:.4f}, {vector[1]:.4f}, {vector[2]:.4f}, ... , {vector[-1]:.4f}]")
        print(f"  Length: {len(vector)} dimensions")

    return vectors


def demo_step4_similarity_search(chunks: list):
    """Step 4: Show how similarity search works."""
    print("\n" + "=" * 60)
    print("STEP 4: SIMILARITY SEARCH")
    print("=" * 60)

    if not OPENAI_API_KEY:
        print("\n[!] OPENAI_API_KEY not set - showing concept only")
        print("\nHow similarity search works:")
        print("  1. User query: 'What are ROAS thresholds?'")
        print("  2. Embed query → [0.11, -0.44, 0.79, ...]")
        print("  3. Find chunks with similar vectors")
        print("  4. Return top K most similar chunks")
        return

    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document

    print("\nBuilding vector store from chunks...")

    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

    # Create documents from chunks
    docs = [Document(page_content=chunk) for chunk in chunks]

    # Build FAISS index
    vector_store = FAISS.from_documents(docs, embeddings)

    print(f"Vector store created with {len(chunks)} vectors")

    # Demo queries
    demo_queries = [
        "What are the ROAS thresholds for scaling?",
        "What is a critical alert?",
        "What CPI should I target for iOS in US?",
    ]

    print("\n--- Demo Queries ---")

    for query in demo_queries:
        print(f"\n🔍 Query: \"{query}\"")

        results = vector_store.similarity_search(query, k=2)

        for i, doc in enumerate(results):
            preview = doc.page_content[:150].replace("\n", " ")
            print(f"   [{i+1}] {preview}...")


def demo_step5_full_pipeline():
    """Step 5: Show the full RAG pipeline in action."""
    print("\n" + "=" * 60)
    print("STEP 5: FULL RAG PIPELINE")
    print("=" * 60)

    if not OPENAI_API_KEY:
        print("\n[!] OPENAI_API_KEY not set - cannot run full demo")
        return

    from agent.tools.rag_tools import search_business_documents

    query = "What should I do if D0 ROAS drops below 60%?"

    print(f"\nUser Question: \"{query}\"")
    print("\nRAG Pipeline:")
    print("  1. Embed query")
    print("  2. Search vector store")
    print("  3. Return relevant chunks")

    print("\n--- Result ---")
    result = search_business_documents.invoke({"query": query})
    print(result)


def main():
    """Run all demo steps."""
    print("\n" + "#" * 60)
    print("#  RAG (Retrieval-Augmented Generation) Demo")
    print("#" * 60)

    # Step 1: Load
    content = demo_step1_load_document()

    input("\n[Press Enter to continue to Step 2: Chunking...]")

    # Step 2: Chunk
    chunks = demo_step2_chunking(content)

    input("\n[Press Enter to continue to Step 3: Embedding...]")

    # Step 3: Embed
    demo_step3_embedding(chunks)

    input("\n[Press Enter to continue to Step 4: Similarity Search...]")

    # Step 4: Search
    demo_step4_similarity_search(chunks)

    input("\n[Press Enter to continue to Step 5: Full Pipeline...]")

    # Step 5: Full pipeline
    demo_step5_full_pipeline()

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
