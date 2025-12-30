from ingest import index_data

if __name__ == "__main__":
    print("🚀 Starting debug ingestion for evidentlyai/docs...")
    try:
        index = index_data("evidentlyai", "docs")
        print("✅ Indexing successful!")
    except Exception as e:
        print(f"\n❌ Script captured compilation/runtime error: {e}")
