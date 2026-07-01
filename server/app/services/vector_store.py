from app.logger import get_logger

logger = get_logger("stockbot.vectorstore")

_vstore = None


def get_vector_store():
    global _vstore
    if _vstore is None:
        from app.config import VECTOR_STORE
        if VECTOR_STORE == "chroma":
            _vstore = _get_chroma()
        else:
            _vstore = _get_pinecone()
    return _vstore


def _get_pinecone():
    from pinecone import Pinecone
    from langchain_pinecone import PineconeVectorStore
    from app.config import PINECONE_API_KEY, PINECONE_INDEX_NAME
    from app.services.embedding_provider import get_embeddings

    logger.info(f"Connecting to Pinecone index: {PINECONE_INDEX_NAME}")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    vstore = PineconeVectorStore(index=index, embedding=get_embeddings())
    logger.info("Pinecone vector store connected")
    return vstore


def _get_chroma():
    from langchain_chroma import Chroma
    from app.config import CHROMA_PERSIST_DIR
    from app.services.embedding_provider import get_embeddings

    logger.info(f"Loading Chroma vector store from {CHROMA_PERSIST_DIR}")
    vstore = Chroma(
        collection_name="stockbot",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_PERSIST_DIR,
    )
    logger.info("Chroma vector store loaded")
    return vstore
