import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from src.core.config import settings
from src.core.logger import logger


def load_manuals() -> List[Document]:
    documents = []
    data_dir = settings.data_dir

    if not os.path.exists(data_dir):
        logger.warning(f"Data directory {data_dir} does not exist.")
        return documents

    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            filepath = os.path.join(data_dir, filename)
            try:
                loader = PyPDFLoader(filepath)
                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} pages from {filename}")
            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to load {filename}: {e}")

    return documents
