import argparse

from kb_ask_ollama import ask_kb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", required=True)
    parser.add_argument("-n", "--n_results", type=int, default=6)
    parser.add_argument("--file_type")
    parser.add_argument("--department")
    parser.add_argument("--tags", help="comma list")
    parser.add_argument("--model", default="llama3.1:8b")
    args = parser.parse_args()

    tags = [tag.strip() for tag in args.tags.split(",")] if args.tags else None

    response = ask_kb(
        args.query,
        n_results=args.n_results,
        file_type=args.file_type,
        department=args.department,
        tags=tags,
        model=args.model,
    )

    print(response["answer"])
    print("\nSources:")
    for index, hit in enumerate(response["hits"], 1):
        metadata = hit.get("metadata", {}) or {}
        file_name = metadata.get("file_name")
        chunk_index = metadata.get("chunk_index")
        print(f"[{index}] {file_name}#chunk{chunk_index}")


if __name__ == "__main__":
    main()

