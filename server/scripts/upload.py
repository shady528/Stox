import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import VECTOR_STORE, EMBEDDING_PROVIDER
from app.services.embedding_provider import get_embeddings


def load_pdfs(folder_path: str):
    loader = PyPDFDirectoryLoader(folder_path)
    return loader.load()


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    return splitter.split_documents(documents)


def ingest_pinecone(chunks, embeddings):
    from pinecone import Pinecone, ServerlessSpec
    from langchain_pinecone import PineconeVectorStore
    from app.config import PINECONE_API_KEY, PINECONE_INDEX_NAME

    # Dimension depends on embedding provider
    dim = 3072 if EMBEDDING_PROVIDER == "google" else 768

    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing:
        print(f"Creating Pinecone index '{PINECONE_INDEX_NAME}' (dim={dim})")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=dim,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print("Index created")
    else:
        print(f"Index '{PINECONE_INDEX_NAME}' already exists")

    print("Uploading to Pinecone...")
    PineconeVectorStore.from_documents(
        chunks,
        embedding=embeddings,
        index_name=PINECONE_INDEX_NAME,
    )
    print("Done!")


def ingest_chroma(chunks, embeddings):
    from langchain_chroma import Chroma
    from app.config import CHROMA_PERSIST_DIR

    print(f"Writing to Chroma at {CHROMA_PERSIST_DIR}...")
    Chroma.from_documents(
        chunks,
        embedding=embeddings,
        collection_name="stockbot",
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print("Done!")


def ingest(pdf_folder: str):
    print(f"Loading PDFs from {pdf_folder}...")
    docs = load_pdfs(pdf_folder)
    print(f"Loaded {len(docs)} pages")

    chunks = chunk_documents(docs)
    print(f"Split into {len(chunks)} chunks")

    embeddings = get_embeddings()

    if VECTOR_STORE == "chroma":
        ingest_chroma(chunks, embeddings)
    else:
        ingest_pinecone(chunks, embeddings)


if __name__ == "__main__":
    pdf_folder = os.path.join(os.path.dirname(__file__), "..", "data", "pdfs")
    print(f"Mode: VECTOR_STORE={VECTOR_STORE} | EMBEDDING_PROVIDER={EMBEDDING_PROVIDER}")
    ingest(pdf_folder)
