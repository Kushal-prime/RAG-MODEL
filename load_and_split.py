from pathlib import Path
from typing import List

from langchain.document_loaders import TextLoader as LCTextLoader
from langchain_community.document_loaders import TextLoader as CommunityTextLoader, DirectoryLoader
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
)

def load_file(path: str, loader_cls=CommunityTextLoader, encoding: str = "utf-8"):
    p = Path(path)
    if not p.exists():
        print(f"File not found: {p}")
        return []
    loader = loader_cls(str(p), encoding=encoding)
    docs = loader.load()
    print(f"Loaded {len(docs)} documents from {p}")
    if docs:
        print(f"  Preview: {docs[0].page_content[:200]}...")
        print(f"  Metadata: {docs[0].metadata}")
    return docs

def load_directory(dir_path: str, glob: str = "*.txt", loader_cls=CommunityTextLoader, encoding: str = "utf-8"):
    p = Path(dir_path)
    if not p.exists():
        print(f"Directory not found: {p}")
        return []
    dir_loader = DirectoryLoader(
        str(p),
        glob=glob,
        loader_cls=loader_cls,
        loader_kwargs={"encoding": encoding},
        show_progress=True,
    )
    docs = dir_loader.load()
    print(f"📁 Loaded {len(docs)} documents from {p}")
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("source", "unknown")
        print(f"  {i}. {src} ({len(d.page_content)} chars)")
    return docs

def split_and_report(text: str, prefix: str = ""):
    if not text:
        print(f"{prefix} No text to split.")
        return

    # Character splitter
    char_splitter = CharacterTextSplitter(separator="\n", chunk_size=200, chunk_overlap=20, length_function=len)
    char_chunks = char_splitter.split_text(text)
    print(f"{prefix} CHARACTER splitter -> {len(char_chunks)} chunks; first: {char_chunks[0][:100]}...")

    # Recursive character splitter
    recursive_splitter = RecursiveCharacterTextSplitter(separators=["\n", " ", ""], chunk_size=200, chunk_overlap=20, length_function=len)
    recursive_chunks = recursive_splitter.split_text(text)
    print(f"{prefix} RECURSIVE splitter -> {len(recursive_chunks)} chunks; first: {recursive_chunks[0][:100]}...")

    # Token splitter
    token_splitter = TokenTextSplitter(chunk_size=50, chunk_overlap=10)
    token_chunks = token_splitter.split_text(text)
    print(f"{prefix} TOKEN splitter -> {len(token_chunks)} chunks; first: {token_chunks[0][:100]}...")

def main():
    base = Path("data2/text_files")
    # load single files
    load_file(base / "rags_intro.txt")
    load_file(base / "Langchain_intro.txt")

    # load directory (recursive if you want use "**/*.txt")
    docs = load_directory(base, glob="*.txt")

    # split the first document text (example)
    if docs:
        text = docs[0].page_content
        split_and_report(text, prefix="Doc 1:")

if __name__ == "__main__":
    main()