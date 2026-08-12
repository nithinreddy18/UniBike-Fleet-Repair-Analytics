import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.core.config import settings
from src.core.logger import logger
from src.nlp.loader import load_manuals
from src.nlp.splitter import split_documents


def get_vector_store() -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # If the collection already exists and has documents, return it
    if os.path.exists(settings.chroma_db_dir):
        vector_store = Chroma(
            persist_directory=settings.chroma_db_dir,
            embedding_function=embeddings,
            collection_name="unibike_manuals",
        )
        # ChromaDB API change: `_collection.count()` gets the number of docs.
        if vector_store._collection.count() > 0:
            logger.info("Loaded existing ChromaDB vector store.")
            return vector_store

    logger.info("Initializing new ChromaDB vector store...")
    documents = load_manuals()
    if not documents:
        logger.warning("No documents loaded. Vector store will be empty.")
        return Chroma(
            persist_directory=settings.chroma_db_dir,
            embedding_function=embeddings,
            collection_name="unibike_manuals",
        )

    chunks = split_documents(documents)
    logger.info(f"Split documents into {len(chunks)} chunks. Ingesting to ChromaDB...")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.chroma_db_dir,
        collection_name="unibike_manuals",
    )
    logger.info("Ingestion complete.")

    return vector_store
