import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_API_ENDPOINT
from app.services.rag import get_embeddings, get_vector_store


def load_pdfs(folder_path: str):
    loader = PyPDFDirectoryLoader(folder_path)
    return loader.load()


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    return splitter.split_documents(documents)


def ingest(pdf_folder: str):
    print(f"Loading PDFs from {pdf_folder}...")
    docs = load_pdfs(pdf_folder)
    print(f"Loaded {len(docs)} pages")

    chunks = chunk_documents(docs)
    print(f"Split into {len(chunks)} chunks")

    print("Uploading to AstraDB...")
    vstore = get_vector_store()
    vstore.add_documents(chunks)
    print("Done!")


if __name__ == "__main__":
    pdf_folder = os.path.join(os.path.dirname(__file__), "..", "data", "pdfs")
    ingest(pdf_folder)
