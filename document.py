from langchain.schema import Document

doc = Document(
    page_content="Kushal, Manjusha, Chinmai, Rudresh are in this class",
    metadata={  # was `meta_data` — correct argument name is `metadata`
        "source": "sam.txt",
        "author": "Samyak Dande",
        "date_created": "2025"
    }
)
print("Document created")

print(
    "Filtering search results,\nTracking document source,\nProvides context,\nDebugging and auditing"
)

print(type(doc))