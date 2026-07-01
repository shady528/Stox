from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

from app.config import DEFAULT_LLM_PROVIDER, OLLAMA_MODEL
from app.services.memory import memory
from app.services.llm_provider import create_llm
from app.services.vector_store import get_vector_store
from app.logger import get_logger

logger = get_logger("stockbot.rag")

_reranker = None


def _get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        logger.info("Loading re-ranker: cross-encoder/ms-marco-MiniLM-L-6-v2")
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        logger.info("Re-ranker loaded")
    return _reranker


def rerank_docs(query: str, docs: list, top_n: int = 2) -> list:
    reranker = _get_reranker()
    pairs = [(query, doc.page_content) for doc in docs]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
    logger.info(f"Re-ranked {len(docs)} docs → kept top {top_n}")
    return [doc for _, doc in ranked[:top_n]]

PROMPT_TEMPLATE = """
Answer the question as detailed as possible from the provided context, make sure to provide all the details. If the answer is not available in the provided context just try to answer without context but keeping chat_history in mind. Try add two Logical follow up questions in next line that can be asked by the user at the end of generated answer with the heading "Want to know more?, ask these follow up questions :"

Current conversation:
{chat_history}
Context:
{context}
Question:
{human_input}

Answer:
"""


def _get_default_llm():
    if DEFAULT_LLM_PROVIDER == "ollama":
        logger.info(f"Using default LLM: Ollama/{OLLAMA_MODEL}")
        return create_llm("ollama", OLLAMA_MODEL)
    else:
        from langchain_google_genai import ChatGoogleGenerativeAI
        logger.info("Using default LLM: Gemini 2.5 Flash")
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)


def get_conversational_chain(llm=None):
    if llm is None:
        llm = _get_default_llm()
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["chat_history", "context", "human_input"],
    )
    return load_qa_chain(llm, chain_type="stuff", memory=memory, prompt=prompt)


def get_answer(user_question: str, provider: str = None, model_name: str = None, api_key: str = None) -> str:
    logger.info(f"Searching vector store for: \"{user_question[:60]}\"")
    vstore = get_vector_store()
    candidate_docs = vstore.similarity_search(user_question, k=5)
    logger.info(f"Retrieved {len(candidate_docs)} candidate documents")
    relevant_docs = rerank_docs(user_question, candidate_docs, top_n=2)

    llm = None
    if provider and model_name:
        logger.info(f"Using custom LLM: {provider}/{model_name}")
        llm = create_llm(provider, model_name, api_key)

    chain = get_conversational_chain(llm=llm)
    response = chain(
        {"input_documents": relevant_docs, "human_input": user_question},
        return_only_outputs=True,
    )
    logger.info("Answer generated successfully")
    return response["output_text"]
