from chromadb import Client


def main():
    client = Client(settings={"persist_directory": "./chroma_db"})
    collection = client.get_collection("chunker_knowledge_base")
    data = collection.get(include=["metadatas", "ids"], limit=100000)
    ids = data.get("ids", [])
    metas = data.get("metadatas", [])

    updated_metadatas = []
    for metadata in metas:
        meta = dict(metadata or {})
        if not meta.get("tags"):
            inferred = []
            file_type = meta.get("file_type", "")
            if file_type in [".py", ".m", ".dax", ".ps1", ".sql", ".ipynb"]:
                inferred.append("code")
            if "RMS" in str(meta.get("data_sources", "")):
                inferred.append("rms_export")
            meta["tags"] = inferred
        updated_metadatas.append(meta)

    if ids:
        collection.update(ids=ids, metadatas=updated_metadatas)
    print("Updated:", len(ids))


if __name__ == "__main__":
    main()

