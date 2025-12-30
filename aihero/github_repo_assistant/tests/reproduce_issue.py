
from minsearch import Index


# Mock the minsearch behavior or just run index_data with a small known problematic input if we knew it.
# Instead, let's try to index a dummy doc that definitely has the keys, and see if it works.

def test_minsearch_basic():
    print("Testing basic minsearch...")
    docs = [
        {"content": "foo", "filename": "a.md"},
        {"content": "bar", "filename": "b.md"}
    ]
    index = Index(text_fields=["content", "filename"])
    try:
        index.fit(docs)
        print("✅ Basic fit passed")
    except Exception as e:
        print(f"❌ Basic fit failed: {e}")

# Now let's try to debug the actual flow by mocking read_repo_data to return somewhat messy data
# but we can't easily mock imports inside the function without patching.

if __name__ == "__main__":
    test_minsearch_basic()
    
    # Try to manually run the chunking logic and then index
    from ingest import create_chunks
    
    raw_docs = [
        {"content": "This is long content", "filename": "real.md", "extra": "stuff"}
    ]
    print("\nRunning chunking...")
    chunks = create_chunks(raw_docs, size=6, step=5)
    print(f"Chunks: {chunks}")
    
    print("Indexing chunks...")
    index = Index(text_fields=["content", "filename"])
    try:
        index.fit(chunks)
        print("✅ Chunk indexing passed")
    except Exception as e:
        print(f"❌ Chunk indexing failed: {e}")
