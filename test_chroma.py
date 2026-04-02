try:
    import chromadb
    print("chromadb version:", chromadb.__version__)
    import sqlite3
    print("sqlite3 version:", sqlite3.sqlite_version)
    from langchain_community.vectorstores import Chroma
    print("Chroma imported successfully")
except Exception as e:
    import traceback
    traceback.print_exc()
