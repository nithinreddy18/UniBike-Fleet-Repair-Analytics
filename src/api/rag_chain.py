import time
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from src.core.config import settings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from src.nlp.vector_store import get_vector_store
from src.core.logger import logger

_chain = None
_active_model = None


def get_candidate_models() -> list[str]:
    """Returns candidate Groq models in priority order for automatic fallback."""
    configured = getattr(settings, "groq_model", "") or "qwen/qwen3.8-27b"
    fallbacks = [
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]
    candidates = [configured] + [m for m in fallbacks if m != configured]
    return candidates


def _build_rag_chain_with_model(model_name: str):
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})

    llm = ChatGroq(
        temperature=0,
        model_name=model_name,
        api_key=settings.groq_api_key,
    )

    template = """You are a knowledgeable and helpful AI repair assistant for the UniBike fleet.

Context from UniBike manuals:
{context}

User Question: {input}

Instructions:
1. If the provided context contains relevant instructions (such as adjusting derailleurs, fixing dropped chains, fixing a flat tire, or adjusting brake pads), provide clear, step-by-step guidance based on the context.
2. If the user asks a general or vague question (e.g., "how to fix a repair in my cycle", "my bike is broken", "hello"), provide a friendly response explaining common bicycle repairs and ask them which specific component they need help with (e.g., flat tire, brakes, chain, derailleurs).
3. If the user asks a specific bicycle question not found in the manuals, provide helpful standard bicycle repair advice using your general knowledge, and suggest submitting a repair ticket in the UniBike portal if professional help is needed.

Answer:"""

    prompt = PromptTemplate.from_template(template)
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, combine_docs_chain)


def get_rag_chain(force_model: str = None):
    global _chain, _active_model
    if _chain is not None and force_model is None:
        return _chain

    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY is missing! The chatbot will fail to answer.")
        return None

    model_to_use = (
        force_model or getattr(settings, "groq_model", "") or "qwen/qwen3.8-27b"
    )
    logger.info(f"Initializing generative RAG chain with model '{model_to_use}'...")
    try:
        _chain = _build_rag_chain_with_model(model_to_use)
        _active_model = model_to_use
        return _chain
    except Exception as e:
        logger.error(f"Failed to build RAG chain with model '{model_to_use}': {e}")
        return None


def query_assistant(question: str) -> tuple[str, list]:
    global _chain, _active_model
    if not settings.groq_api_key:
        return (
            "I am currently offline. Please configure the GROQ_API_KEY environment variable on the server.",
            [],
        )

    start_time = time.time()
    candidates = get_candidate_models()

    chain = get_rag_chain()
    if chain is None and _active_model is None:
        # Try initializing with fallback models
        for m in candidates:
            chain = get_rag_chain(force_model=m)
            if chain is not None:
                break

    if chain is None:
        return (
            "Unable to initialize RAG chain. Please verify server configuration and GROQ_API_KEY.",
            [],
        )

    answer = None
    docs = []
    last_error = None

    models_to_try = [_active_model] if _active_model in candidates else []
    for c in candidates:
        if c not in models_to_try:
            models_to_try.append(c)

    for model_name in models_to_try:
        try:
            if _active_model != model_name:
                logger.info(f"Switching RAG model to fallback: {model_name}")
                chain = get_rag_chain(force_model=model_name)

            response = chain.invoke({"input": question})
            answer = response.get("answer", "I could not find an answer.")
            docs = response.get("context", [])
            break  # Success!
        except Exception as e:
            last_error = e
            logger.warning(f"RAG Chain attempt with model '{model_name}' failed: {e}")
            _chain = None

    if answer is None:
        logger.error(f"All RAG Chain candidate models failed. Last error: {last_error}")
        answer = (
            f"Sorry, I encountered an error while processing your request: {last_error}"
        )
        docs = []

    elapsed = time.time() - start_time
    logger.info(f"Generative RAG query executed in {elapsed:.2f} seconds.")
    return answer, docs
