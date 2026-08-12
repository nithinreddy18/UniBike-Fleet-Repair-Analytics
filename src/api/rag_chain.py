import time
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from src.core.config import settings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from src.nlp.vector_store import get_vector_store
from src.core.logger import logger

_chain = None


def get_rag_chain():
    global _chain
    if _chain is not None:
        return _chain

    logger.info("Initializing generative RAG chain...")
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})

    # If API key is missing, this will fail. Instructing the user to set it.
    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY is missing! The chatbot will fail to answer.")
        return None

    llm = ChatGroq(
        temperature=0,
        model_name="llama-3.1-8b-instant",  # Groq's stable Llama 3.1 8B model
        api_key=settings.groq_api_key,
    )

    template = """You are a helpful AI repair assistant for the UniBike fleet. 
First, try to answer the user's question using the provided context. 
If the answer is NOT in the context, evaluate the question carefully:
1. If it is a basic, general, or common-knowledge question (e.g., "how to use a bicycle", "what is a bike", "hi"), answer it normally and helpfully using your own internal knowledge.
2. If it is a highly specific, technical, or repair-specific question, and the context does not contain the answer, reply EXACTLY with: 'I cannot find this in the documents.'

Context:
{context}

Question: {input}
Answer:"""

    prompt = PromptTemplate.from_template(template)
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    _chain = create_retrieval_chain(retriever, combine_docs_chain)
    return _chain


def query_assistant(question: str) -> tuple[str, list]:
    if not settings.groq_api_key:
        return "I am currently offline. Please configure the GROQ_API_KEY on the server.", []
        
    chain = get_rag_chain()
    start_time = time.time()

    try:
        response = chain.invoke({"input": question})
        answer = response.get("answer", "I could not find an answer.")
        docs = response.get("context", [])
    except Exception as e:  # noqa: BLE001
        logger.error(f"RAG Chain error: {e}")
        answer = "Sorry, I encountered an error while processing your request."
        docs = []

    elapsed = time.time() - start_time
    logger.info(f"Generative RAG query executed in {elapsed:.2f} seconds.")

    return answer, docs
