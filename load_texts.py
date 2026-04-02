from pathlib import Path
from langchain.document_loaders import TextLoader as LCTextLoader
from langchain_community.document_loaders import TextLoader as LCCommunityTextLoader

def load_and_show(path: str, loader_cls=LCCommunityTextLoader, encoding: str = "utf-8"):
    p = Path(path)
    if not p.exists():
        print(f"File not found: {p}")
        return []
    loader = loader_cls(str(p), encoding=encoding)
    docs = loader.load()
    print(f"Loaded {len(docs)} documents from {p}")
    print("-" * 46)
    if docs:
        print(f"content preview: {docs[0].page_content[:500]}........")
        print(f"Metadata: {docs[0].metadata}")
    return docs

if __name__ == "__main__":
    load_and_show("data2/text_files/rags_intro.txt")
    load_and_show("data2/text_files/Langchain_intro.txt")